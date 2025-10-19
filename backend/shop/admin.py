from django.contrib import admin

from .models import Order, OrderItem, Product, ProductImage


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("id", "sku", "title", "price", "active", "is_new", "is_hit", "stock_qty")
    list_filter = ("active", "is_new", "is_hit")
    search_fields = ("sku", "title", "description")
    inlines = [ProductImageInline]
    fields = ("sku", "title", "description", "price", "active", "is_new", "is_hit", "stock_qty", "low_stock_threshold")


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ("product", "qty", "price")


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "customer_name", "customer_phone", "total", "status", "created_at")
    list_filter = ("status",)
    search_fields = ("customer_name", "customer_phone", "customer_email")
    inlines = [OrderItemInline]
    readonly_fields = ("total", "created_at")
