from django.shortcuts import render
from django.http import HttpResponse
from .serializers import UserSerializers, UserSerializer
from django.contrib.auth.models import User
from rest_framework.decorators import api_view, throttle_classes
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import authenticate
from django.contrib.auth.hashers import check_password
from rest_framework_simplejwt.tokens import RefreshToken
from .throttles import LoginRateThrottle
from .utils.emails import send_email


# Create your views here.

def test_mail(request):
    status = send_email()
    return HttpResponse(f"send grid response: {status}")


def hello(request):

    return HttpResponse("Welcome to the urbantrends authentication app")


@api_view(['POST'])
def createUser(request):
    if request.method == 'POST':
        serializer = UserSerializers(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"user created": serializer.data}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    return Response({"error": "method not allowed"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

@api_view(['POST'])
@throttle_classes([LoginRateThrottle])
def loginUser(request):
    username = request.data.get("username")
    password = request.data.get("password")

    if not username or not password:
        return Response(
            {"error": "Invalid credentials"},
            status=status.HTTP_400_BAD_REQUEST
        )

    user = authenticate(
        request,
        username=username,
        password=password
    )

    if user is None:
        return Response(
            {"error": "Invalid credentials"},
            status=status.HTTP_401_UNAUTHORIZED
        )
    
    refresh = RefreshToken.for_user(user)

    # Serialize user data
    user_data = UserSerializer(user).data

    return Response(
        {
            "user": user_data,           # contains username and email
            "access": str(refresh.access_token),
            "refresh": str(refresh),
        },
        status=status.HTTP_200_OK
    )