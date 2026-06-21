"""Provider application used by the advanced Pact example."""

from copy import deepcopy
from typing import Any
from uuid import uuid4

from flask import Flask, jsonify, request

from .data.orders import MISSING_ORDER_ID, OPEN_ORDER_ID, ORDER_FIXTURES


DATA_STORE: dict[str, dict[str, Any]] = deepcopy(ORDER_FIXTURES)
DEFAULT_AUTH_TOKENS: dict[str, dict[str, Any]] = {
    "test-token": {
        "active": True,
        "scopes": {"orders:read", "orders:write"},
    }
}
AUTH_TOKENS: dict[str, dict[str, Any]] = deepcopy(DEFAULT_AUTH_TOKENS)


def reset_data_store() -> None:
    DATA_STORE.clear()
    DATA_STORE.update(deepcopy(ORDER_FIXTURES))


def reset_auth_policy() -> None:
    AUTH_TOKENS.clear()
    AUTH_TOKENS.update(deepcopy(DEFAULT_AUTH_TOKENS))


def register_access_token(
    token: str,
    *,
    active: bool = True,
    scopes: set[str] | None = None,
) -> None:
    AUTH_TOKENS[token] = {
        "active": active,
        "scopes": scopes or set(),
    }


def ensure_order_exists(order_id: str = OPEN_ORDER_ID) -> None:
    if order_id not in DATA_STORE:
        DATA_STORE[order_id] = deepcopy(ORDER_FIXTURES[OPEN_ORDER_ID])
        DATA_STORE[order_id]["id"] = order_id


def ensure_order_missing(order_id: str = MISSING_ORDER_ID) -> None:
    DATA_STORE.pop(order_id, None)


def create_app() -> Flask:
    app = Flask(__name__)

    @app.after_request
    def set_json_content_type(response):
        response.headers["Content-Type"] = "application/json; charset=utf-8"
        return response

    @app.before_request
    def require_auth():
        if request.path == "/health":
            return None

        correlation_id = request.headers.get("X-Request-Id", "unknown")
        auth_header = request.headers.get("Authorization")
        if auth_header is None:
            return (
                jsonify(
                    {
                        "code": "UNAUTHORIZED",
                        "message": "Missing bearer token.",
                        "correlation_id": correlation_id,
                    }
                ),
                401,
            )

        prefix = "Bearer "
        if not auth_header.startswith(prefix):
            return (
                jsonify(
                    {
                        "code": "UNAUTHORIZED",
                        "message": "Invalid authorization scheme.",
                        "correlation_id": correlation_id,
                    }
                ),
                401,
            )

        token_policy = AUTH_TOKENS.get(auth_header.removeprefix(prefix))
        if token_policy is None:
            return (
                jsonify(
                    {
                        "code": "UNAUTHORIZED",
                        "message": "Invalid bearer token.",
                        "correlation_id": correlation_id,
                    }
                ),
                401,
            )

        if not token_policy["active"]:
            return (
                jsonify(
                    {
                        "code": "EXPIRED_TOKEN",
                        "message": "Bearer token has expired.",
                        "correlation_id": correlation_id,
                    }
                ),
                401,
            )

        required_scope = "orders:write" if request.method == "POST" else "orders:read"
        if required_scope not in token_policy["scopes"]:
            return (
                jsonify(
                    {
                        "code": "INSUFFICIENT_SCOPE",
                        "message": f"Bearer token requires {required_scope}.",
                        "correlation_id": correlation_id,
                    }
                ),
                403,
            )

        return None

    @app.get("/health")
    def health():
        return jsonify({"status": "ok"})

    @app.get("/orders")
    def list_orders():
        status = request.args.get("status")
        page_size = int(request.args.get("page_size", "25"))
        orders = [
            order
            for order in DATA_STORE.values()
            if status is None or order["status"] == status
        ]
        return jsonify({"orders": orders[:page_size]})

    @app.get("/orders/<order_id>")
    def get_order(order_id: str):
        order = DATA_STORE.get(order_id)
        if order is None:
            return (
                jsonify(
                    {
                        "code": "ORDER_NOT_FOUND",
                        "message": f"Order {order_id} was not found.",
                        "correlation_id": request.headers.get("X-Request-Id", "unknown"),
                    }
                ),
                404,
            )
        return jsonify(order)

    @app.post("/orders")
    def create_order():
        payload = request.get_json(force=True)
        order_id = str(uuid4())
        first_item = payload["items"][0]
        unit_price_cents = 1299
        subtotal_cents = first_item["quantity"] * unit_price_cents
        discount_cents = 200 if payload.get("coupon_code") else 0
        order = {
            "id": order_id,
            "status": "open",
            "customer": {
                "id": payload["customer_id"],
                "tier": "gold",
            },
            "items": [
                {
                    "product_id": first_item["product_id"],
                    "name": "burger",
                    "quantity": first_item["quantity"],
                    "unit_price_cents": unit_price_cents,
                }
            ],
            "totals": {
                "subtotal_cents": subtotal_cents,
                "discount_cents": discount_cents,
                "grand_total_cents": subtotal_cents - discount_cents,
                "currency": "USD",
            },
            "created_at": "2026-06-01T10:15:30Z",
            "updated_at": "2026-06-01T10:16:00Z",
        }
        DATA_STORE[order_id] = order
        response = jsonify(order)
        response.status_code = 201
        response.headers["Location"] = f"/orders/{order_id}"
        return response

    return app
