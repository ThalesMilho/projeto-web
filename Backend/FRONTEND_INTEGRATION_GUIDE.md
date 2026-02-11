# 🚀 FRONTEND INTEGRATION GUIDE
## Backend API v2.0 - Complete Integration Handbook

**Version:** 2.0.0  
**Last Updated:** 2026-02-11  
**Backend Team:** Senior Technical Lead  
**Target Audience:** Frontend Development Team  

---

## 🚨 **CRITICAL BREAKING CHANGES**

### **⚠️ MONEY AS INTEGER MIGRATION**
**THIS IS A BREAKING CHANGE - READ CAREFULLY**

**Before (Old API):**
```json
{
  "valor": 10.50,     // ❌ DECIMAL - NO LONGER SUPPORTED
  "amount": 25.00     // ❌ DECIMAL - NO LONGER SUPPORTED
}
```

**After (New API v2.0):**
```json
{
  "valor": 1050,      // ✅ INTEGER - CENTS ONLY
  "amount": 2500       // ✅ INTEGER - CENTS ONLY
}
```

**Migration Required:**
- **All money inputs** must be converted to cents (multiply by 100)
- **All money outputs** are provided in both formats for flexibility
- **Validation errors** will occur for decimal inputs

---

## 🔑 **AUTH & SECURITY**

### **Authentication Headers**
```http
Authorization: Bearer <JWT_TOKEN>
Content-Type: application/json
```

### **Token Management**
- **Access Token Lifetime:** 15 minutes
- **Refresh Token Lifetime:** 7 days
- **Token Refresh Endpoint:** `POST /api/accounts/token/refresh/`

### **Token Expiration Handling**
```json
// 401 Response - Token Expired
{
  "detail": "Given token not valid for any token type",
  "code": "token_not_valid"
}

// 403 Response - Insufficient Permissions
{
  "detail": "You do not have permission to perform this action."
}
```

### **CORS Configuration**
**Frontend domains must be whitelisted in backend:**
```bash
# Environment Variables Required
CORS_ALLOWED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
CORS_ALLOW_CREDENTIALS=true
```

---

## 💰 **MONEY HANDLING**

### **INPUTS (Send as Integer Cents)**

#### **Deposits**
```http
POST /api/accounts/depositar/
{
  "valor": 1000,  // R$ 10,00
  "metodo": "pix"
}
```

#### **Withdrawals**
```http
POST /api/accounts/saque/
{
  "valor": 5000,  // R$ 50,00
  "chave_pix": "user@pix.com"
}
```

#### **Betting**
```http
POST /api/games/apostas/
{
  "valor": 500,   // R$ 5,00
  "palpites": ["1234"],
  "sorteio": 1
}
```

### **OUTPUTS (Both Formats Available)**

#### **User Balance**
```json
{
  "saldo_cents": 10000,     // Integer - for calculations
  "saldo": 100.00           // Decimal - for display
}
```

#### **Transaction History**
```json
{
  "valor": 5.00,            // Decimal - already converted
  "valor_premio": 1500.00   // Decimal - already converted
}
```

### **Validation Rules**
- **Deposit Minimum:** R$ 1,00 (100 cents)
- **Withdrawal Minimum:** R$ 10,00 (1000 cents)
- **Bet Minimum:** R$ 1,00 (100 cents)

---

## 📋 **ENUM DICTIONARIES**

### **User Types**
```json
"tipo_usuario": "JOGADOR"    // Regular player
"tipo_usuario": "AFILIADO"   // Affiliate
"tipo_usuario": "ADMIN"      // Administrator
```

### **Payment Status**
```json
"status": "PENDENTE"         // Pending
"status": "APROVADO"        // Approved
"status": "RECUSADO"         // Rejected/Failed
"status": "CANCELADO"        // Cancelled
"status": "EM_ANALISE"       // Under Analysis (Compliance)
"status": "PROCESSANDO"      // Processing Payment
```

### **Payment Types**
```json
"tipo": "DEPOSITO"           // Credit - Deposit
"tipo": "SAQUE"             // Debit - Withdrawal
"tipo": "APOSTA"            // Debit - Bet
"tipo": "PREMIO"            // Credit - Prize
"tipo": "ESTORNO"           // Credit - Refund
"tipo": "BONUS"             // Credit - Bonus
"tipo": "COMISSAO"          // Credit - Commission
```

### **Bet Status**
```json
"status": "PENDENTE"         // Pending draw
"status": "GANHOU"           // Won
"status": "PERDEU"           // Lost
"status": "CANCELADA"        // Cancelled
```

### **Game Types**
```json
"tipo": "BICHO"             // Traditional Bicho
"tipo": "LOTINHA"           // Lotinha
"tipo": "QUININHA"          // Quininha
"tipo": "SENINHA"           // Seninha
"tipo": "LOTERIAS"          // Lotteries
"tipo": "LOTO"              // Loto
```

### **Draw Times**
```json
"horario": "PTM"            // 11:30
"horario": "PT"             // 14:30
"horario": "PTV"            // 16:30
"horario": "FED"            // 19:00 (Federal)
"horario": "COR"            // 21:30 (Corujinha)
```

---

## 🐛 **ERROR SHAPES**

### **Validation Errors (400)**
```json
{
  "valor": ["Valor mínimo de depósito é R$ 1,00 (100 centavos)."],
  "palpites": ["O palpite é obrigatório."],
  "tipo_jogo": ["Modalidade inválida ou não encontrada para o código 'X'."]
}
```

### **Authentication Errors (401)**
```json
{
  "detail": "Given token not valid for any token type",
  "code": "token_not_valid"
}
```

### **Permission Errors (403)**
```json
{
  "detail": "You do not have permission to perform this action."
}
```

### **Not Found Errors (404)**
```json
{
  "detail": "Not found."
}
```

### **Server Errors (500)**
```json
{
  "detail": "Erro interno do servidor."
}
```

### **Business Logic Errors**
```json
{
  "detail": "Saldo insuficiente."
}
{
  "detail": "Este sorteio já está fechado."
}
{
  "detail": "Rollover pendente."
}
```

---

## 📅 **FORMATS & STANDARDS**

### **Date/Time**
- **Format:** ISO 8601 UTC
- **Example:** `"2026-02-11T14:30:00Z"`
- **Timezone:** All timestamps in UTC

### **Pagination**
- **Type:** PageNumberPagination
- **Default Page Size:** 20
- **Max Page Size:** 1000
- **Query Parameters:** `?page=2&page_size=50`

**Response Structure:**
```json
{
  "count": 150,
  "next": "http://api.example.com/accounts/transactions/?page=3",
  "previous": "http://api.example.com/accounts/transactions/?page=1",
  "results": [
    {
      "id": 1,
      "valor": 100.00,
      "criado_em": "2026-02-11T14:30:00Z"
    }
  ]
}
```

### **Rate Limiting**
- **Anonymous Users:** 10 requests/hour
- **Authenticated Users:** 1000 requests/hour
- **Headers:** `X-RateLimit-Limit`, `X-RateLimit-Remaining`

---

## 🔗 **ENDPOINT SUMMARY**

### **Authentication**
```http
POST /api/accounts/token/           # Login
POST /api/accounts/token/refresh/   # Refresh token
POST /api/accounts/logout/          # Logout
```

### **User Management**
```http
GET  /api/accounts/me/             # Current user profile
PUT  /api/accounts/me/             # Update profile
POST /api/accounts/register/        # Register new user
```

### **Financial Operations**
```http
POST /api/accounts/depositar/      # Create deposit
POST /api/accounts/saque/          # Request withdrawal
GET  /api/accounts/transactions/   # Transaction history
GET  /api/accounts/dashboard/       # Financial dashboard
```

### **Gaming Operations**
```http
GET  /api/games/sorteios/         # Available draws
POST /api/games/apostas/          # Place bet
GET  /api/games/apostas/          # Bet history
GET  /api/games/modalidades/       # Game modalities
```

### **Documentation**
```http
GET /api/schema/                  # OpenAPI JSON
GET /api/docs/                    # Swagger UI
GET /api/redoc/                   # Reoc UI
```

---

## 🛠 **INTEGRATION CHECKLIST**

### **Pre-Launch Checklist**
- [ ] **Money Conversion:** All inputs converted to cents (multiply by 100)
- [ ] **CORS Whitelist:** Frontend domain added to `CORS_ALLOWED_ORIGINS`
- [ ] **Token Refresh:** Implement automatic token refresh logic
- [ ] **Error Handling:** Handle all error shapes correctly
- [ ] **Pagination:** Implement pagination for list endpoints
- [ ] **Date Parsing:** Handle ISO 8601 UTC timestamps

### **Testing Checklist**
- [ ] **Deposit Flow:** Test with minimum/maximum amounts
- [ ] **Withdrawal Flow:** Test with valid/invalid PIX keys
- [ ] **Betting Flow:** Test with various game types
- [ ] **Token Expiry:** Test refresh token flow
- [ ] **Error Scenarios:** Test all error response shapes
- [ ] **Pagination:** Test large dataset handling

### **Production Checklist**
- [ ] **Environment Variables:** Set CORS origins
- [ ] **Rate Limiting:** Monitor rate limit headers
- [ ] **Error Monitoring:** Implement error tracking
- [ ] **Performance:** Monitor response times
- [ ] **Security:** Validate all inputs on frontend

---

## 🚨 **COMMON INTEGRATION PITFALLS**

### **❌ DON'T DO THIS**
```javascript
// WRONG - Sending decimals
const depositData = {
  valor: 10.50  // This will fail validation
};

// WRONG - Not handling token refresh
// Token expires, user gets logged out

// WRONG - Assuming money format
const balance = response.data.saldo; // This is already converted
```

### **✅ DO THIS INSTEAD**
```javascript
// CORRECT - Sending cents
const depositData = {
  valor: 1050  // R$ 10,50 in cents
};

// CORRECT - Token refresh handling
if (error.response?.status === 401) {
  await refreshToken();
  retryRequest();
}

// CORRECT - Choose appropriate balance format
const balanceForDisplay = response.data.saldo;      // 100.00
const balanceForCalculations = response.data.saldo_cents; // 10000
```

---

## 📞 **SUPPORT & CONTACT**

### **Backend Team Contacts**
- **Technical Lead:** [Contact Info]
- **API Documentation:** http://api.yourdomain.com/api/docs/
- **Support Channel:** [Slack/Discord/Email]

### **Emergency Contacts**
- **Production Issues:** [Emergency Contact]
- **Security Issues:** [Security Contact]

---

## 📝 **CHANGE LOG**

### **v2.0.0 (2026-02-11)**
- ⚠️ **BREAKING:** Money fields now require integer cents
- ✨ **NEW:** Dual balance format (cents + decimal)
- 🔒 **SECURITY:** Enhanced CORS configuration
- 📚 **DOCS:** Complete API documentation overhaul
- 🐛 **FIX:** Consistent error response shapes

---

**Integration Status:** 🟢 **READY FOR DEVELOPMENT**  
**Support Level:** 🟢 **FULL SUPPORT**  
**Documentation:** 🟢 **COMPLETE**  

*This guide will be updated with each API version. Please check for updates regularly.*
