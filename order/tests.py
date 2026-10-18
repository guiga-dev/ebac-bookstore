from django.contrib.auth import get_user_model
from django.test import TestCase
from product.models import Product, Category
from .models import Order
from .serializers import OrderSerializer

class OrderSerializerTests(TestCase):
    def setUp(self):
        self.user=get_user_model().objects.create_user(username="leitor")
        category=Category.objects.create(name="Livros")
        self.product=Product.objects.create(name="Django",price="49.90",category=category)

    def test_create_and_relations(self):
        serializer=OrderSerializer(data={"user":self.user.pk,"products":[self.product.pk]})
        self.assertTrue(serializer.is_valid(),serializer.errors)
        order=serializer.save()
        self.assertEqual(order.products.get(),self.product)
        data=OrderSerializer(order).data
        self.assertEqual(data["products"],[self.product.pk])
        self.assertEqual(set(data),{"id","user","products","created_at"})

    def test_invalid_and_required_fields(self):
        for payload in [{},{"user":self.user.pk,"products":[]},{"user":9999,"products":[self.product.pk]},{"user":self.user.pk,"products":[9999]}]:
            self.assertFalse(OrderSerializer(data=payload).is_valid())
