from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from .serializer import UserSerializer, CustomTokenObtainPairSerializer 
from rest_framework_simplejwt.views import TokenObtainPairView

# --- MOCK DE LOGIN (Simulação para o Front testar) ---
#class LoginView(APIView):
#   def post(self, request):
#       return Response({
#            "token": "token-falso-de-teste", 
#            "user_id": 1,
#            "message": "Login simulado (MOCK) com sucesso!"
#S        }, status=status.HTTP_200_OK)

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