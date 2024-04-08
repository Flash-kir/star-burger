from django.utils import timezone
from django.db import models
from django.core.validators import MinValueValidator
from phonenumber_field.modelfields import PhoneNumberField


class Restaurant(models.Model):
    name = models.CharField(
        'название',
        max_length=50
    )
    address = models.CharField(
        'адрес',
        max_length=100,
        blank=True,
    )
    contact_phone = models.CharField(
        'контактный телефон',
        max_length=50,
        blank=True,
    )

    class Meta:
        verbose_name = 'ресторан'
        verbose_name_plural = 'рестораны'

    def __str__(self):
        return self.name


class ProductQuerySet(models.QuerySet):
    def available(self):
        products = (
            RestaurantMenuItem.objects
            .filter(availability=True)
            .values_list('product')
        )
        return self.filter(pk__in=products)


class ProductCategory(models.Model):
    name = models.CharField(
        'название',
        max_length=50
    )

    class Meta:
        verbose_name = 'категория'
        verbose_name_plural = 'категории'

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(
        'название',
        max_length=50
    )
    category = models.ForeignKey(
        ProductCategory,
        verbose_name='категория',
        related_name='products',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    price = models.DecimalField(
        'цена',
        max_digits=8,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    image = models.ImageField(
        'картинка'
    )
    special_status = models.BooleanField(
        'спец.предложение',
        default=False,
        db_index=True,
    )
    description = models.TextField(
        'описание',
        max_length=200,
        blank=True,
    )

    objects = ProductQuerySet.as_manager()

    class Meta:
        verbose_name = 'товар'
        verbose_name_plural = 'товары'

    def __str__(self):
        return self.name


class RestaurantMenuItem(models.Model):
    restaurant = models.ForeignKey(
        Restaurant,
        related_name='menu_items',
        verbose_name="ресторан",
        on_delete=models.CASCADE,
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='menu_items',
        verbose_name='продукт',
    )
    availability = models.BooleanField(
        'в продаже',
        default=True,
        db_index=True
    )

    class Meta:
        verbose_name = 'пункт меню ресторана'
        verbose_name_plural = 'пункты меню ресторана'
        unique_together = [
            ['restaurant', 'product']
        ]

    def __str__(self):
        return f"{self.restaurant.name} - {self.product.name}"


class Order(models.Model):
    NEW = 'N'
    COOK = 'C'
    DELIVERY = 'D'
    READY = 'R'
    ORDER_STATUS = (
        ('N', 'Необработанный'),
        ('C', 'Готовится'),
        ('D', 'Передан в доставку'),
        ('R', 'Выполнен'),
    )
    CASH = 'C'
    ELECTRONIC = 'E'
    PAYMENT_METHODS = (
        ('C', 'Наличные'),
        ('E', 'Электронно'),
    )
    name = models.CharField(
        verbose_name='имя',
        max_length=50
    )
    surname = models.CharField(
        verbose_name='отчество',
        max_length=50,
    )
    phonenumber = PhoneNumberField(
        region="RU",
        db_index=True,
        verbose_name='телефон',
    )
    address = models.CharField(
        verbose_name='адрес',
        max_length=200,
    )
    status = models.CharField(
        max_length=2,
        choices=ORDER_STATUS,
        default=NEW,
        db_index=True,
        verbose_name='статус заказа',
    )
    payment_method = models.CharField(
        max_length=2,
        choices=PAYMENT_METHODS,
        blank=True,
        db_index=True,
        verbose_name='метод оплаты',
    )
    restaurant = models.ForeignKey(
        Restaurant,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        default=None,
    )
    comment = models.TextField(
        max_length=300,
        blank=True,
        verbose_name='комментарий',
    )
    registered_at = models.DateTimeField(
        default=timezone.now,
        blank=True,
        db_index=True,
        verbose_name='время регистрации',
    )
    called_at = models.DateTimeField(
        blank=True,
        null=True,
        db_index=True,
        verbose_name='время обзвона',
    )
    delivered_at = models.DateTimeField(
        blank=True,
        null=True,
        db_index=True,
        verbose_name='время доставки',
    )

    def __str__(self):
        return f'{self.pk}. {self.surname} {self.name} - {self.phonenumber}({self.address})'

    def get_order_items_list(self):
        return list(self.items.values_list('item', flat=True))

    def restaurants_possibility_make_order(self, ):
        actual_menus = {}
        menu_items = list(RestaurantMenuItem.objects.filter(availability=True).values_list('restaurant', 'product'))
        for item in menu_items:
            if item[0] not in actual_menus.keys():
                actual_menus[item[0]] = []
            actual_menus[item[0]].append(item[1])
        item_list = self.get_order_items_list()
        restaurant_list = []
        for restaurant, products_list in actual_menus.items():
            if set(item_list).issubset(set(products_list)):
                restaurant_list.append(restaurant)
        return restaurant_list


class OrderContent(models.Model):
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        verbose_name='заказ',
        related_name='items'
    )
    item = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        verbose_name='продукт',
        related_name='products',
    )
    quantity = models.IntegerField(
        verbose_name='количество',
        validators=[MinValueValidator(1)],
    )
    price = models.DecimalField(
        'цена',
        max_digits=8,
        decimal_places=2,
        validators=[MinValueValidator(0)],
    )


class Address(models.Model):
    address = models.CharField(
        verbose_name='адрес',
        max_length=200,
    )
    lat = models.DecimalField(
        'широта',
        max_digits=8,
        decimal_places=2,
        default=None,
        null=True,
    )
    lon = models.DecimalField(
        'долгота',
        max_digits=8,
        decimal_places=2,
        default=None,
        null=True,
    )

    def __str__(self):
        return self.address


class Distances(models.Model):
    address_1 = models.ForeignKey(
        Address,
        on_delete=models.SET_NULL,
        null=True,
        related_name='address_1',
        verbose_name='адрес 1'
    )
    address_2 = models.ForeignKey(
        Address,
        on_delete=models.SET_NULL,
        null=True,
        related_name='address_2',
        verbose_name='адрес 2'
    )
    distance = models.DecimalField(
        'расстояние',
        max_digits=8,
        decimal_places=2,
        default=None,
        null=True,
    )

    class Meta:
        unique_together = ['address_1', 'address_2']

    def __str__(self):
        return f'{self.distance} км.'


class OrderDistance(models.Model):
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        verbose_name='заказ',
        related_name='distances',
        null=True,
        default=None,
    )
    restaurant = models.ForeignKey(
        Restaurant,
        on_delete=models.CASCADE,
        verbose_name='ресторан',
        related_name='distances',
        null=True,
        default=None,
    )
    distance = models.ForeignKey(
        Distances,
        verbose_name='расстояние',
        default=None,
        null=True,
        on_delete=models.SET_NULL,
    )

    class Meta:
        unique_together = ['order', 'restaurant']
