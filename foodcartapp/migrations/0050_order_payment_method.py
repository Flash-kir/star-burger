# Generated by Django 3.2.15 on 2023-06-08 21:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0049_auto_20230608_2049'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='payment_method',
            field=models.CharField(choices=[('C', 'Наличные'), ('E', 'Электронно')], db_index=True, default='C', max_length=2),
        ),
    ]
