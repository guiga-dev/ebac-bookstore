from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from product.models import Product,Category

class OrderViewSetTests(APITestCase):
    def test_order_crud(self):
        user=get_user_model().objects.create_user(username="cliente")
        category=Category.objects.create(name="Ciência")
        product=Product.objects.create(name="Cosmos",price="25.00",category=category)
        response=self.client.post("/api/orders/",{"user":user.pk,"products":[product.pk]},format="json")
        self.assertEqual(response.status_code,201,response.data)
        url=f"/api/orders/{response.data['id']}/"
        self.assertEqual(self.client.get(url).status_code,200)
        self.assertEqual(self.client.get("/api/orders/").status_code,200)
        self.assertEqual(self.client.patch(url,{"products":[product.pk]},format="json").status_code,200)
        self.assertEqual(self.client.delete(url).status_code,204)
