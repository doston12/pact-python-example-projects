from pathlib import Path
from typing import Any, Generator

import pytest
from pact import Pact, match

from ...pact_config import CONSUMER_NAME, PACT_DIR, PROVIDER_NAME


OPEN_ORDER_ID = "11111111-1111-4111-8111-111111111111"
MISSING_ORDER_ID = "99999999-9999-4999-8999-999999999999"
TIMESTAMP_PATTERN = r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z"
REQUEST_ID_PATTERN = r"req-[0-9]+"
VALID_TOKEN = "test-token"
EXPIRED_TOKEN = "expired-token"
WRITE_ONLY_TOKEN = "write-only-token"


@pytest.fixture
def pact() -> Generator[Pact, None, None]:
    pact = Pact(CONSUMER_NAME, PROVIDER_NAME).with_specification("V4")
    yield pact
    pact.write_file(Path(PACT_DIR))


def order_body(order_id: str = OPEN_ORDER_ID) -> dict[str, Any]:
    return {
        "id": match.uuid(order_id),
        "status": match.regex("open", regex="open|paid|shipped|cancelled"),
        "customer": {
            "id": match.regex("cust-123", regex=r"cust-[0-9]+"),
            "tier": match.regex("gold", regex="standard|gold|enterprise"),
        },
        "items": match.each_like(
            {
                "product_id": match.regex("burger-001", regex=r"[a-z]+-[0-9]{3}"),
                "name": match.str("burger"),
                "quantity": match.int(2),
                "unit_price_cents": match.int(1299),
            },
            min=1,
        ),
        "totals": {
            "subtotal_cents": match.int(2598),
            "discount_cents": match.int(200),
            "grand_total_cents": match.int(2398),
            "currency": match.regex("USD", regex="[A-Z]{3}"),
        },
        "created_at": match.regex("2026-06-01T10:15:30Z", regex=TIMESTAMP_PATTERN),
        "updated_at": match.regex("2026-06-01T10:16:00Z", regex=TIMESTAMP_PATTERN),
    }


def error_body(code: str, message: str) -> dict[str, Any]:
    return {
        "code": match.regex(code, regex=r"[A-Z_]+"),
        "message": match.str(message),
        "correlation_id": match.regex("req-123456", regex=REQUEST_ID_PATTERN),
    }


def authenticated_interaction(pact: Pact, description: str, token: str = VALID_TOKEN):
    return (
        pact.upon_receiving(description)
        .with_header("Authorization", f"Bearer {token}", part="Request")
        .with_header("Accept", "application/json", part="Request")
        .with_header("X-Request-Id", match.regex("req-123456", regex=REQUEST_ID_PATTERN), part="Request")
    )


def unauthenticated_interaction(pact: Pact, description: str):
    return (
        pact.upon_receiving(description)
        .with_header("Accept", "application/json", part="Request")
        .with_header("X-Request-Id", match.regex("req-123456", regex=REQUEST_ID_PATTERN), part="Request")
    )
