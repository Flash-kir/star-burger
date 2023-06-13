# Generated by Django 3.2.15 on 2023-06-13 11:18

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0055_alter_orderdistance_restaurant'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='restaurant',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to='foodcartapp.restaurant'),
        ),
    ]
