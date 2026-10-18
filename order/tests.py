from django.contrib.auth import get_user_model
from django.test import TestCase
from product.models import Product,Category
from .serializers import OrderSerializer

class OrderSerializerTests(TestCase):
    def test_user_is_assigned_by_view_not_client(self):
        user=get_user_model().objects.create_user(username="cliente")
        category=Category.objects.create(name="Livros")
        product=Product.objects.create(name="Django",price="49",category=category)
        serializer=OrderSerializer(data={"user":999,"products":[product.pk]})
        self.assertTrue(serializer.is_valid(),serializer.errors)
        self.assertNotIn("user",serializer.validated_data)
        order=serializer.save(user=user)
        self.assertEqual(order.user,user)
        self.assertFalse(OrderSerializer(data={"products":[]}).is_valid())
