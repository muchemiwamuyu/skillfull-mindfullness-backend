from django.urls import path
from .views import hello, createUser, loginUser, test_mail
from rest_framework_simplejwt.views import TokenRefreshView
urlpatterns = [
    path('greetings/', hello, name='Hello from urbantrends'),
    path('user-create/', createUser, name="Create urbantrends user"),
    path('login-user/', loginUser, name='Login urbantrends user'),
    path('test-mail/', test_mail, name='test mail'),
    path('token/refresh', TokenRefreshView.as_view(), name='Token refresh')
]