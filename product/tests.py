from decimal import Decimal
from django.test import TestCase
from .models import Category, Product
from .serializers import CategorySerializer, ProductSerializer

class SerializerTests(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name="Programação")
        self.valid = {"name":"Python", "price":"39.90", "category_id":self.category.pk}

    def test_product_create_and_nested_category(self):
        serializer=ProductSerializer(data=self.valid)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        product=serializer.save()
        self.assertEqual(product.price,Decimal("39.90"))
        data=ProductSerializer(product).data
        self.assertEqual(data["category"]["name"], "Programação")
        self.assertEqual(set(data), {"id","name","price","description","active","category"})

    def test_product_required_and_invalid_data(self):
        for data, field in [({},"name"),({**self.valid,"price":"0"},"price"),({**self.valid,"price":"-1"},"price"),({**self.valid,"category_id":9999},"category_id")]:
            serializer=ProductSerializer(data=data)
            self.assertFalse(serializer.is_valid())
            self.assertIn(field,serializer.errors)

    def test_category_create_and_unique_name(self):
        serializer=CategorySerializer(data={"name":"Ficção"})
        self.assertTrue(serializer.is_valid(),serializer.errors)
        category=serializer.save()
        self.assertEqual(CategorySerializer(category).data["description"],"")
        self.assertFalse(CategorySerializer(data={"name":"Programação"}).is_valid())
        self.assertFalse(CategorySerializer(data={}).is_valid())
