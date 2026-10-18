from rest_framework.test import APITestCase
from .models import Category,Product

class PaginationTests(APITestCase):
    def test_pages_have_bounded_results_and_next_link(self):
        category=Category.objects.create(name="Paginação")
        Product.objects.bulk_create([Product(name=f"Livro {n}",price="10",category=category) for n in range(12)])
        first=self.client.get("/api/products/")
        self.assertEqual(first.status_code,200)
        self.assertEqual(first.data["count"],12)
        self.assertEqual(len(first.data["results"]),5)
        self.assertIsNotNone(first.data["next"])
        second=self.client.get("/api/products/?page=2")
        self.assertTrue(set(p["id"] for p in first.data["results"]).isdisjoint(p["id"] for p in second.data["results"]))
        self.assertEqual(len(self.client.get("/api/products/?page=3").data["results"]),2)
        self.assertEqual(self.client.get("/api/products/?page=99").status_code,404)
