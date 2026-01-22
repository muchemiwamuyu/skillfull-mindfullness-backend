from django.shortcuts import render
from django.http import HttpResponse
from rest_framework import status
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.exceptions import ValidationError
from .models import DevProject
from .serializers import DevProjectSerializer
# Create your views here.

def hello(request):
    return HttpResponse("Hello from Urbantrends dev projects!")

class DevProjectView(ModelViewSet):
    serializer_class = DevProjectSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def get_queryset(self):
        return DevProject.objects.filter(created_by=self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(
            data=request.data,
            context={"request": request}
        )

        try:
            serializer.is_valid(raise_exception=True)
            project = serializer.save(created_by=request.user)

        except ValidationError as e:
            return Response(
                {
                    "status": "error",
                    "message": "Validation failed",
                    "errors": e.detail,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        except IntegrityError:
            return Response(
                {
                    "status": "error",
                    "message": "Duplicate project detected",
                    "errors": {
                        "title": ["You already have a project with this title."]
                    },
                },
                status=status.HTTP_409_CONFLICT,
            )

        except Exception:
            return Response(
                {
                    "status": "error",
                    "message": "Something went wrong. Please try again.",
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        return Response(
            {
                "status": "success",
                "message": f"Hello {request.user.username}, you have successfully created the following project.",
                "project": DevProjectSerializer(project).data,
            },
            status=status.HTTP_201_CREATED,
        )

  
class DevProjectList(ReadOnlyModelViewSet):
    serializer_class = DevProjectSerializer
    queryset = DevProject.objects.all().order_by("-created_at")
    permission_classes = [IsAuthenticatedOrReadOnly]
    authentication_classes = [JWTAuthentication]





