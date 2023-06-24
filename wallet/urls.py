from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TransactionViewSet, StockViewSet, TransactionMonthYearViewSet, SummaryTransactionViewSet, TransactionStockView

router = DefaultRouter()
router.register(r'transactions', TransactionViewSet, basename='transaction')
router.register(r'transactions-month-year', TransactionMonthYearViewSet, basename='transaction-month-year')
router.register(r'transactions-stock', TransactionStockView, basename='transaction-stock')
router.register(r'transactions-summary', SummaryTransactionViewSet, basename='transaction-summary')
router.register(r'stocks', StockViewSet , basename='stock')

urlpatterns = [    
    path('', include(router.urls)),
]
