import ServiceAPI from './ServiceBaseAPI.js';

export default class TransactionApprovalAPI extends ServiceAPI {
    
    // Mock data for different time periods
    #mockData = {
        day: {
            pendingDeposits: [
                { 
                    id: 87649, 
                    user: "Fernanda Lima", 
                    amount: 3000.00, 
                    date: "08/01/2026 14:05", 
                    status: "pending",
                    method: "PIX",
                    history: []
                },
                { 
                    id: 87648, 
                    user: "Paulo Mendes", 
                    amount: 1250.00, 
                    date: "08/01/2026 11:30", 
                    status: "pending",
                    method: "Transferência Bancária",
                    history: []
                },
                { 
                    id: 87647, 
                    user: "Camila Rocha", 
                    amount: 800.00, 
                    date: "08/01/2026 10:45", 
                    status: "pending",
                    method: "PIX",
                    history: []
                },
                { 
                    id: 87646, 
                    user: "Lucas Ferreira", 
                    amount: 2500.00, 
                    date: "08/01/2026 09:20", 
                    status: "pending",
                    method: "Boleto",
                    history: []
                },
                { 
                    id: 87645, 
                    user: "Mariana Souza", 
                    amount: 1800.00, 
                    date: "08/01/2026 08:15", 
                    status: "pending",
                    method: "PIX",
                    history: []
                }
            ],
            pendingWithdrawals: [
                { 
                    id: 54316, 
                    user: "Fernanda Lima", 
                    amount: 2000.00, 
                    date: "08/01/2026 14:10", 
                    status: "pending",
                    method: "PIX",
                    history: []
                },
                { 
                    id: 54315, 
                    user: "Paulo Mendes", 
                    amount: 950.00, 
                    date: "08/01/2026 11:55", 
                    status: "pending",
                    method: "Transferência Bancária",
                    history: []
                },
                { 
                    id: 54314, 
                    user: "Camila Rocha", 
                    amount: 500.00, 
                    date: "08/01/2026 10:30", 
                    status: "pending",
                    method: "PIX",
                    history: []
                },
                { 
                    id: 54313, 
                    user: "Lucas Ferreira", 
                    amount: 1800.00, 
                    date: "08/01/2026 09:15", 
                    status: "pending",
                    method: "Transferência Bancária",
                    history: []
                },
                { 
                    id: 54312, 
                    user: "Mariana Souza", 
                    amount: 1200.00, 
                    date: "08/01/2026 08:40", 
                    status: "pending",
                    method: "PIX",
                    history: []
                }
            ],
            suspiciousWithdrawals: [
                { 
                    id: 54325, 
                    user: "Ricardo Pereira", 
                    amount: 8500.00, 
                    date: "08/01/2026 13:25", 
                    status: "analyzing",
                    method: "Transferência Bancária",
                    suspicious: true,
                    suspiciousReason: "Valor muito acima da média de saques do usuário (média: R$ 1.200,00)",
                    history: [
                        {
                            operator: "Sistema",
                            date: "08/01/2026 13:25",
                            action: "Marcado para análise",
                            notes: "Saque com valor 7x maior que a média do usuário"
                        }
                    ]
                },
                { 
                    id: 54324, 
                    user: "Tatiana Gomes", 
                    amount: 3750.00, 
                    date: "08/01/2026 11:50", 
                    status: "analyzing",
                    method: "PIX",
                    suspicious: true,
                    suspiciousReason: "Múltiplos saques em um curto período de tempo (3 saques nas últimas 24h)",
                    history: [
                        {
                            operator: "Sistema",
                            date: "08/01/2026 11:50",
                            action: "Marcado para análise",
                            notes: "Usuário realizou 3 saques nas últimas 24h totalizando R$ 7.500,00"
                        }
                    ]
                },
                { 
                    id: 54323, 
                    user: "Eduardo Santos", 
                    amount: 5400.00, 
                    date: "08/01/2026 10:35", 
                    status: "analyzing",
                    method: "Transferência Bancária",
                    suspicious: true,
                    suspiciousReason: "Saque realizado 30 minutos após recebimento de bônus de R$ 1.000,00",
                    history: [
                        {
                            operator: "Sistema",
                            date: "08/01/2026 10:35",
                            action: "Marcado para análise",
                            notes: "Saque realizado logo após recebimento de bônus, possível violação dos termos"
                        }
                    ]
                },
                { 
                    id: 54322, 
                    user: "Bianca Martins", 
                    amount: 4200.00, 
                    date: "08/01/2026 09:40", 
                    status: "analyzing",
                    method: "PIX",
                    suspicious: true,
                    suspiciousReason: "Conta criada há menos de 48h com depósito e saque rápido",
                    history: [
                        {
                            operator: "Sistema",
                            date: "08/01/2026 09:40",
                            action: "Marcado para análise",
                            notes: "Conta nova com comportamento suspeito de depósito e saque rápido"
                        }
                    ]
                },
                { 
                    id: 54321, 
                    user: "Gustavo Lima", 
                    amount: 6800.00, 
                    date: "08/01/2026 08:20", 
                    status: "analyzing",
                    method: "Transferência Bancária",
                    suspicious: true,
                    suspiciousReason: "IP diferente do usual e valor acima da média",
                    history: [
                        {
                            operator: "Sistema",
                            date: "08/01/2026 08:20",
                            action: "Marcado para análise",
                            notes: "Acesso de IP não reconhecido e valor de saque incomum"
                        }
                    ]
                }
            ],
            decisionLogs: [
                {
                    id: 1001,
                    transactionId: 87640,
                    type: "deposit",
                    decision: "approved",
                    operator: "João Silva",
                    date: "08/01/2026 15:30",
                    notes: "Depósito verificado e aprovado. Comprovante conferido."
                },
                {
                    id: 1002,
                    transactionId: 87641,
                    type: "deposit",
                    decision: "rejected",
                    operator: "Maria Oliveira",
                    date: "08/01/2026 15:15",
                    notes: "Comprovante ilegível. Solicitado novo envio ao cliente."
                },
                {
                    id: 1003,
                    transactionId: 54310,
                    type: "withdrawal",
                    decision: "approved",
                    operator: "João Silva",
                    date: "08/01/2026 14:45",
                    notes: "Saque verificado e aprovado. Dados bancários conferidos."
                },
                {
                    id: 1004,
                    transactionId: 54311,
                    type: "withdrawal",
                    decision: "rejected",
                    operator: "Carlos Mendes",
                    date: "08/01/2026 14:30",
                    notes: "Dados bancários não conferem com o cadastro do cliente."
                },
                {
                    id: 1005,
                    transactionId: 54320,
                    type: "withdrawal",
                    decision: "analyzing",
                    operator: "Maria Oliveira",
                    date: "08/01/2026 14:00",
                    notes: "Saque com valor elevado. Solicitada verificação adicional."
                },
                {
                    id: 1006,
                    transactionId: 87642,
                    type: "deposit",
                    decision: "approved",
                    operator: "Carlos Mendes",
                    date: "08/01/2026 13:45",
                    notes: "Depósito verificado e aprovado. Comprovante conferido."
                },
                {
                    id: 1007,
                    transactionId: 54319,
                    type: "withdrawal",
                    decision: "approved",
                    operator: "João Silva",
                    date: "08/01/2026 13:30",
                    notes: "Saque verificado e aprovado. Dados bancários conferidos."
                },
                {
                    id: 1008,
                    transactionId: 87643,
                    type: "deposit",
                    decision: "rejected",
                    operator: "Maria Oliveira",
                    date: "08/01/2026 13:15",
                    notes: "Comprovante não corresponde ao valor declarado."
                },
                {
                    id: 1009,
                    transactionId: 54318,
                    type: "withdrawal",
                    decision: "approved",
                    operator: "Carlos Mendes",
                    date: "08/01/2026 13:00",
                    notes: "Saque verificado e aprovado. Dados bancários conferidos."
                },
                {
                    id: 1010,
                    transactionId: 87644,
                    type: "deposit",
                    decision: "approved",
                    operator: "João Silva",
                    date: "08/01/2026 12:45",
                    notes: "Depósito verificado e aprovado. Comprovante conferido."
                }
            ]
        },
        week: {
            pendingDeposits: [
                // Same structure as day but with more entries
            ],
            pendingWithdrawals: [
                // Same structure as day but with more entries
            ],
            suspiciousWithdrawals: [
                // Same structure as day but with more entries
            ],
            decisionLogs: [
                // Same structure as day but with more entries
            ]
        },
        month: {
            pendingDeposits: [
                // Same structure as day but with more entries
            ],
            pendingWithdrawals: [
                // Same structure as day but with more entries
            ],
            suspiciousWithdrawals: [
                // Same structure as day but with more entries
            ],
            decisionLogs: [
                // Same structure as day but with more entries
            ]
        },
        year: {
            pendingDeposits: [
                // Same structure as day but with more entries
            ],
            pendingWithdrawals: [
                // Same structure as day but with more entries
            ],
            suspiciousWithdrawals: [
                // Same structure as day but with more entries
            ],
            decisionLogs: [
                // Same structure as day but with more entries
            ]
        }
    };

    async getTransactionData(period = 'day', tab = 'deposits', status = 'all') {
        try {
            // In a real implementation, this would call the API
            // return await this.http().get(`admin/transactions?period=${period}&tab=${tab}&status=${status}`);
            
            // For now, return mock data based on the selected period
            const data = this.#mockData[period] || this.#mockData.day;
            
            // Filter by status if needed
            if (status !== 'all') {
                if (tab === 'deposits') {
                    data.pendingDeposits = data.pendingDeposits.filter(item => item.status === status);
                } else if (tab === 'withdrawals') {
                    data.pendingWithdrawals = data.pendingWithdrawals.filter(item => item.status === status);
                } else if (tab === 'suspicious') {
                    data.suspiciousWithdrawals = data.suspiciousWithdrawals.filter(item => item.status === status);
                }
            }
            
            return {
                status: 200,
                data: data
            };
        } catch (error) {
            return error.response;
        }
    }

    async updateTransactionStatus(transactionId, action, type, notes = '') {
        try {
            // In a real implementation, this would call the API
            // return await this.http().post('admin/transactions/update', { transactionId, action, type, notes });
            
            // For now, return a success response
            return {
                status: 200,
                data: {
                    message: `Transaction ${transactionId} ${action === 'approve' ? 'approved' : action === 'reject' ? 'rejected' : 'marked for analysis'} successfully`
                }
            };
        } catch (error) {
            return error.response;
        }
    }
}
