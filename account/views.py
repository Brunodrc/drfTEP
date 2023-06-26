from .models import Investor
from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import AllowAny
from .serializers import InvestorSerializer, UserSerializer
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView


class RegisterUser(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        user_serializer = UserSerializer(data=request.data)
        user_serializer.is_valid(raise_exception=True)
        user = user_serializer.save()
        
        investor_data = {
            'user': user.id,
            'risk_profile': request.data.get('risk_profile')
        }
        
        investor_serializer = InvestorSerializer(data=investor_data)
        investor_serializer.is_valid(raise_exception=True)
        investor_serializer.save()
        

        refresh = RefreshToken.for_user(user)

        return Response({
            'access_token': str(refresh.access_token),
            'refresh_token': str(refresh),
            'user': user_serializer.data,
            'investor': investor_serializer.data,
            'error': user_serializer.errors,
            
        })


class RegisterViewSet(viewsets.ModelViewSet):
    queryset = Investor.objects.all()
    serializer_class = InvestorSerializer


# # views personalizadas
# class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
#     @classmethod
#     def get_token(cls, user):
#         token = super().get_token(user)

#         # Adicione os dados do usuário ao payload do token
#         if hasattr(user, 'name'):
#             token['id'] = user.id
#             token['name'] = user.name
#             token['email'] = user.email
#             if hasattr(user, 'investor'):
#                 token['risk_profile'] = user.investor.risk_profile

#         return token

# class CustomTokenObtainPairView(TokenObtainPairView):
#     serializer_class = CustomTokenObtainPairSerializer

#     def post(self, request, *args, **kwargs):
#         response = super().post(request, *args, **kwargs)
#         serializer = self.get_serializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
#         user = serializer.user

#         if request.user.is_authenticated:
#             # Adiciona os dados do usuário à resposta
#             user = request.user
#             data = {
#                 'id': user.id,
#                 'name': user.name,
#                 'email': user.email,
#                 # 'risk_profile': user.investor.risk_profile,
#                 # 'access': response.data['access'],
#                 # 'refresh': response.data['refresh']
#             }
#             if hasattr(user, 'investor'):
#                 data['risk_profile'] = user.investor.risk_profile

#             data['access'] = response.data['access']

#             response.data.update(data)
#         return response

# class CustomTokenRefreshView(TokenRefreshView):
#     def post(self, request, *args, **kwargs):
#         response = super().post(request, *args, **kwargs)

#         # Verifique se o usuário está autenticado
#         if request.user.is_authenticated:
#             user = request.user

#             # Adicione os dados do usuário à resposta
#             data = {
#                 'id': user.id,
#                 'name': user.name,
#                 'email': user.email,
#             }

#             if hasattr(user, 'investor'):
#                 data['risk_profile'] = user.investor.risk_profile

#             response.data.update(data)

#         return response