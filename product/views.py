from django.db.models import Avg, Count
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from .models import Category, Product, Review
from .serializers import (
    CategorySerializer,
    ProductSerializer,
    ReviewSerializer,
    ProductWithReviewsSerializer,
)


@api_view(["GET"])
def category_list_api_view(request):
    categories = Category.objects.annotate(products_count=Count("products")).order_by("id")
    data = CategorySerializer(categories, many=True).data
    return Response(data=data)


@api_view(["GET"])
def category_detail_api_view(request, id):
    category = Category.objects.annotate(products_count=Count("products")).filter(id=id).first()
    if not category:
        return Response({"error": "category not found"}, status=status.HTTP_404_NOT_FOUND)
    data = CategorySerializer(category, many=False).data
    return Response(data=data)


@api_view(["GET"])
def product_list_api_view(request):
    products = Product.objects.select_related("category").order_by("id")
    data = ProductSerializer(products, many=True).data
    return Response(data=data)


@api_view(["GET"])
def product_detail_api_view(request, id):
    product = Product.objects.select_related("category").filter(id=id).first()
    if not product:
        return Response({"error": "product not found"}, status=status.HTTP_404_NOT_FOUND)
    data = ProductSerializer(product, many=False).data
    return Response(data=data)


@api_view(["GET"])
def review_list_api_view(request):
    reviews = Review.objects.select_related("product").order_by("id")
    data = ReviewSerializer(reviews, many=True).data
    return Response(data=data)


@api_view(["GET"])
def review_detail_api_view(request, id):
    review = Review.objects.select_related("product").filter(id=id).first()
    if not review:
        return Response({"error": "review not found"}, status=status.HTTP_404_NOT_FOUND)
    data = ReviewSerializer(review, many=False).data
    return Response(data=data)


@api_view(["GET"])
def products_reviews_api_view(request):
    # общий средний балл всех отзывов
    overall = Review.objects.aggregate(rating=Avg("stars"))["rating"]
    overall_rating = round(float(overall), 2) if overall is not None else 0

    # товары + отзывы + средний балл по каждому товару
    products = (
        Product.objects.select_related("category")
        .prefetch_related("reviews")
        .annotate(rating=Avg("reviews__stars"))
        .order_by("id")
    )

    products_data = ProductWithReviewsSerializer(products, many=True).data

    return Response({
        "rating": overall_rating,
        "results": products_data
    })