from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import Dict, List

from django.core.exceptions import ValidationError
from django.core.validators import validate_email

from .models import Order, OrderItem, Product


def serialize_product(product: Product) -> Dict[str, object]:
    return {
        "id": product.id,
        "sku": product.sku,
        "title": product.title,
        "description": product.description,
        "price": _decimal_to_number(product.price),
        "active": product.active,
        "is_new": getattr(product, "is_new", False),
        "is_hit": getattr(product, "is_hit", False),
        "stock_qty": getattr(product, "stock_qty", 0),
        "low_stock_threshold": getattr(product, "low_stock_threshold", 0),
        "images": [
            {
                "id": image.id,
                "image": image.image.url if getattr(image, "image", None) else "",
            }
            for image in product.images.all()
        ],
    }


def serialize_order(order: Order) -> Dict[str, object]:
    return {
        "id": order.id,
        "total": _decimal_to_number(order.total),
        "status": order.status,
    }


@dataclass
class OrderItemPayload:
    product_id: int
    qty: int


@dataclass
class OrderPayload:
    customer_name: str
    customer_phone: str
    customer_email: str
    delivery_method: str
    delivery_address: str
    items: List[OrderItemPayload]


def validate_order_payload(data: dict) -> OrderPayload:
    if not isinstance(data, dict):
        raise ValidationError("Order payload must be an object.")

    name = _require_string(data.get("customer_name"), "customer_name")
    phone = _require_string(data.get("customer_phone"), "customer_phone")

    email_raw = data.get("customer_email", "")
    email = ""
    if email_raw:
        email = _require_string(email_raw, "customer_email", allow_blank=True)
        try:
            validate_email(email)
        except ValidationError as exc:
            raise ValidationError({"customer_email": exc.messages})

    delivery_method = _require_string(data.get("delivery_method", "pickup"), "delivery_method", allow_blank=False)
    delivery_address = _require_string(data.get("delivery_address", ""), "delivery_address", allow_blank=True)

    items_raw = data.get("items")
    if not isinstance(items_raw, list):
        raise ValidationError({"items": "Items must be provided as a list."})

    items: List[OrderItemPayload] = []
    for item in items_raw:
        if not isinstance(item, dict):
            raise ValidationError({"items": "Each item must be an object."})
        product_id = item.get("product_id")
        qty = item.get("qty")
        if not isinstance(product_id, int):
            raise ValidationError({"product_id": "Invalid product_id."})
        if not isinstance(qty, int) or qty < 1:
            raise ValidationError({"qty": "Quantity must be a positive integer."})
        items.append(OrderItemPayload(product_id=product_id, qty=qty))

    if not items:
        raise ValidationError({"items": "Order must contain at least one item."})

    return OrderPayload(
        customer_name=name,
        customer_phone=phone,
        customer_email=email,
        delivery_method=delivery_method,
        delivery_address=delivery_address,
        items=items,
    )


def create_order(payload: OrderPayload) -> Order:
    product_ids = [item.product_id for item in payload.items]
    products = {
        product.id: product
        for product in Product.objects.filter(id__in=product_ids, active=True)
    }

    order = Order.objects.create(
        customer_name=payload.customer_name,
        customer_phone=payload.customer_phone,
        customer_email=payload.customer_email,
        delivery_method=payload.delivery_method,
        delivery_address=payload.delivery_address,
        total=Decimal("0.0"),
    )

    total = Decimal("0.0")
    for item in payload.items:
        product = products.get(item.product_id)
        if not product:
            continue
        qty = Decimal(item.qty)
        line_total = Decimal(product.price) * qty
        total += line_total
        OrderItem.objects.create(
            order=order,
            product=product,
            qty=item.qty,
            price=product.price,
        )

    order.total = total
    order.save(update_fields=["total"])
    return order


def _require_string(value, field: str, allow_blank: bool = False) -> str:
    if value is None:
        raise ValidationError({field: "This field is required."})
    if not isinstance(value, str):
        raise ValidationError({field: "Value must be a string."})
    cleaned = value.strip()
    if not allow_blank and not cleaned:
        raise ValidationError({field: "This field may not be blank."})
    return cleaned


def _decimal_to_number(value) -> float:
    if value is None:
        return 0.0
    return float(Decimal(value))
