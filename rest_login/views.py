from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import authenticate
from .serializers import RegisterSerializer, CustomTokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from .models import AuthLog
from django.contrib.auth.models import User

@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    serializer = RegisterSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class EmailTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)

        # If login is successful, log it
        if response.status_code == 200:
            user = User.objects.get(email=request.data.get('email'))
            ip = request.META.get('REMOTE_ADDR')
            AuthLog.objects.create(user=user, action='login', ip_address=ip)

        return response


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_view(request):
    AuthLog.objects.create(user=request.user, action='logout', ip_address=request.META.get('REMOTE_ADDR'))
    return Response({"message": "Logged out (client should delete token)"})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard(request):
    return Response({
        "message": f"Hello {request.user.username}, you're authenticated!"
    })


