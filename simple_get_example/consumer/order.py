from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class OrderItem:
    name: str
    quantity: int
    value: int

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "OrderItem":
        return cls(
            name=data["name"],
            quantity=data["quantity"],
            value=data["value"],
        )


@dataclass(frozen=True)
class Order:
    id: int
    items: tuple[OrderItem, ...]

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Order":
        return cls(
            id=data["id"],
            items=tuple(OrderItem.from_dict(item) for item in data["items"]),
        )

    def total(self) -> int:
        return sum(item.quantity * item.value for item in self.items)

    def __str__(self) -> str:
        return f"Order {self.id}, Total: {self.total()}"
