from django.urls import path, include
from .views import webhook, test_send

urlpatterns = [
    path("webhook", webhook),
    path("test", test_send),
]
path("tg/", include("telebot.urls")),
