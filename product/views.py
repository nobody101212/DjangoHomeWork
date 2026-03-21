from django.db.models import Avg, Count
from rest_framework import generics
from rest_framework.response import Response
from django.contrib.auth import authenticate
from django.contrib.auth.models import User

from .models import Category, Product, Review, UserConfirmation
from .serializers import (
    CategorySerializer,
    ProductSerializer,
    ReviewSerializer,
    ProductWithReviewsSerializer,
    RegisterSerializer,
    ConfirmSerializer,
    LoginSerializer
)


class CategoryListCreateView(generics.ListCreateAPIView):
    queryset = Category.objects.annotate(products_count=Count("products")).order_by("id")
    serializer_class = CategorySerializer


class CategoryDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    lookup_field = "id"


class ProductListCreateView(generics.ListCreateAPIView):
    queryset = Product.objects.select_related("category").order_by("id")
    serializer_class = ProductSerializer


class ProductDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Product.objects.select_related("category")
    serializer_class = ProductSerializer
    lookup_field = "id"


class ReviewListCreateView(generics.ListCreateAPIView):
    queryset = Review.objects.select_related("product").order_by("id")
    serializer_class = ReviewSerializer


class ReviewDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Review.objects.select_related("product")
    serializer_class = ReviewSerializer
    lookup_field = "id"


class ProductsReviewsView(generics.GenericAPIView):
    def get(self, request):
        overall = Review.objects.aggregate(rating=Avg("stars"))["rating"]
        overall_rating = round(float(overall), 2) if overall else 0

        products = (
            Product.objects.select_related("category")
            .prefetch_related("reviews")
            .annotate(rating=Avg("reviews__stars"))
            .order_by("id")
        )

        data = ProductWithReviewsSerializer(products, many=True).data

        return Response({
            "rating": overall_rating,
            "results": data
        })


class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer


class ConfirmView(generics.GenericAPIView):
    serializer_class = ConfirmSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
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
            return Response({"error": "Invalid code"}, status=400)

        return Response(serializer.errors, status=400)


class LoginView(generics.GenericAPIView):
    serializer_class = LoginSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
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