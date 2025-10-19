from django.urls import path
from .views import HealthView, ProductListView, ProductDetailView, OrderCreateView

urlpatterns = [
    path("health", HealthView.as_view()),
    path("products", ProductListView.as_view()),
    path("products/<int:id>", ProductDetailView.as_view()),
    path("orders", OrderCreateView.as_view()),
]
