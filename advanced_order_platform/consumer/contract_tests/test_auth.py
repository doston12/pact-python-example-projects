import pytest
from pact import Pact

from ..order import ApiError, OrderApiError
from ..order_client import OrderClient
from .conftest import (
    EXPIRED_TOKEN,
    OPEN_ORDER_ID,
    WRITE_ONLY_TOKEN,
    authenticated_interaction,
    error_body,
    unauthenticated_interaction,
)


def test_raises_domain_error_when_token_is_missing(pact: Pact) -> None:
    (
        unauthenticated_interaction(pact, "a request to list orders without a token")
        .given("no access token is provided")
        .with_request("GET", "/orders")
        .with_query_parameter("status", "open")
        .with_query_parameter("page_size", "25")
        .will_respond_with(401)
        .with_header("Content-Type", "application/json; charset=utf-8", part="Response")
        .with_body(
            error_body("UNAUTHORIZED", "Missing bearer token."),
            content_type="application/json",
        )
    )

    with pact.serve() as mock_server:
        with pytest.raises(OrderApiError) as exc_info:
            OrderClient(None, str(mock_server.url)).list_orders("open")

    api_error: ApiError = exc_info.value.api_error
    assert exc_info.value.status_code == 401
    assert api_error.code == "UNAUTHORIZED"


def test_raises_domain_error_when_token_is_expired(pact: Pact) -> None:
    (
        authenticated_interaction(
            pact,
            "a request to fetch an order with an expired token",
            EXPIRED_TOKEN,
        )
        .given("the access token is expired", {"token": EXPIRED_TOKEN})
        .with_request("GET", f"/orders/{OPEN_ORDER_ID}")
        .will_respond_with(401)
        .with_header("Content-Type", "application/json; charset=utf-8", part="Response")
        .with_body(
            error_body("EXPIRED_TOKEN", "Bearer token has expired."),
            content_type="application/json",
        )
    )

    with pact.serve() as mock_server:
        with pytest.raises(OrderApiError) as exc_info:
            OrderClient(EXPIRED_TOKEN, str(mock_server.url)).get_order(OPEN_ORDER_ID)

    api_error: ApiError = exc_info.value.api_error
    assert exc_info.value.status_code == 401
    assert api_error.code == "EXPIRED_TOKEN"


def test_raises_domain_error_when_token_has_insufficient_scope(pact: Pact) -> None:
    (
        authenticated_interaction(
            pact,
            "a request to list orders with a write-only token",
            WRITE_ONLY_TOKEN,
        )
        .given("the access token cannot read orders", {"token": WRITE_ONLY_TOKEN})
        .with_request("GET", "/orders")
        .with_query_parameter("status", "open")
        .with_query_parameter("page_size", "25")
        .will_respond_with(403)
        .with_header("Content-Type", "application/json; charset=utf-8", part="Response")
        .with_body(
            error_body("INSUFFICIENT_SCOPE", "Bearer token requires orders:read."),
            content_type="application/json",
        )
    )

    with pact.serve() as mock_server:
        with pytest.raises(OrderApiError) as exc_info:
            OrderClient(WRITE_ONLY_TOKEN, str(mock_server.url)).list_orders("open")

    api_error: ApiError = exc_info.value.api_error
    assert exc_info.value.status_code == 403
    assert api_error.code == "INSUFFICIENT_SCOPE"
