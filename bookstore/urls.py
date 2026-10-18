from django.contrib import admin
from django.urls import include,path
urlpatterns=[path("admin/",admin.site.urls),path("api/",include("product.urls")),path("api/",include("order.urls"))]

from django.conf import settings
if settings.DEBUG:
    urlpatterns += [path("__debug__/",include("debug_toolbar.urls"))]
