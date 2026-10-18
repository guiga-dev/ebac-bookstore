from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework.authtoken.models import Token
from product.models import Product,Category
from .models import Order

class OrderAuthenticationTests(APITestCase):
    def setUp(self):
        self.user=get_user_model().objects.create_user(username="cliente",password="test-only-password")
        self.other=get_user_model().objects.create_user(username="outro")
        category=Category.objects.create(name="Livros")
        self.product=Product.objects.create(name="Django",price="49",category=category)
        self.own=Order.objects.create(user=self.user)
        self.foreign=Order.objects.create(user=self.other)
        self.token=Token.objects.create(user=self.user)

    def login_token(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.token.key}")

    def test_anonymous_and_invalid_token_rejected(self):
        self.assertEqual(self.client.get("/api/orders/").status_code,401)
        self.client.credentials(HTTP_AUTHORIZATION="Token invalid")
        self.assertEqual(self.client.get("/api/orders/").status_code,401)

    def test_products_remain_public(self):
        self.assertEqual(self.client.get("/api/products/").status_code,200)

    def test_only_owner_can_see_update_delete_order(self):
        self.login_token()
        data=self.client.get("/api/orders/").data
        self.assertEqual([item["id"] for item in data["results"]],[self.own.pk])
        url=f"/api/orders/{self.foreign.pk}/"
        self.assertEqual(self.client.get(url).status_code,404)
        self.assertEqual(self.client.patch(url,{"products":[self.product.pk]},format="json").status_code,404)
        self.assertEqual(self.client.delete(url).status_code,404)

    def test_create_cannot_impersonate_owner_and_crud_works(self):
        self.login_token()
        response=self.client.post("/api/orders/",{"user":self.other.pk,"products":[self.product.pk]},format="json")
        self.assertEqual(response.status_code,201,response.data)
        self.assertEqual(response.data["user"],self.user.pk)
        url=f"/api/orders/{response.data['id']}/"
        self.assertEqual(self.client.patch(url,{"products":[self.product.pk]},format="json").status_code,200)
        self.assertEqual(self.client.delete(url).status_code,204)

    def test_real_token_endpoint(self):
        response=self.client.post("/api/token/",{"username":"cliente","password":"test-only-password"})
        self.assertEqual(response.status_code,200)
        self.assertEqual(response.data["token"],self.token.key)
