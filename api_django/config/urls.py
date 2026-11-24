from django.contrib import admin
from django.urls import path, include
from api import views

urlpatterns = [
    path("", views.painel),
    path("admin/", admin.site.urls),
    path("api/", include("api.urls")),
]
