# Generated by Django 4.2.1 on 2023-06-19 13:03

import datetime
from django.db import migrations, models
import django.db.models.deletion
import wallet.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('account', '0004_userdata_is_admin_alter_userdata_date_joined_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Stock',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(max_length=6, unique=True, validators=[wallet.models.validate_code])),
                ('name_enterprise', models.CharField(max_length=35)),
                ('cnpj', models.CharField(max_length=18)),
            ],
        ),
        migrations.CreateModel(
            name='Transaction',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_done', models.DateField(blank=True, default=datetime.datetime.now)),
                ('quantity_stock', models.PositiveIntegerField()),
                ('unite_price', models.DecimalField(decimal_places=2, max_digits=8)),
                ('type_of', models.CharField(choices=[('C', 'Compra'), ('V', 'Venda')], max_length=1)),
                ('brokerage', models.DecimalField(decimal_places=2, max_digits=8)),
                ('investor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='account.investor')),
                ('stock', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='wallet.stock')),
            ],
        ),
    ]
