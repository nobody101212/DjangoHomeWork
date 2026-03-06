from django.db.models import Avg, Count
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from .models import Category, Product, Review
from .serializers import (
    CategorySerializer, ProductSerializer, ReviewSerializer,
    ProductWithReviewsSerializer
)


@api_view(["GET", "POST"])
def category_list_api_view(request):
    if request.method == "GET":
        categories = Category.objects.annotate(products_count=Count("products")).order_by("id")
        data = CategorySerializer(categories, many=True).data
        return Response(data=data)

    serializer = CategorySerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET", "PUT", "PATCH", "DELETE"])
def category_detail_api_view(request, id):
    category = Category.objects.filter(id=id).first()
    if not category:
        return Response({"error": "category not found"}, status=status.HTTP_404_NOT_FOUND)

    if request.method == "GET":
        category_qs = Category.objects.annotate(products_count=Count("products")).filter(id=id).first()
        data = CategorySerializer(category_qs).data
        return Response(data=data)

    if request.method in ("PUT", "PATCH"):
        serializer = CategorySerializer(category, data=request.data, partial=(request.method == "PATCH"))
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    category.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)



@api_view(["GET", "POST"])
def product_list_api_view(request):
    if request.method == "GET":
        products = Product.objects.all().order_by("id")
        data = ProductSerializer(products, many=True).data
        return Response(data=data)

    serializer = ProductSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET", "PUT", "PATCH", "DELETE"])
def product_detail_api_view(request, id):
    product = Product.objects.filter(id=id).first()
    if not product:
        return Response({"error": "product not found"}, status=status.HTTP_404_NOT_FOUND)

    if request.method == "GET":
        data = ProductSerializer(product).data
        return Response(data=data)

    if request.method in ("PUT", "PATCH"):
        serializer = ProductSerializer(product, data=request.data, partial=(request.method == "PATCH"))
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    product.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)



@api_view(["GET", "POST"])
def review_list_api_view(request):
    if request.method == "GET":
        reviews = Review.objects.all().order_by("id")
        data = ReviewSerializer(reviews, many=True).data
        return Response(data=data)

    serializer = ReviewSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET", "PUT", "PATCH", "DELETE"])
def review_detail_api_view(request, id):
    review = Review.objects.filter(id=id).first()
    if not review:
        return Response({"error": "review not found"}, status=status.HTTP_404_NOT_FOUND)

    if request.method == "GET":
        data = ReviewSerializer(review).data
        return Response(data=data)

    if request.method in ("PUT", "PATCH"):
        serializer = ReviewSerializer(review, data=request.data, partial=(request.method == "PATCH"))
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    review.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)



@api_view(["GET"])
def products_reviews_api_view(request):
    overall = Review.objects.aggregate(rating=Avg("stars"))["rating"]
    overall_rating = round(float(overall), 2) if overall is not None else 0

    products = (
        Product.objects.prefetch_related("reviews")
        .annotate(rating=Avg("reviews__stars"))
        .order_by("id")
    )
    products_data = ProductWithReviewsSerializer(products, many=True).data

    return Response({
        "rating": overall_rating,
        "results": products_data
    })