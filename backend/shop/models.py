from django.db import models


class Product(models.Model):
    sku = models.CharField(max_length=64, unique=True)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, default="")
    price = models.DecimalField(max_digits=12, decimal_places=2)
    active = models.BooleanField(default=True)
    is_new = models.BooleanField(default=False)
    is_hit = models.BooleanField(default=False)
    stock_qty = models.IntegerField(default=0)
    low_stock_threshold = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"{self.sku} | {self.title}"


class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="images")
    image = models.ImageField(upload_to="products/")

    def __str__(self) -> str:
        return f"{self.product_id}:{self.image.name}"


class Order(models.Model):
    STATUS_NEW = "new"
    STATUS_PROCESSING = "processing"
    STATUS_DONE = "done"
    STATUS_CHOICES = [
        (STATUS_NEW, "new"),
        (STATUS_PROCESSING, "processing"),
        (STATUS_DONE, "done"),
    ]

    customer_name = models.CharField(max_length=255)
    customer_phone = models.CharField(max_length=64)
    customer_email = models.EmailField(blank=True, default="")
    delivery_method = models.CharField(max_length=64, default="pickup")
    delivery_address = models.CharField(max_length=512, blank=True, default="")
    total = models.DecimalField(max_digits=12, decimal_places=2)
    status = models.CharField(max_length=32, choices=STATUS_CHOICES, default=STATUS_NEW)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"Order #{self.pk}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    qty = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=12, decimal_places=2)

    def __str__(self) -> str:
        return f"Item {self.pk}"
