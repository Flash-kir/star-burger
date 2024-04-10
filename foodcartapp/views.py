from django.http import JsonResponse
from django.templatetags.static import static
from django.db import transaction

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.serializers import ValidationError

from .models import Product
from .models import Order
from .models import OrderContent

from .serializers import OrderSerializer
from .serializers import OrderContentSerializer


def banners_list_api(request):
    return JsonResponse([
        {
            'title': 'Burger',
            'src': static('burger.jpg'),
            'text': 'Tasty Burger at your door step',
        },
        {
            'title': 'Spices',
            'src': static('food.jpg'),
            'text': 'All Cuisines',
        },
        {
            'title': 'New York',
            'src': static('tasty.jpg'),
            'text': 'Food is incomplete without a tasty dessert',
        }
    ], safe=False, json_dumps_params={
        'ensure_ascii': False,
        'indent': 4,
    })


def product_list_api(request):
    products = Product.objects.select_related('category').available()

    dumped_products = []
    for product in products:
        dumped_product = {
            'id': product.id,
            'name': product.name,
            'price': product.price,
            'special_status': product.special_status,
            'description': product.description,
            'category': {
                'id': product.category.id,
                'name': product.category.name,
            } if product.category else None,
            'image': product.image.url,
            'restaurant': {
                'id': product.id,
                'name': product.name,
            }
        }
        dumped_products.append(dumped_product)
    return JsonResponse(dumped_products, safe=False, json_dumps_params={
        'ensure_ascii': False,
        'indent': 4,
    })


@api_view(['POST'])
def register_order(request):
    serializer = OrderSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    products = request.data.get('products', [])
    if not isinstance(products, list):
        raise ValidationError('Expects products field be a list')

    for items in products:
        serializer_products = OrderContentSerializer(data=items)
        serializer_products.is_valid(raise_exception=True)
    number = serializer.validated_data['phonenumber']
    serializer.validated_data['phonenumber'] = number.as_national
    order = serializer.save(data=serializer.validated_data)
    with transaction.atomic():
        for item in serializer.validated_data['products']:
            serializer_products.save(data=item['OrderContent'], order=order)
    return Response(serializer.validated_data)
