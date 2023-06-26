from django.urls import path, include
from rest_framework import routers
from account.views import RegisterViewSet, RegisterUser
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
) 

router = routers.DefaultRouter()
router.register(r'register', RegisterViewSet, basename='registerAuth')

urlpatterns = [
    path('', include(router.urls)),
    path('login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    # path('login/', CustomTokenObtainPairView.as_view(), name='token_obtain_custom'),
    path('login/refreshtoken', TokenRefreshView.as_view(), name='token_refresh'),
    # path('login/refreshtoken', CustomTokenRefreshView.as_view(), name='token_custom'),
    path('signup/', RegisterUser.as_view(), name='signup'),
]

