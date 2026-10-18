from django.conf import settings
from django.db import models

class Order(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="orders")
    products = models.ManyToManyField("product.Product", related_name="orders")
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        ordering = ["id"]
