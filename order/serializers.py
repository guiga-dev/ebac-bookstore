from rest_framework import serializers
from .models import Order

class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model=Order
        fields=["id","user","products","created_at"]
        read_only_fields=["user","created_at"]
        extra_kwargs={"products":{"allow_empty":False}}
