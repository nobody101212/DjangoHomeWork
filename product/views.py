from django.db.models import Avg, Count
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from .models import UserConfirmation
from .serializers import RegisterSerializer, ConfirmSerializer, LoginSerializer


from .models import Category, Product, Review
from .serializers import (
    CategorySerializer,
    ProductSerializer,
    ReviewSerializer,
    ProductWithReviewsSerializer,
)


@api_view(["GET", "POST"])
def category_list_api_view(request):
    if request.method == "GET":
        categories = Category.objects.annotate(products_count=Count("products")).order_by("id")
        return Response(CategorySerializer(categories, many=True).data)

    serializer = CategorySerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET", "PUT", "PATCH", "DELETE"])
def category_detail_api_view(request, id):
    if request.method == "GET":
        category = Category.objects.annotate(products_count=Count("products")).filter(id=id).first()
        if not category:
            return Response({"error": "category not found"}, status=status.HTTP_404_NOT_FOUND)
        return Response(CategorySerializer(category).data)

    category = Category.objects.filter(id=id).first()
    if not category:
        return Response({"error": "category not found"}, status=status.HTTP_404_NOT_FOUND)

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
        products = Product.objects.select_related("category").order_by("id")
        return Response(ProductSerializer(products, many=True).data)

    serializer = ProductSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET", "PUT", "PATCH", "DELETE"])
def product_detail_api_view(request, id):
    product = Product.objects.select_related("category").filter(id=id).first()
    if not product:
        return Response({"error": "product not found"}, status=status.HTTP_404_NOT_FOUND)

    if request.method == "GET":
        return Response(ProductSerializer(product).data)

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
        reviews = Review.objects.select_related("product").order_by("id")
        return Response(ReviewSerializer(reviews, many=True).data)

    serializer = ReviewSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET", "PUT", "PATCH", "DELETE"])
def review_detail_api_view(request, id):
    review = Review.objects.select_related("product").filter(id=id).first()
    if not review:
        return Response({"error": "review not found"}, status=status.HTTP_404_NOT_FOUND)

    if request.method == "GET":
        return Response(ReviewSerializer(review).data)

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
        Product.objects.select_related("category")
        .prefetch_related("reviews")
        .annotate(rating=Avg("reviews__stars"))
        .order_by("id")
    )

    return Response({
        "rating": overall_rating,
        "results": ProductWithReviewsSerializer(products, many=True).data
    })


@api_view(["POST"])
def register_view(request):
    serializer = RegisterSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response({"message": "User created. Confirm your account."})
    return Response(serializer.errors, status=400)


@api_view(["POST"])
def confirm_view(request):
    serializer = ConfirmSerializer(data=request.data)
    if serializer.is_valid():
        username = serializer.validated_data["username"]
        code = serializer.validated_data["code"]

        try:
            user = User.objects.get(username=username)
            confirmation = UserConfirmation.objects.get(user=user)
        except:
            return Response({"error": "User not found"}, status=404)

        if confirmation.code == code:
            user.is_active = True
            user.save()
            confirmation.delete()
            return Response({"message": "User confirmed"})
        else:
            return Response({"error": "Invalid code"}, status=400)

    return Response(serializer.errors, status=400)


@api_view(["POST"])
def login_view(request):
    serializer = LoginSerializer(data=request.data)
    if serializer.is_valid():
        user = authenticate(
            username=serializer.validated_data["username"],
            password=serializer.validated_data["password"]
        )
        if user:
            if not user.is_active:
                return Response({"error": "User not confirmed"}, status=403)
            return Response({"message": "Login successful"})
        return Response({"error": "Invalid credentials"}, status=400)

    return Response(serializer.errors, status=400)