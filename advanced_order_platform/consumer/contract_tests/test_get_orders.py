import pytest
from pact import Pact, match

from ..order import ApiError, OrderApiError
from ..order_client import OrderClient
from .conftest import (
    MISSING_ORDER_ID,
    OPEN_ORDER_ID,
    VALID_TOKEN,
    authenticated_interaction,
    error_body,
    order_body,
)


def test_can_list_open_orders_with_query_contract(pact: Pact) -> None:
    (
        authenticated_interaction(pact, "a request to list open orders")
        .given("open orders exist")
        .with_request("GET", "/orders")
        .with_query_parameter("status", "open")
        .with_query_parameter("page_size", "25")
        .will_respond_with(200)
        .with_header("Content-Type", "application/json; charset=utf-8", part="Response")
        .with_body(
            {"orders": match.each_like(order_body(), min=1)},
            content_type="application/json",
        )
    )

    with pact.serve() as mock_server:
        orders = OrderClient(VALID_TOKEN, str(mock_server.url)).list_orders("open")

    assert orders[0].id == OPEN_ORDER_ID
    assert orders[0].status == "open"
    assert orders[0].totals.currency == "USD"


def test_can_fetch_one_order_by_id(pact: Pact) -> None:
    (
        authenticated_interaction(pact, "a request to fetch an existing order")
        .given("order exists", {"order_id": OPEN_ORDER_ID})
        .with_request("GET", f"/orders/{OPEN_ORDER_ID}")
        .will_respond_with(200)
        .with_header("Content-Type", "application/json; charset=utf-8", part="Response")
        .with_body(order_body(), content_type="application/json")
    )

    with pact.serve() as mock_server:
        order = OrderClient(VALID_TOKEN, str(mock_server.url)).get_order(OPEN_ORDER_ID)

    assert order.id == OPEN_ORDER_ID


def test_raises_domain_error_when_order_is_missing(pact: Pact) -> None:
    (
        authenticated_interaction(pact, "a request to fetch a missing order")
        .given("order does not exist", {"order_id": MISSING_ORDER_ID})
        .with_request("GET", f"/orders/{MISSING_ORDER_ID}")
        .will_respond_with(404)
        .with_header("Content-Type", "application/json; charset=utf-8", part="Response")
        .with_body(
            error_body("ORDER_NOT_FOUND", f"Order {MISSING_ORDER_ID} was not found."),
            content_type="application/json",
        )
    )

    with pact.serve() as mock_server:
        with pytest.raises(OrderApiError) as exc_info:
            OrderClient(VALID_TOKEN, str(mock_server.url)).get_order(MISSING_ORDER_ID)

    api_error: ApiError = exc_info.value.api_error
    assert exc_info.value.status_code == 404
    assert api_error.code == "ORDER_NOT_FOUND"
