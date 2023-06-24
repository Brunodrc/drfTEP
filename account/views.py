from .models import Investor
from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import AllowAny
from .serializers import InvestorSerializer, UserSerializer

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

# class Login(APIView):
#     def post(self, request):
#         try:
#             data = request.data
#             serializer = LoginSerializer(data=data)
#             if serializer.is_valid():
#                 email = serializer.data['email']
#                 password = serializer.data['password']
#                 user = authenticate(email =email, password = password)

#                 if user is None:
#                     return Response({
#                         'status':400,
#                         'msg': "email ou senha invalido.",
#                         'data': {} 
#                     })
#                 refresh = RefreshToken.for_user(user)

#                 return{
#                     'refresh': str(refresh),
#                     'access': str(refresh.access_token),
#                 }
#             return Response({
#                 'status':400,
#                 'msg': "algum erro",
#                 'data': serializer.errors
#             })
#         except Exception as e:
#             print(e)
