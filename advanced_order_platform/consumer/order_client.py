import os
from typing import Any

import requests

from .order import ApiError, NewOrder, Order, OrderApiError


HOSTNAME = "127.0.0.1"


class OrderClient:
    def __init__(self, token: str | None, base_url: str | None = None) -> None:
        if base_url is None:
            api_port = os.environ["API_PORT"]
            base_url = f"http://{HOSTNAME}:{api_port}"
        self.base_url = base_url.rstrip("/")
        self.token = token

    def list_orders(self, status: str, page_size: int = 25) -> list[Order]:
        response = requests.get(
            f"{self.base_url}/orders",
            params={"status": status, "page_size": page_size},
            headers=self._headers(),
            timeout=10,
        )
        body = self._json_or_raise(response)
        return [Order.from_dict(order) for order in body["orders"]]

    def get_order(self, order_id: str) -> Order:
        response = requests.get(
            f"{self.base_url}/orders/{order_id}",
            headers=self._headers(),
            timeout=10,
        )
        body = self._json_or_raise(response)
        return Order.from_dict(body)

    def create_order(self, new_order: NewOrder, idempotency_key: str) -> Order:
        response = requests.post(
            f"{self.base_url}/orders",
            json=new_order.to_dict(),
            headers={
                **self._headers(),
                "Idempotency-Key": idempotency_key,
            },
            timeout=10,
        )
        body = self._json_or_raise(response)
        return Order.from_dict(body)

    def _headers(self) -> dict[str, str]:
        headers = {
            "Accept": "application/json",
            "X-Request-Id": "req-123456",
        }
        if self.token is not None:
            headers["Authorization"] = f"Bearer {self.token}"
        return headers

    def _json_or_raise(self, response: requests.Response) -> Any:
        body = response.json()
        if response.status_code >= 400:
            raise OrderApiError(response.status_code, ApiError.from_dict(body))
        response.raise_for_status()
        return body
