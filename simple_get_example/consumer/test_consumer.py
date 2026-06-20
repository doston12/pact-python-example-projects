"""
    Brief: This module contains the consumer tests for the order service using Pact. The flow is:

    -  fixture creates Pact contract builder
    - test adds expected request/response
    - pact.serve() starts mock server
    - client calls mock_server.url
    - after test, fixture writes pact (contract) file
"""

from pathlib import Path
from typing import Generator

import pytest
from pact import Pact, match

from .order import Order, OrderItem
from .order_client import fetch_orders
from ..pact_config import CONSUMER_NAME, PACT_DIR, PROVIDER_NAME


ITEM_PROPERTIES = {
    "name": "burger",
    "quantity": 2,
    "value": 100,
}

ORDER_PROPERTIES = {
    "id": 1,
    "items": [ITEM_PROPERTIES],
}


@pytest.fixture
def pact() -> Generator[Pact, None, None]:
    # To create pact object we must provide consumer and provider names,
    # and it is good to specify the pact specification version -- the latest spec version is V4
    # more about pact specification versions: https://docs.pact.io/getting_started/specification
    pact = Pact(CONSUMER_NAME, PROVIDER_NAME).with_specification("V4")
    yield pact
    # write the pact (contract) file, later the provider will use it to verify the contract
    pact.write_file(Path(PACT_DIR))


def test_will_receive_the_list_of_current_orders(pact: Pact) -> None:
    """
    Test that the consumer will receive the list of current orders from the provider.

    Steps:
    1. Define the response-object -- this is what consumer expects from provider API.
    2. Define the expected HTTP communication between consumer and provider.
    3. Generate pact contracr file

    """

    # this block of code defines the expected response body from the provider API. It says:
    # The response body should be a list. Each item in the list should be an order.
    # Each order has: id: integer and items: list
    # Each item has: name: string, quantity: integer, value: integer
    # So this block only describes the JSON body -- which consumer expects from provider API.
    expected_response = match.each_like(
        {
            "id": match.int(ORDER_PROPERTIES["id"]),
            "items": match.each_like(
                {
                    "name": match.str(ITEM_PROPERTIES["name"]),
                    "quantity": match.int(ITEM_PROPERTIES["quantity"]),
                    "value": match.int(ITEM_PROPERTIES["value"]),
                },
            ),
        },
    )

    # this defines the expected HTTP communication between consumer and provider. It says:
    # When consumer sends: GET /orders
    # Then provider should respond with: 200 OK, Content-Type: application/json; charset=utf-8,
    # and the expected_response body
    (
        pact.upon_receiving("a request for orders")
        .given("there are orders")
        .with_request("GET", "/orders")
        .will_respond_with(200)
        .with_header("Content-Type", "application/json; charset=utf-8")
        .with_body(expected_response, content_type="application/json")
    )

    # pact contract is defined now. It is not generated yet, we defined how the contract looks like.
    # We will generate it in the next step

    # When your application is running in production, you would call the provider API, get some data from it and
    # display it on your application. This is done via fetch_orders method -- so, it is an important method that you
    # use to get and display data from another system/application (the provider API). In next step, we make a call to
    # fetch_orders method, but instead of calling the real provider API, we will call the pact mock server.
    # This simply means: Run my real consumer code (which gets data from an external system) but use pack mock server.

    # So, fetch_orders method makes HTTP GET /orders call against the pact mock server.
    # Pact mock server receives this request AND Pact checks: Is this the GET /orders request I was told to expect?
    # We told the pact mock server to expect GET /orders request in the previous 2 steps -- where we build expected
    # response shape and expected http communication -- our pact mock server knows only about this, and nothing else.
    # if you send it 'POST /orders' request, it will return 500 error, because it was not told to expect this request.

    # When we sent GET /orders request to pact mock server it returns the response we defined in the previous step.
    # That response is fake(mock response), but it has the same shape that our consumer expects from the real
    # provider API. Once fetch_orders received the fake HTTP response from pact mock server, it tries to parse the
    # response into our consumer model: Order and OrderItem classes. So this last step proves two things:
    # 1. fetch_orders() made the HTTP request described in the Pact interaction: GET /orders
    # 2. fetch_orders() can parse the provider response shape into the objects our app uses

    # The core idea here is to confirm that the consumer code can handle the response shape that the provider is
    # expected to return. This is the essence of contract testing: ensuring that both sides of the interaction
    # (consumer and provider) agree on the request and response formats.

    with pact.serve() as mock_server:
        assert fetch_orders(str(mock_server.url)) == [
            Order(
                id=ORDER_PROPERTIES["id"],
                items=(OrderItem.from_dict(ITEM_PROPERTIES),),
            )
        ]

    # After the test finishes, the fixture writes this interaction to a pact contract file.
    # Later, the provider test will use this contract file to check that real provider can return this same shape.
