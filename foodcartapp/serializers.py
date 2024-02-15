from django.core.validators import RegexValidator

from rest_framework.serializers import ModelSerializer
from rest_framework.serializers import ValidationError
from rest_framework.serializers import CharField, ListField, IntegerField
from phonenumber_field.serializerfields import PhoneNumberField

from .models import Product, Order, OrderContent


class OrderContentSerializer(ModelSerializer):
    product = IntegerField(source="OrderContent.item")
    quantity = IntegerField(
        source="OrderContent.quantity",
        min_value=1,
    )

    class Meta():
        model = OrderContent
        fields = ('id', 'product', 'quantity')

    def create(self, validated_data):
        return OrderContent.objects.create(**validated_data['OrderContent'])

    def update(self, instance, validated_data):
        instance.order = validated_data.get('order', instance.order),
        instance.item = validated_data.get('item', instance.item),
        instance.quantity = validated_data.get('quantity', instance.quantity),
        instance.price = validated_data.get('price', instance.price),
        instance.save()
        return instance


class OrderSerializer(ModelSerializer):
    firstname = CharField(source="Order.name")
    lastname = CharField(source="Order.surname")
    address = CharField(source="Order.address")
    phonenumber = CharField(
        source="Order.phone",
        max_length=17,
        validators=[
            RegexValidator(
                regex=r'^((\+?7|8)[ \-.]?)?((\([1-9][0-9]{2}\))|([1-9][0-9]{2}))?([ \-.])?(\d{3}[\- .]?\d{2}[\- .]?\d{2})$',
                message="Phone number must be entered in the format '+71234567890'. Up to 13 digits allowed."
            ),
        ],
    )
    products = OrderContentSerializer(many=True)

    class Meta:
        model = Order
        fields = ('id', 'firstname', 'lastname', 'address', 'phonenumber', 'products')

    def create(self, validated_data):
        return Order.objects.create(**validated_data['Order'])

    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name),
        instance.surname = validated_data.get('surname', instance.surname),
        instance.address = validated_data.get('address', instance.address),
        instance.phone = validated_data.get('phone', instance.phone),
        instance.save()
        return instance
