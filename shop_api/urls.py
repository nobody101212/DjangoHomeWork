"""
URL configuration for shop_api project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path
from product.views import *

urlpatterns = [
    path("admin/", admin.site.urls),

    path("api/v1/categories/", CategoryListCreateView.as_view()),
    path("api/v1/categories/<int:id>/", CategoryDetailView.as_view()),

    path("api/v1/products/", ProductListCreateView.as_view()),
    path("api/v1/products/<int:id>/", ProductDetailView.as_view()),

    path("api/v1/reviews/", ReviewListCreateView.as_view()),
    path("api/v1/reviews/<int:id>/", ReviewDetailView.as_view()),

    path("api/v1/products/reviews/", ProductsReviewsView.as_view()),

    path("api/v1/users/register/", RegisterView.as_view()),
    path("api/v1/users/confirm/", ConfirmView.as_view()),
    path("api/v1/users/login/", LoginView.as_view()),
]
