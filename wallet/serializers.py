from rest_framework import serializers
from .models import Stock, Transaction, validate_code
from datetime import datetime, timezone

class StockSerializer(serializers.ModelSerializer):
    code = serializers.CharField(
        max_length=6,
        validators=[validate_code],
        error_messages={
            'invalid': 'O código deve ter 4 letras maiúsculas seguidas de um ou dois números.'
        }
    )
    # aplicar formatação personalizada
    cnpj = serializers.SerializerMethodField()

    class Meta:
        model = Stock
        fields = ['id','code', 'name_enterprise', 'cnpj']
   
   #formatar a exibição do cnpj: XX.XXX.XXX/XXXX-XX
    def get_cnpj(self, obj):
        cnpj = obj.cnpj
        if cnpj:
            cnpj = '{}.{}.{}/{}-{}'.format(cnpj[:2], cnpj[2:5], cnpj[5:8], cnpj[8:12], cnpj[12:14])
        return cnpj

#serializer CRUD
class TransactionSerializer(serializers.ModelSerializer):
    investor = serializers.HiddenField(default=serializers.CurrentUserDefault())
    date_done = serializers.DateField(default=datetime.now().date)
    stock_code = serializers.CharField(write_only=True)  
    stock = serializers.ReadOnlyField(source='stock.code')  
    total_operation = serializers.SerializerMethodField()

    class Meta:
        model = Transaction
        fields = (
            'id',
            'stock',
            'investor',
            'quantity_stock',
            'unite_price',
            'type_of',
            'brokerage',
            'date_done',
            'total_operation',
            'stock_code',  
        )

    def create(self, validated_data):
        stock_code = validated_data.pop('stock_code', None)  
        stock = Stock.objects.get(code=stock_code)
        validated_data['stock'] = stock 
        validated_data['date_done'] = datetime.now().date()
        return super().create(validated_data)

    def update(self, instance, validated_data):
        stock_code = validated_data.pop('stock_code', None)
        if stock_code:
            stock = Stock.objects.get(code=stock_code)
            instance.stock = stock
        return super().update(instance, validated_data)

    def get_total_operation(self, obj):
        return str(obj.value_total_transaction())
    
#Serializer view
class TransactionSerializerView(serializers.ModelSerializer):
    stock_code = serializers.CharField(read_only=True)
    investor = serializers.PrimaryKeyRelatedField(
        read_only=True,
        default=serializers.CurrentUserDefault()
    )
    date_done = serializers.DateField()
    total_operation = serializers.DecimalField(max_digits=10, decimal_places=2,read_only=True)
    average_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    profit_loss = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    


    class Meta:
        model = Transaction
        fields = ['id', 'stock_code', 'investor','quantity_stock', 'unite_price', 'type_of', 'brokerage','date_done', 'total_operation', 'average_price', 'profit_loss']
        read_only_fields = ['total_operation', 'stock_code']


    def create(self, validated_data):
        stock_code = validated_data.pop('stock_code')
        stock = Stock.objects.get(code=stock_code)
        validated_data['stock'] = stock
        validated_data['date_done'] = timezone.now()
        return super().create(validated_data)
