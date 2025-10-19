import json
from django.core.exceptions import ValidationError
from django.http import Http404, JsonResponse
from django.views import View

from .models import Product
from .serializers import (
    create_order,
    serialize_order,
    serialize_product,
    validate_order_payload,
)


class HealthView(View):
    def get(self, request, *args, **kwargs):
        return JsonResponse({"ok": True})


class ProductListView(View):
    def get(self, request, *args, **kwargs):
        products = (
            Product.objects.filter(active=True)
            .prefetch_related("images")
            .order_by("-id")
        )
        data = [serialize_product(product) for product in products]
        return JsonResponse(data, safe=False)


class ProductDetailView(View):
    def get(self, request, id: int, *args, **kwargs):
        try:
            product = (
                Product.objects.prefetch_related("images")
                .get(id=id, active=True)
            )
        except Product.DoesNotExist as exc:
            raise Http404("Product not found.") from exc
        return JsonResponse(serialize_product(product))


class OrderCreateView(View):
    def post(self, request, *args, **kwargs):
        try:
            payload = json.loads(request.body.decode() or "{}")
        except json.JSONDecodeError:
            return JsonResponse({"errors": {"detail": "Invalid JSON."}}, status=400)

        try:
            validated = validate_order_payload(payload)
        except ValidationError as exc:
            return JsonResponse({"errors": _error_messages(exc)}, status=400)

        order = create_order(validated)
        return JsonResponse(serialize_order(order), status=201)


def _error_messages(exc: Exception):
    if hasattr(exc, "message_dict"):
        return exc.message_dict
    if hasattr(exc, "messages"):
        return exc.messages
    return {"detail": str(exc)}
