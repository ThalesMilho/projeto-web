from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from .serializer import UserSerializer, CustomTokenObtainPairSerializer 
from rest_framework_simplejwt.views import TokenObtainPairView

class RegisterView(APIView):
    permission_classes = [AllowAny] 

    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            # Retorna 201 Created e os dados (sem a senha)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        # Retorna 400 Bad Request e explica o erro (ex: "CPF já existe")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CustomLoginView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer