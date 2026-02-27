from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from .models import Category, Product, Review


@api_view(["GET"])
def category_list_api_view(request):
    categories = Category.objects.all()
    data = [{"id": c.id, "name": c.name} for c in categories]
    return Response(data=data)


@api_view(["GET"])
def category_detail_api_view(request, id):
    try:
        c = Category.objects.get(id=id)
    except Category.DoesNotExist:
        return Response({"error": "category not found"}, status=status.HTTP_404_NOT_FOUND)

    data = {"id": c.id, "name": c.name}
    return Response(data=data)


@api_view(["GET"])
def product_list_api_view(request):
    products = Product.objects.all()
    data = []
    for p in products:
        data.append({
            "id": p.id,
            "title": p.title,
            "description": p.description,
            "price": str(p.price),        # Decimal -> строка, чтобы JSON точно не ругался
            "category": p.category_id,    # id категории
        })
    return Response(data=data)


@api_view(["GET"])
def product_detail_api_view(request, id):
    try:
        p = Product.objects.get(id=id)
    except Product.DoesNotExist:
        return Response({"error": "product not found"}, status=status.HTTP_404_NOT_FOUND)

    data = {
        "id": p.id,
        "title": p.title,
        "description": p.description,
        "price": str(p.price),
        "category": p.category_id,
    }
    return Response(data=data)


@api_view(["GET"])
def review_list_api_view(request):
    reviews = Review.objects.all()
    data = [{"id": r.id, "text": r.text, "product": r.product_id} for r in reviews]
    return Response(data=data)


@api_view(["GET"])
def review_detail_api_view(request, id):
    try:
        r = Review.objects.get(id=id)
    except Review.DoesNotExist:
        return Response({"error": "review not found"}, status=status.HTTP_404_NOT_FOUND)

    data = {"id": r.id, "text": r.text, "product": r.product_id}
    return Response(data=data)