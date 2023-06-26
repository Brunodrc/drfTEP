from django.db import models
from account.models import Investor
from datetime import datetime
from django.core.exceptions import ValidationError
import re

def validate_code(value):

    pattern = r'^[A-Z]{4}\d{1,2}$'
    if not re.match(pattern, value):
        raise ValidationError('O código deve ter 4 letras maiúsculas seguidas de um ou dois números.')


class Stock(models.Model):
    code = models.CharField(max_length=6, unique=True, validators=[validate_code])
    name_enterprise = models.CharField(max_length=35)
    cnpj = models.CharField(max_length=18)

    def __str__(self):
        return "{} - {}".format(self.code, self.name_enterprise)

class Transaction(models.Model):
    TYPE_OF_TRANSACTION = (
        ('C', 'Compra'),
        ('V', 'Venda'),
    )
    date_done = models.DateField(default=datetime.now, blank=True)
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE)
    quantity_stock = models.PositiveIntegerField()
    unite_price = models.DecimalField(max_digits=8, decimal_places=2)
    type_of = models.CharField(max_length=1, choices=TYPE_OF_TRANSACTION)
    brokerage = models.DecimalField(max_digits=8, decimal_places=2)
    investor = models.ForeignKey(Investor, on_delete=models.CASCADE)

# calcular o valor de compra e venda de ação em uma transação
    def buy_value(self):
        value = self.quantity_stock * self.unite_price 
        return round(value, 2)
    
    def value_total_transaction(self):
        if self.type_of == 'C':
            value_total = self.buy_value() + self.brokerage
        else:
            value_total = self.buy_value() - self.brokerage
        
        return round(value_total, 2)

    def __str__(self):
        return '{}-{}'.format(self.stock,self.type_of)
