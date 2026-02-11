# 🚀 GUIA DE INTEGRAÇÃO DO FRONTEND
## Backend API v2.0 - Manual Completo de Integração

--
## 🚨 **MUDANÇAS CRÍTICAS (BREAKING CHANGES)**

**Antes (API Antiga):**
```json
{
  "valor": 10.50,     // ❌ DECIMAL - NÃO MAIS SUPORTADO
  "amount": 25.00     // ❌ DECIMAL - NÃO MAIS SUPORTADO
}
```

**Depois (Nova API v2.0):**
```json
{
  "valor": 1050,      // ✅ INTEIRO - APENAS CENTAVOS
  "amount": 2500       // ✅ INTEIRO - APENAS CENTAVOS
}
```

**Migração Obrigatória:**
- **Todas as entradas de dinheiro** devem ser convertidas para centavos (multiplicar por 100)
- **Todas as saídas de dinheiro** são fornecidas em ambos os formatos para flexibilidade
- **Erros de validação** ocorrerão para entradas decimais

---

## 🔑 **AUTENTICAÇÃO & SEGURANÇA**

### **Cabeçalhos de Autenticação**
```http
Authorization: Bearer <JWT_TOKEN>
Content-Type: application/json
```

### **Gerenciamento de Token**
- **Tempo de Vida do Access Token:** 15 minutos
- **Tempo de Vida do Refresh Token:** 7 dias
- **Endpoint de Refresh do Token:** `POST /api/accounts/token/refresh/`

### **Tratamento de Expiração de Token**
```json
// Resposta 401 - Token Expirado
{
  "detail": "Given token not valid for any token type",
  "code": "token_not_valid"
}

// Resposta 403 - Permissões Insuficientes
{
  "detail": "You do not have permission to perform this action."
}
```

### **Configuração CORS**
**Domínios Frontend devem ser autorizados na whitelist do backend:**
```bash
# Variáveis de Ambiente Obrigatórias
CORS_ALLOWED_ORIGINS=https://seudominio.com,https://www.seudominio.com
CORS_ALLOW_CREDENTIALS=true
```

---

## 💰 **MANIPULAÇÃO DE DINHEIRO**

### **ENTRADAS (Enviar como Inteiro em Centavos)**

#### **Depósitos**
```http
POST /api/accounts/depositar/
{
  "valor": 1000,  // R$ 10,00
  "metodo": "pix"
}
```

#### **Saques**
```http
POST /api/accounts/saque/
{
  "valor": 5000,  // R$ 50,00
  "chave_pix": "user@pix.com"
}
```

#### **Apostas**
```http
POST /api/games/apostas/
{
  "valor": 500,   // R$ 5,00
  "palpites": ["1234"],
  "sorteio": 1
}
```

### **SAÍDAS (Ambos os Formatos Disponíveis)**

#### **Saldo do Usuário**
```json
{
  "saldo_cents": 10000,     // Inteiro - para cálculos
  "saldo": 100.00           // Decimal - para exibição
}
```

#### **Histórico de Transações**
```json
{
  "valor": 5.00,            // Decimal - já convertido
  "valor_premio": 1500.00   // Decimal - já convertido
}
```

### **Regras de Validação**
- **Mínimo de Depósito:** R$ 1,00 (100 centavos)
- **Mínimo de Saque:** R$ 10,00 (1000 centavos)
- **Mínimo de Aposta:** R$ 1,00 (100 centavos)

---

## 📋 **DICIONÁRIOS DE ENUMS**

### **Tipos de Usuário**
```json
"tipo_usuario": "JOGADOR"    // Jogador Comum
"tipo_usuario": "AFILIADO"   // Afiliado
"tipo_usuario": "ADMIN"      // Administrador
```

### **Status de Pagamento**
```json
"status": "PENDENTE"         // Pendente
"status": "APROVADO"        // Aprovado
"status": "RECUSADO"         // Rejeitado/Falhou
"status": "CANCELADO"        // Cancelado
"status": "EM_ANALISE"       // Em Análise (Compliance)
"status": "PROCESSANDO"      // Processando Pagamento
```

### **Tipos de Pagamento**
```json
"tipo": "DEPOSITO"           // Crédito - Depósito
"tipo": "SAQUE"             // Débito - Saque
"tipo": "APOSTA"            // Débito - Aposta
"tipo": "PREMIO"            // Crédito - Prêmio
"tipo": "ESTORNO"           // Crédito - Reembolso
"tipo": "BONUS"             // Crédito - Bônus
"tipo": "COMISSAO"          // Crédito - Comissão
```

### **Status de Aposta**
```json
"status": "PENDENTE"         // Aguardando Sorteio
"status": "GANHOU"           // Ganhou
"status": "PERDEU"           // Perdeu
"status": "CANCELADA"        // Cancelada
```

### **Tipos de Jogo**
```json
"tipo": "BICHO"             // Bicho Tradicional
"tipo": "LOTINHA"           // Lotinha
"tipo": "QUININHA"          // Quininha
"tipo": "SENINHA"           // Seninha
"tipo": "LOTERIAS"          // Loterias
"tipo": "LOTO"              // Loto
```

### **Horários de Sorteio**
```json
"horario": "PTM"            // 11:30
"horario": "PT"             // 14:30
"horario": "PTV"            // 16:30
"horario": "FED"            // 19:00 (Federal)
"horario": "COR"            // 21:30 (Corujinha)
```

---

## 🐛 **FORMATOS DE ERRO**

### **Erros de Validação (400)**
```json
{
  "valor": ["Valor mínimo de depósito é R$ 1,00 (100 centavos)."],
  "palpites": ["O palpite é obrigatório."],
  "tipo_jogo": ["Modalidade inválida ou não encontrada para o código 'X'."]
}
```

### **Erros de Autenticação (401)**
```json
{
  "detail": "Given token not valid for any token type",
  "code": "token_not_valid"
}
```

### **Erros de Permissão (403)**
```json
{
  "detail": "You do not have permission to perform this action."
}
```

### **Erros de Não Encontrado (404)**
```json
{
  "detail": "Not found."
}
```

### **Erros de Servidor (500)**
```json
{
  "detail": "Erro interno do servidor."
}
```

### **Erros de Lógica de Negócio**
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

## 📅 **FORMATOS & PADRÕES**

### **Data/Hora**
- **Formato:** ISO 8601 UTC
- **Exemplo:** `"2026-02-11T14:30:00Z"`
- **Timezone:** Todos os timestamps em UTC

### **Paginação**
- **Tipo:** PageNumberPagination
- **Tamanho Padrão da Página:** 20
- **Tamanho Máximo da Página:** 1000
- **Parâmetros de Query:** `?page=2&page_size=50`

**Estrutura da Resposta:**
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

### **Limitação de Taxa (Rate Limiting)**
- **Usuários Anônimos:** 10 requisições/hora
- **Usuários Autenticados:** 1000 requisições/hora
- **Cabeçalhos:** `X-RateLimit-Limit`, `X-RateLimit-Remaining`

---

## 🔗 **RESUMO DOS ENDPOINTS**

### **Autenticação**
```http
POST /api/accounts/token/           # Login
POST /api/accounts/token/refresh/   # Refresh token
POST /api/accounts/logout/          # Logout
```

### **Gerenciamento de Usuário**
```http
GET  /api/accounts/me/             # Perfil do usuário atual
PUT  /api/accounts/me/             # Atualizar perfil
POST /api/accounts/register/        # Registrar novo usuário
```

### **Operações Financeiras**
```http
POST /api/accounts/depositar/      # Criar depósito
POST /api/accounts/saque/          # Solicitar saque
GET  /api/accounts/transactions/   # Histórico de transações
GET  /api/accounts/dashboard/       # Dashboard financeiro
```

### **Operações de Jogos**
```http
GET  /api/games/sorteios/         # Sorteios disponíveis
POST /api/games/apostas/          # Fazer aposta
GET  /api/games/apostas/          # Histórico de apostas
GET  /api/games/modalidades/       # Modalidades de jogo
```

### **Documentação**
```http
GET /api/schema/                  # OpenAPI JSON
GET /api/docs/                    # Swagger UI
GET /api/redoc/                   # Reoc UI
```

---

## 🛠 **CHECKLIST DE INTEGRAÇÃO**

### **Checklist Pré-Lançamento**
- [ ] **Conversão de Dinheiro:** Todas as entradas convertidas para centavos (multiplicar por 100)
- [ ] **Whitelist CORS:** Domínio frontend adicionado ao `CORS_ALLOWED_ORIGINS`
- [ ] **Refresh de Token:** Implementar lógica automática de refresh de token
- [ ] **Tratamento de Erros:** Lidar com todos os formatos de erro corretamente
- [ ] **Paginação:** Implementar paginação para endpoints de lista
- [ ] **Parsing de Data:** Lidar com timestamps ISO 8601 UTC

### **Checklist de Testes**
- [ ] **Fluxo de Depósito:** Testar com valores mínimos/máximos
- [ ] **Fluxo de Saque:** Testar com chaves PIX válidas/inválidas
- [ ] **Fluxo de Apostas:** Testar com vários tipos de jogo
- [ ] **Expiração de Token:** Testar fluxo de refresh de token
- [ ] **Cenários de Erro:** Testar todos os formatos de resposta de erro
- [ ] **Paginação:** Testar manipulação de grandes conjuntos de dados

### **Checklist de Produção**
- [ ] **Variáveis de Ambiente:** Configurar origens CORS
- [ ] **Limitação de Taxa:** Monitorar cabeçalhos de rate limit
- [ ] **Monitoramento de Erros:** Implementar rastreamento de erros
- [ ] **Performance:** Monitorar tempos de resposta
- [ ] **Segurança:** Validar todas as entradas no frontend

---

## 🚨 **ARMADILHAS COMUNS DE INTEGRAÇÃO**

### **❌ NÃO FAÇA ISSO**
```javascript
// ERRADO - Enviando decimais
const depositData = {
  valor: 10.50  // Isso vai falhar na validação
};

// ERRADO - Não tratando refresh de token
// Token expira, usuário é deslogado

// ERRADO - Assumindo formato de dinheiro
const balance = response.data.saldo; // Isso já está convertido
```

### **✅ FAÇA ISSO EM VEZ**
```javascript
// CORRETO - Enviando centavos
const depositData = {
  valor: 1050  // R$ 10,50 em centavos
};

// CORRETO - Tratamento de refresh de token
if (error.response?.status === 401) {
  await refreshToken();
  retryRequest();
}

// CORRETO - Escolher formato apropriado de saldo
const balanceParaExibicao = response.data.saldo;      // 100.00
const balanceParaCalculos = response.data.saldo_cents; // 10000
```

---

## 📞 **SUPORTE & CONTATO**

### **Contatos da Equipe Backend**
- **Líder Técnico:** [Informações de Contato]
- **Documentação da API:** http://api.seudominio.com/api/docs/
- **Canal de Suporte:** [Slack/Discord/Email]

### **Contatos de Emergência**
- **Problemas de Produção:** [Contato de Emergência]
- **Problemas de Segurança:** [Contato de Segurança]

---

## 📝 **LOG DE MUDANÇAS**

### **v2.0.0 (2026-02-11)**
- ⚠️ **BREAKING:** Campos de dinheiro agora exigem inteiros em centavos
- ✨ **NOVO:** Formato de saldo duplo (centavos + decimal)
- 🔒 **SEGURANÇA:** Configuração CORS aprimorada
- 📚 **DOCS:** Reformulação completa da documentação da API
- 🐛 **CORREÇÃO:** Formatos de resposta de erro consistentes

---

**Status da Integração:** 🟢 **PRONTO PARA DESENVOLVIMENTO**  
**Nível de Suporte:** 🟢 **SUPORTE COMPLETO**  
**Documentação:** 🟢 **COMPLETA**  

*Este guia será atualizado a cada versão da API. Verifique atualizações regularmente.*
