from rest_framework.test import APITestCase
from .models import Category, Product

class ProductViewSetTests(APITestCase):
    def test_product_crud(self):
        category=Category.objects.create(name="Tecnologia")
        response=self.client.post("/api/products/",{"name":"API","price":"20.00","category_id":category.pk})
        self.assertEqual(response.status_code,201,response.data)
        url=f"/api/products/{response.data['id']}/"
        self.assertEqual(self.client.get(url).status_code,200)
        self.assertEqual(self.client.patch(url,{"price":"25.00"}).status_code,200)
        self.assertEqual(self.client.get("/api/products/").status_code,200)
        self.assertEqual(self.client.delete(url).status_code,204)
        self.assertEqual(self.client.get(url).status_code,404)

    def test_category_crud_and_validation(self):
        response=self.client.post("/api/categories/",{"name":"Romance"})
        self.assertEqual(response.status_code,201)
        url=f"/api/categories/{response.data['id']}/"
        self.assertEqual(self.client.get(url).data["name"],"Romance")
        self.assertEqual(self.client.patch(url,{"description":"Literatura"}).status_code,200)
        self.assertEqual(self.client.delete(url).status_code,204)
        self.assertEqual(self.client.post("/api/products/",{}).status_code,400)
