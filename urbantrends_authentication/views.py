from django.shortcuts import render
from django.http import HttpResponse
from .serializers import UserSerializers, UserSerializer, PasswordResetRequestSerializer, PasswordResetConfirmSerializer
from django.contrib.auth.models import User
from rest_framework.decorators import api_view, throttle_classes
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import authenticate
from django.contrib.auth.hashers import check_password
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.views import APIView
from .throttles import LoginRateThrottle
from .utils.emails import send_email
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.template.loader import render_to_string
from .utils.google import verify_google_token


# Create your views here.

def test_mail(request):
    status = send_email()
    return HttpResponse(f"email response: {status}")


def hello(request):

    return HttpResponse("Welcome to the urbantrends authentication app")


@api_view(['POST'])
def createUser(request):
    if request.method == 'POST':
        serializer = UserSerializers(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            html_content = render_to_string("emails/Urbantrends-dev/email.html", {"user": user})
            email_status = send_email(
                subject="Welcome to Urbantrends!",
                to_emails=[user.email],
                html_content=html_content
            )
            return Response({"user created": serializer.data, "email_status": email_status}, status=status.HTTP_201_CREATED)
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

@api_view(['POST'])
def request_password_reset(request):
    """Send password reset email with tokenized link"""
    serializer = PasswordResetRequestSerializer(data=request.data)
    if serializer.is_valid():
        email = serializer.validated_data['email']
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

        # Generate token & uid
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)

        # Construct reset link (example: frontend URL)
        reset_link = f"https://urbantrends.dev/reset-password/{uid}/{token}/"

        # Send email
        email_status = send_email(
            subject="Urbantrends Password Reset",
            to_emails=[user.email],
            html_content=f"<p>Click the link below to reset your password:</p>"
                         f"<a href='{reset_link}'>Reset Password</a>"
        )
        return Response({"message": "Password reset email sent", "status": email_status})

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def confirm_password_reset(request):
    """Set new password using token & uid"""
    serializer = PasswordResetConfirmSerializer(data=request.data)
    if serializer.is_valid():
        uid = request.data.get("uid")
        token = serializer.validated_data["token"]
        new_password = serializer.validated_data["new_password"]

        try:
            user_id = force_str(urlsafe_base64_decode(uid))
            user = User.objects.get(pk=user_id)
        except (User.DoesNotExist, ValueError, TypeError):
            return Response({"error": "Invalid link"}, status=status.HTTP_400_BAD_REQUEST)

        if not default_token_generator.check_token(user, token):
            return Response({"error": "Invalid or expired token"}, status=status.HTTP_400_BAD_REQUEST)

        # Set new password
        user.set_password(new_password)
        user.save()

        return Response({"message": "Password has been reset successfully"})

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class googleAuthView(APIView):
    permission_classes = []


    def post(self, request):
        token = request.data.get("token")

        if not token:
            return Response(
                {"error": "Token missing"},
                status=status.HTTP_400_BAD_REQUEST
            )

        google_data = verify_google_token(token)

        if not google_data:
            return Response(
                {"error": "Invalid Google token"},
                status=status.HTTP_400_BAD_REQUEST
            )

        email = google_data["email"]
        username = email.split("@")[0]

        user, created = User.objects.get_or_create(
            email=email,
            defaults={"username": username}
        )

        refresh = RefreshToken.for_user(user)

        return Response({
            "access": str(refresh.access_token),
            "refresh": str(refresh),
            "user": {
                "username": user.username,
                "email": user.email
            }
        })