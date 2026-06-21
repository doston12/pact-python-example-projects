OPEN_ORDER_ID = "11111111-1111-4111-8111-111111111111"
SHIPPED_ORDER_ID = "22222222-2222-4222-8222-222222222222"
MISSING_ORDER_ID = "99999999-9999-4999-8999-999999999999"

ORDER_FIXTURES = {
    OPEN_ORDER_ID: {
        "id": OPEN_ORDER_ID,
        "status": "open",
        "customer": {
            "id": "cust-123",
            "tier": "gold",
        },
        "items": [
            {
                "product_id": "burger-001",
                "name": "burger",
                "quantity": 2,
                "unit_price_cents": 1299,
            }
        ],
        "totals": {
            "subtotal_cents": 2598,
            "discount_cents": 200,
            "grand_total_cents": 2398,
            "currency": "USD",
        },
        "created_at": "2026-06-01T10:15:30Z",
        "updated_at": "2026-06-01T10:16:00Z",
    },
    SHIPPED_ORDER_ID: {
        "id": SHIPPED_ORDER_ID,
        "status": "shipped",
        "customer": {
            "id": "cust-456",
            "tier": "standard",
        },
        "items": [
            {
                "product_id": "fries-001",
                "name": "fries",
                "quantity": 1,
                "unit_price_cents": 499,
            }
        ],
        "totals": {
            "subtotal_cents": 499,
            "discount_cents": 0,
            "grand_total_cents": 499,
            "currency": "USD",
        },
        "created_at": "2026-06-02T11:00:00Z",
        "updated_at": "2026-06-03T08:10:00Z",
    },
}
