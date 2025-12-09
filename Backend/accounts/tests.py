from django.test import TestCase
from django.contrib.auth import get_user_model

class AccountsTests(TestCase):
    def test_criar_usuario_com_cpf(self):
        """
        Teste se o CustomUserManager cria o usuário corretamente
        usando o CPF como identificador.
        """
        User = get_user_model()
        cpf = "12345678900"
        senha = "senha_segura_123"
        
        # Criação
        user = User.objects.create_user(
            cpf_cnpj=cpf, 
            password=senha, 
            nome_completo="Teste da Silva"
        )

        # Verificações
        self.assertEqual(user.cpf_cnpj, cpf)
        self.assertEqual(user.username, cpf) # Garante que a tua lógica de username=cpf funcionou
        self.assertTrue(user.check_password(senha)) # Garante que a senha foi hashada
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)
        self.assertEqual(float(user.saldo), 0.00)

    def test_criar_superuser(self):
        """Teste se o Superusuário ganha as permissões certas"""
        User = get_user_model()
        admin = User.objects.create_superuser(
            cpf_cnpj="99999999999", 
            password="admin", 
            nome_completo="Admin Chefe"
        )
        self.assertTrue(admin.is_staff)
        self.assertTrue(admin.is_superuser)