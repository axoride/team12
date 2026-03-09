from decimal import Decimal
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import CartItem
from .serializers import CartItemSerializer


@api_view(['GET'])
def get_cart_items(request):
    items = CartItem.objects.all()
    serializer = CartItemSerializer(items, many=True)
    return Response(serializer.data)


@api_view(['POST'])
def add_to_cart(request):
    user_id = request.data.get('user_id')
    book_id = request.data.get('book_id')
    price = request.data.get('price')
    quantity = request.data.get('quantity', 1)

    if not user_id or not book_id or not price:
        return Response(
            {'error': 'user_id, book_id, and price are required'},
            status=status.HTTP_400_BAD_REQUEST
        )

    item = CartItem.objects.create(
        user_id=user_id,
        book_id=book_id,
        price=price,
        quantity=quantity
    )

    serializer = CartItemSerializer(item)
    return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(['GET'])
def get_cart_subtotal(request):
    user_id = request.GET.get('user_id')

    if not user_id:
        return Response(
            {'error': 'user_id is required'},
            status=status.HTTP_400_BAD_REQUEST
        )

    items = CartItem.objects.filter(user_id=user_id)

    subtotal = Decimal('0.00')
    for item in items:
        subtotal += item.price * item.quantity

    return Response({
        'user_id': int(user_id),
        'subtotal': subtotal
    })