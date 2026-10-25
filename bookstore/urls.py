from django.contrib import admin
from django.urls import include,path
from .views import hello, update_server
urlpatterns=[path("admin/",admin.site.urls),path("api/",include("product.urls")),path("api/",include("order.urls"))]
urlpatterns += [path("hello/", hello, name="hello"), path("update_server/", update_server, name="update-server")]

from django.conf import settings
if settings.DEBUG:
    urlpatterns += [path("__debug__/",include("debug_toolbar.urls"))]

from rest_framework.authtoken.views import obtain_auth_token
urlpatterns += [path("api/token/",obtain_auth_token,name="api-token")]
