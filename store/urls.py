from django.urls import path

from . import views

app_name = "store"

urlpatterns = [
    path("", views.home, name="home"),
    path("about/", views.about, name="about"),
    path("order/", views.product_all, name="product_all"),
    path("<slug:slug>", views.product_detail, name="product_detail"),
    path("store/<slug:category_slug>/", views.category_list, name="category_list"),
]
