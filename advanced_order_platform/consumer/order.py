from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True) # turn simple python class into immutable data container, i.e. object from dataclass is immutable, it can't be changed after initialization
class Customer:
    id: str
    tier: str

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Customer":
        return cls(id=data["id"], tier=data["tier"])


@dataclass(frozen=True)
class OrderItem:
    product_id: str
    name: str
    quantity: int
    unit_price_cents: int

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "OrderItem":
        return cls(
            product_id=data["product_id"],
            name=data["name"],
            quantity=data["quantity"],
            unit_price_cents=data["unit_price_cents"],
        )


@dataclass(frozen=True)
class Totals:
    subtotal_cents: int
    discount_cents: int
    grand_total_cents: int
    currency: str

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Totals":
        return cls(
            subtotal_cents=data["subtotal_cents"],
            discount_cents=data["discount_cents"],
            grand_total_cents=data["grand_total_cents"],
            currency=data["currency"],
        )


@dataclass(frozen=True)
class Order:
    id: str
    status: str
    customer: Customer
    items: tuple[OrderItem, ...]
    totals: Totals
    created_at: str
    updated_at: str

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Order":
        return cls(
            id=data["id"],
            status=data["status"],
            customer=Customer.from_dict(data["customer"]),
            items=tuple(OrderItem.from_dict(item) for item in data["items"]),
            totals=Totals.from_dict(data["totals"]),
            created_at=data["created_at"],
            updated_at=data["updated_at"],
        )


@dataclass(frozen=True)
class NewOrderItem:
    product_id: str
    quantity: int

    def to_dict(self) -> dict[str, Any]:
        return {
            "product_id": self.product_id,
            "quantity": self.quantity,
        }


@dataclass(frozen=True)
class NewOrder:
    customer_id: str
    items: tuple[NewOrderItem, ...]
    coupon_code: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "customer_id": self.customer_id,
            "items": [item.to_dict() for item in self.items],
            "coupon_code": self.coupon_code,
        }


@dataclass(frozen=True)
class ApiError:
    code: str
    message: str
    correlation_id: str

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ApiError":
        return cls(
            code=data["code"],
            message=data["message"],
            correlation_id=data["correlation_id"],
        )


class OrderApiError(RuntimeError):
    def __init__(self, status_code: int, api_error: ApiError) -> None:
        super().__init__(f"{status_code} {api_error.code}: {api_error.message}")
        self.status_code = status_code
        self.api_error = api_error
