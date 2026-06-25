from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/auth/", include("accounts.urls")),
    path("api/products/", include("catalog.urls")),
    path("api/search/", include("search.urls")),
]