from rest_framework import viewsets, permissions
from rest_framework.response import Response
from .models import Stock, Transaction
from .serializers import StockSerializer, TransactionSerializer
from rest_framework import filters
from django.db.models import Q


class StockViewSet(viewsets.ModelViewSet):
    serializer_class = StockSerializer
    permission_classes = [permissions.IsAuthenticated]

    queryset = Stock.objects.all()

# métodos para remover caracteres especiais do CNPJ
    def create(self, request, *args, **kwargs):
        request.data['cnpj'] = ''.join(filter(str.isdigit, request.data.get('cnpj')))
        return super().create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        request.data['cnpj'] = ''.join(filter(str.isdigit, request.data.get('cnpj')))
        return super().update(request, *args, **kwargs)

#view com os métodos create, read, update, delete,
class TransactionViewSet(viewsets.ModelViewSet):
    serializer_class = TransactionSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.OrderingFilter]
    ordering = ['date_done']

    def get_queryset(self):
        investor = self.request.user.investor
        queryset = Transaction.objects.filter(investor=investor).order_by('date_done')
        
        for transaction in queryset:
            transaction.total_operation = transaction.value_total_transaction()
             
        return queryset

    def perform_create(self, serializer):

        serializer.save(investor=self.request.user.investor)
        return Response({'message': 'Transação criada com sucesso.', 
                         'transaction': serializer.data}, status=201)

#  views apenas apenas para leitura:

# lista trasações de um unica ação  
class TransactionStockView(viewsets.ReadOnlyModelViewSet):
    serializer_class = TransactionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        investor = self.request.user.investor
        stock_code = self.request.query_params.get('stock_code')
        
        queryset = Transaction.objects.filter(
            investor=investor,
            stock__code__icontains=stock_code
        )
        stocks_summary = {}
        for transaction in queryset:
            stock_id = transaction.stock_id
            transaction.total_operation = transaction.value_total_transaction()

            # Obter ou inicializar as informações da ação no dicionário de resumo
            stock_summary = stocks_summary.get(stock_id, {
                'transactions': [],
                'total_quantity': 0,
                'total_value': 0,
                'average_price': 0,
                'profit_loss': 0,
                'total_profit_loss': 0,
            })
            stock_summary['transactions'].append(transaction)

            # Calcular o preço médio
            total_quantity = stock_summary['total_quantity']
            total_value = stock_summary['total_value']
            new_quantity = total_quantity + transaction.quantity_stock
            new_value = (total_quantity * stock_summary['average_price'] + transaction.buy_value()) / new_quantity
            stock_summary['average_price'] = new_value

            # Atualizar o valor total e lucro/prejuízo
            stock_summary['total_quantity'] = new_quantity
            stock_summary['total_value'] += transaction.buy_value()

            if transaction.type_of == 'V':
                # Calcular o lucro/prejuízo somente se for uma venda
                stock_summary['profit_loss'] += transaction.total_operation - (transaction.quantity_stock * stock_summary['average_price'])

            # Atualizar as informações da ação no dicionário de resumo
            stocks_summary[stock_id] = stock_summary
            print(f'REsultado ---> {stock_summary}')
        
        #o resumo das infromações obtidas será colocado aqui
        summary_list = []

        # Iterar sobre as transações e adicionar os dados resumidos à lista
        for transaction in queryset:
            stock_id = transaction.stock_id
            stock_summary = stocks_summary[stock_id]
            

            # Criar um dicionário com os dados resumidos
            summary_data = {
                'id': transaction.id,
                'stock_code': transaction.stock.code,
                'investor': transaction.investor,
                'quantity_stock': transaction.quantity_stock,
                'unite_price': transaction.unite_price,
                'type_of': transaction.type_of,
                'brokerage': transaction.brokerage,
                'date_done': transaction.date_done,
                'total_operation': transaction.total_operation,
                'total_value': stock_summary['total_value'],
                'average_price': stock_summary['average_price'],
                'profit_loss': stock_summary['profit_loss'],
            }
           
           
            # Adicionar o dicionário à lista
            summary_list.append(summary_data)
        print(f'Lista obtida: {summary_list}')
        return summary_list
        # return queryset

#lista as transações de mes e ano escolhidas
class TransactionMonthYearViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = TransactionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        investor = self.request.user.investor
        month = self.request.query_params.get('month')
        year = self.request.query_params.get('year')

        # Verificar se os parâmetros month e year foram fornecidos
        if not month or not year:
            return Transaction.objects.none()

        # Converter month e year para valores inteiros
        try:
            month = int(month)
            year = int(year)
        except ValueError:
            return Transaction.objects.none()

        # Filtrar as transações pelo investidor, mês e ano
        queryset = Transaction.objects.filter(
            Q(investor=investor),
            Q(date_done__month=month, date_done__year=year)
        )
        return queryset

# lista as transações e informa o preço médio, valor total e lucro/prejuízo para cada ação e total lucro de todas as transaçẽes
class SummaryTransactionViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = TransactionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        investor = self.request.user.investor
        queryset = Transaction.objects.filter(investor=investor)

        # Calcular o preço médio, valor total e lucro/prejuízo para cada ação
        stocks_summary = {}
        for transaction in queryset:
            stock_id = transaction.stock_id
            transaction.total_operation = transaction.value_total_transaction()

            # Obter ou inicializar as informações da ação no dicionário de resumo
            stock_summary = stocks_summary.get(stock_id, {
                'transactions': [],
                'total_quantity': 0,
                'total_value': 0,
                'average_price': 0,
                'profit_loss': 0,
                'total_profit_loss': 0,
            })
            stock_summary['transactions'].append(transaction)

            # Calcular o preço médio
            total_quantity = stock_summary['total_quantity']
            total_value = stock_summary['total_value']
            new_quantity = total_quantity + transaction.quantity_stock
            new_value = (total_quantity * stock_summary['average_price'] + transaction.buy_value()) / new_quantity
            stock_summary['average_price'] = new_value

            # Atualizar o valor total e lucro/prejuízo
            stock_summary['total_quantity'] = new_quantity
            stock_summary['total_value'] += transaction.buy_value()

            if transaction.type_of == 'V':
                # Calcular o lucro/prejuízo somente se for uma venda
                stock_summary['profit_loss'] += transaction.total_operation - (transaction.quantity_stock * stock_summary['average_price'])

            # Atualizar as informações da ação no dicionário de resumo
            stocks_summary[stock_id] = stock_summary

        # Calcular o lucro total de todas as ações
        total_profit_loss = sum(stock_summary['profit_loss'] for stock_summary in stocks_summary.values())
        # Lista para armazenar os dados resumidos das transações
        summary_list = []

        # Iterar sobre as transações e adicionar os dados resumidos à lista
        for transaction in queryset:
            stock_id = transaction.stock_id
            stock_summary = stocks_summary[stock_id]
            

            # Criar um dicionário com os dados resumidos
            summary_data = {
                'id': transaction.id,
                'stock_code': transaction.stock.code,
                'investor': transaction.investor,
                'quantity_stock': transaction.quantity_stock,
                'unite_price': transaction.unite_price,
                'type_of': transaction.type_of,
                'brokerage': transaction.brokerage,
                'date_done': transaction.date_done,
                'total_operation': transaction.total_operation,
                'total_value': stock_summary['total_value'],
                'average_price': stock_summary['average_price'],
                'profit_loss': stock_summary['profit_loss'],
            }
           
           
            # Adicionar o dicionário à lista
            summary_list.append(summary_data)
        print(f'Lista obtida: {summary_list}')
        return summary_list
