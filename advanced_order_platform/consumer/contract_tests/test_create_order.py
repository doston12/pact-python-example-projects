from pact import Pact, match

from ..order import NewOrder, NewOrderItem
from ..order_client import OrderClient
from .conftest import OPEN_ORDER_ID, VALID_TOKEN, authenticated_interaction, order_body


def test_can_create_order_with_idempotency_contract(pact: Pact) -> None:
    new_order = NewOrder(
        customer_id="cust-123",
        items=(NewOrderItem(product_id="burger-001", quantity=2),),
        coupon_code="SAVE200",
    )
    expected_request_body = {
        "customer_id": match.regex("cust-123", regex=r"cust-[0-9]+"),
        "items": match.each_like(
            {
                "product_id": match.regex("burger-001", regex=r"[a-z]+-[0-9]{3}"),
                "quantity": match.int(2),
            },
            min=1,
        ),
        "coupon_code": match.str("SAVE200"),
    }

    # define the expected pact interation
    (
        authenticated_interaction(pact, "a request to create an order")
        .given("the customer can place orders", {"customer_id": "cust-123"})
        .with_request("POST", "/orders")
        .with_header(
            "Idempotency-Key",
            match.uuid("33333333-3333-4333-8333-333333333333"),
            part="Request",
        )
        .with_body(expected_request_body, content_type="application/json", part="Request")
        .will_respond_with(201)
        .with_header("Content-Type", "application/json; charset=utf-8", part="Response")
        .with_header(
            "Location",
            match.regex(f"/orders/{OPEN_ORDER_ID}", regex=r"/orders/[0-9a-f-]{36}"),
            part="Response",
        )
        .with_body(order_body(), content_type="application/json")
    )

    with pact.serve() as mock_server:
        order = OrderClient(VALID_TOKEN, str(mock_server.url)).create_order(
            new_order,
            "33333333-3333-4333-8333-333333333333",
        )

    # these assertions needed to confirm that our consumer code is working correctly and parsing the response from
    # the provider API as expected. Without these assertions -- the test would only verify the contract, but not the
    # consumer's ability to handle the response. Generally, you don't have to write long list of assertions here
    # just enough to prove that consumer can actually use the response.
    assert order.customer.id == "cust-123"
    assert order.items[0].quantity == 2

    # assert order.status == "open" --> adding this might be OK..

    # BUT avoid something like this:
    # assert order.id == ...
    # assert order.status == ...
    # assert order.customer.id == ...
    # assert order.customer.tier == ...
    # assert order.items[0].product_id == ...
    # assert order.items[0].name == ...
    # assert order.items[0].quantity == ...
    # assert order.items[0].unit_price_cents == ...
    # assert order.totals.subtotal_cents == ...
    # assert order.totals.discount_cents == ...
    # assert order.totals.grand_total_cents == ...
    # assert order.totals.currency == ...
    # assert order.created_at == ...
    # assert order.updated_at == ...

