# 📚 **DOCUMENTAÇÃO COMPLETA DA API - FRONTEND INTEGRATION**

## **🎯 VISÃO GERAL**

### **🔗 ENDPOINTS PRINCIPAIS**
```
📋 Schema JSON: http://127.0.0.1:8000/api/schema/
📚 Swagger UI: http://127.0.0.1:8000/api/docs/
📖 Redoc UI: http://127.0.0.1:8000/api/redoc/
```

### **🔒 AUTENTICAÇÃO OBRIGATÓRIA**
- **TODOS os endpoints** precisam de `Authorization: Bearer <token>`
- **Exceções**: `/register/`, `/login/`, `/password-reset/`
- **Token expira**: 1 hora
- **Refresh token**: 1 dia

---

## **👤 ENDPOINTS DE USUÁRIO (ACCOUNTS)**

### **🔐 AUTENTICAÇÃO**
```http
POST /api/accounts/register/
POST /api/accounts/login/
POST /api/accounts/token/refresh/
POST /api/accounts/password-reset/
POST /api/accounts/password-reset-confirm/<uidb64>/<token>/
```

### **👤 PERFIL E DADOS**
```http
GET /api/accounts/me/                    # Dados do usuário logado
GET /api/accounts/meus-movimentos/     # Histórico de transações
```

### **💰 OPERAÇÕES FINANCEIRAS**
```http
POST /api/accounts/depositar/           # Gerar PIX de depósito
POST /api/accounts/saque/               # Solicitar saque
GET /api/accounts/dashboard/            # Dashboard financeiro
GET /api/accounts/relatorios/operacional/  # Relatórios operacionais
GET /api/accounts/relatorios/financeiro/csv/  # Relatório financeiro CSV
```

### **🔧 ENDPOINTS DE TESTE**
```http
GET /api/accounts/test-skalepay/        # Testar conexão SkalePay
POST /api/accounts/webhook/skalepay/    # Webhook SkalePay
```

---

## **🎲 ENDPOINTS DE JOGOS (GAMES)**

### **📊 DADOS PÚBLICOS (Sem autenticação)**
```http
GET /api/games/bichos/                 # Lista de bichos
GET /api/games/cotacoes/               # Cotações atuais
GET /api/games/sorteios/abertos/       # Sorteios abertos
```

### **🎮 REGRAS DOS JOGOS**
```http
GET /api/games/quininha/               # Regras Quinina
GET /api/games/seninha/               # Regras Seninha
GET /api/games/lotinha/               # Regras Lotinha
```

### **🎯 APOSTAS (Com autenticação)**
```http
GET /api/games/apostas/                # Listar apostas do usuário
POST /api/games/apostas/               # Criar nova aposta
GET /api/games/apostas/{id}/           # Detalhes da aposta
PUT /api/games/apostas/{id}/           # Atualizar aposta
DELETE /api/games/apostas/{id}/        # Cancelar aposta
```

### **🏆 APURAÇÃO (Admin)**
```http
POST /api/games/apurar/{id}/           # Apurar sorteio
GET /api/games/comprovante/{id}/       # Imprimir comprovante
```

---

## **🔑 EXEMPLOS DE INTEGRAÇÃO**

### **1. LOGIN E OBTENÇÃO DE TOKEN**
```javascript
// POST /api/accounts/login/
{
  "cpf_cnpj": "70114581150",
  "password": "kurtcobain1010"
}

// RESPOSTA:
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "user": {
    "id": 1,
    "cpf_cnpj": "70114581150",
    "nome_completo": "Admin",
    "saldo": 0
  }
}
```

### **2. USANDO O TOKEN NAS REQUISIÇÕES**
```javascript
// Headers para TODAS as requisições (exceto login/register):
{
  "Authorization": "Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "Content-Type": "application/json"
}
```

### **3. OBTER DADOS DO USUÁRIO**
```javascript
// GET /api/accounts/me/
// RESPOSTA:
{
  "id": 1,
  "cpf_cnpj": "70114581150",
  "nome_completo": "Admin",
  "email": "thmilhomens0@gmail.com",
  "saldo": 0,  // EM CENTAVOS!
  "tipo_usuario": "ADMIN",
  "data_cadastro": "2024-01-01T00:00:00Z"
}
```

### **4. CRIAR APOSTA**
```javascript
// POST /api/games/apostas/
{
  "jogo": 1,
  "sorteio": 1,
  "valor": 1000,  // R$ 10,00 (em centavos)
  "palpites": ["1234", "5678"],
  "modalidade": 1
}

// RESPOSTA:
{
  "id": 123,
  "valor": 1000,
  "valor_premio": 10000,  // R$ 100,00
  "status": "PENDENTE",
  "ganhou": false,
  "criado_em": "2024-01-01T12:00:00Z"
}
```

### **5. DEPOSITAR DINHEIRO**
```javascript
// POST /api/accounts/depositar/
{
  "valor": 5000  // R$ 50,00 (em centavos)
}

// RESPOSTA:
{
  "pix_qrcode": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAA...",
  "pix_copiacola": "00020126580014br.gov.bcb.pix0134...",
  "valor": 5000,
  "expiracao": "2024-01-01T13:00:00Z"
}
```

---

## **💰 REGRAS IMPORTANTES**

### **📏 VALORES MONETÁRIOS**
- **TODOS os valores** são em **CENTAVOS** (inteiros)
- **R$ 1,00** = `100`
- **R$ 10,50** = `1050`
- **R$ 100,00** = `10000`

### **🔢 CPF/CNPJ**
- **Formato**: Apenas números (sem pontos/travessões)
- **Exemplo**: `"12345678901"` (não `"123.456.789-01"`)

### **🎯 STATUS DAS APOSTAS**
- `PENDENTE` - Aguardando sorteio
- `GANHOU` - Apostador ganhou
- `PERDEU` - Apostador perdeu
- `CANCELADA` - Aposta cancelada

---

## **🚨 TRATAMENTO DE ERROS**

### **🔒 AUTENTICAÇÃO**
```javascript
// 401 Unauthorized
{
  "detail": "As credenciais de autenticação não foram fornecidas."
}

// 401 Token expirado
{
  "detail": "O token não é válido para nenhum tipo de token",
  "code": "token_not_valid"
}
```

### **💸 SALDO INSUFICIENTE**
```javascript
// 400 Bad Request
{
  "saldo": ["Saldo insuficiente para realizar esta operação."]
}
```

### **📋 VALIDAÇÃO**
```javascript
// 400 Bad Request
{
  "cpf_cnpj": ["CPF inválido."],
  "valor": ["Valor deve ser positivo."]
}
```

---

## **🔄 REFRESH DE TOKEN**

### **🔄 QUANDO USAR?**
- Quando receber erro `401 Unauthorized`
- Quando o token estiver próximo de expirar

### **🔄 COMO USAR?**
```javascript
// POST /api/accounts/token/refresh/
{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}

// RESPOSTA:
{
  "access": "novo_access_token_aqui",
  "refresh": "novo_refresh_token_aqui"
}
```

---

## **📱 WEBHOOKS**

### **💳 SKALEPAY WEBHOOK**
```http
POST /api/accounts/webhook/skalepay/
Content-Type: application/json
X-Skalepay-Signature: sha256=...

{
  "event": "payment.confirmed",
  "data": {
    "transaction_id": "tx_123456",
    "amount": 5000,
    "status": "paid"
  }
}
```

---

## **🎯 CHECKLIST FINAL DE INTEGRAÇÃO**

### **✅ OBRIGATÓRIO**
- [ ] Implementar sistema de **tokens JWT**
- [ ] **Refresh automático** de tokens
- [ ] Tratamento de **valores em centavos**
- [ ] **Validação de CPF** (apenas números)
- [ ] **Tratamento de erros 401/403**

### **✅ RECOMENDADO**
- [ ] **Cache** de dados públicos (bichos, cotações)
- [ ] **Loading states** para operações financeiras
- [ ] **Confirmação** antes de apostas
- [ ] **Notificações** de mudanças de status

### **✅ SEGURANÇA**
- [ ] **Nunca** armazenar tokens no localStorage
- [ ] **Sempre** usar HTTPS em produção
- [ ] **Validar** respostas da API
- [ ] **Rate limiting** no frontend

---

## **🚀 AMBIENTE DE PRODUÇÃO**

### **🔗 ENDPOINTS PRODUÇÃO**
```
📋 Schema: https://seu-dominio.com/api/schema/
📚 Docs: https://seu-dominio.com/api/docs/
🔐 API: https://seu-dominio.com/api/
```

### **🔒 SEGURANÇA**
- **HTTPS obrigatório**
- **CORS configurado** para seu domínio
- **Rate limiting** ativo
- **Monitoramento** de erros

---

## **🎯 CONCLUSÃO**

**Seu amigo tem TUDO o que precisa para integrar!**

✅ **Documentação completa e funcional**  
✅ **Todos os endpoints documentados**  
✅ **Exemplos práticos**  
✅ **Tratamento de erros**  
✅ **Regras de negócio claras**  

**Ele só precisa acessar http://127.0.0.1:8000/api/docs/ e começar!** 🚀
