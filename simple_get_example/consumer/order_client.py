import os

import requests

from .order import Order


HOSTNAME = "127.0.0.1"


def fetch_orders(base_url: str | None = None) -> list[Order]:
    if base_url is None:
        api_port = os.environ["API_PORT"]
        base_url = f"http://{HOSTNAME}:{api_port}"

    url = f"{base_url}/orders"

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        body = response.json()
    except requests.RequestException as err:
        print(err)
        error_body = err.response.text if err.response is not None else None
        raise RuntimeError(f"Error from response: {error_body}") from err

    return [Order.from_dict(order) for order in body]
