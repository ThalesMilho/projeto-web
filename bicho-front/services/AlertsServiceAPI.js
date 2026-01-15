import ServiceAPI from './ServiceBaseAPI.js';

export default class AlertsServiceAPI extends ServiceAPI {
    
    // Mock data for different time periods
    #mockData = {
        day: {
            summary: {
                ipAlertsCount: 8,
                withdrawalAlertsCount: 12,
                bonusAlertsCount: 5,
                totalAlerts: 25
            },
            ipAlerts: [
                {
                    id: 1001,
                    user: "Carlos Silva",
                    details: "5 contas diferentes registradas no IP 192.168.1.45 nas últimas 24 horas",
                    date: "08/01/2026 09:45",
                    severity: "high",
                    relatedData: {
                        "IP": "192.168.1.45",
                        "Contas Registradas": "5",
                        "Primeiro Registro": "08/01/2026 08:15",
                        "Último Registro": "08/01/2026 09:30"
                    },
                    recommendations: [
                        "Verificar documentos de identidade de todas as contas",
                        "Bloquear temporariamente o IP para novos registros",
                        "Solicitar verificação adicional para todas as contas"
                    ]
                },
                {
                    id: 1002,
                    user: "Ana Oliveira",
                    details: "3 contas diferentes registradas no IP 192.168.2.78 nas últimas 12 horas",
                    date: "08/01/2026 08:30",
                    severity: "medium",
                    relatedData: {
                        "IP": "192.168.2.78",
                        "Contas Registradas": "3",
                        "Primeiro Registro": "08/01/2026 07:45",
                        "Último Registro": "08/01/2026 08:15"
                    },
                    recommendations: [
                        "Verificar documentos de identidade de todas as contas",
                        "Monitorar atividades das contas por 48 horas"
                    ]
                },
                {
                    id: 1003,
                    user: "Marcos Santos",
                    details: "4 contas diferentes registradas no IP 192.168.3.21 nas últimas 18 horas",
                    date: "07/01/2026 22:15",
                    severity: "high",
                    relatedData: {
                        "IP": "192.168.3.21",
                        "Contas Registradas": "4",
                        "Primeiro Registro": "07/01/2026 20:30",
                        "Último Registro": "07/01/2026 22:00"
                    },
                    recommendations: [
                        "Verificar documentos de identidade de todas as contas",
                        "Bloquear temporariamente o IP para novos registros",
                        "Solicitar verificação adicional para todas as contas"
                    ]
                },
                {
                    id: 1004,
                    user: "Juliana Costa",
                    details: "2 contas diferentes registradas no IP 192.168.4.92 nas últimas 6 horas",
                    date: "07/01/2026 19:20",
                    severity: "low",
                    relatedData: {
                        "IP": "192.168.4.92",
                        "Contas Registradas": "2",
                        "Primeiro Registro": "07/01/2026 18:45",
                        "Último Registro": "07/01/2026 19:10"
                    },
                    recommendations: [
                        "Monitorar atividades das contas por 24 horas"
                    ]
                },
                {
                    id: 1005,
                    user: "Roberto Almeida",
                    details: "3 contas diferentes registradas no IP 192.168.5.67 nas últimas 10 horas",
                    date: "07/01/2026 15:10",
                    severity: "medium",
                    relatedData: {
                        "IP": "192.168.5.67",
                        "Contas Registradas": "3",
                        "Primeiro Registro": "07/01/2026 14:30",
                        "Último Registro": "07/01/2026 15:00"
                    },
                    recommendations: [
                        "Verificar documentos de identidade de todas as contas",
                        "Monitorar atividades das contas por 48 horas"
                    ]
                }
            ],
            withdrawalAlerts: [
                {
                    id: 2001,
                    user: "Fernanda Lima",
                    details: "Solicitação de saque de R$ 3.000,00 feita 15 minutos após depósito pendente de R$ 3.500,00",
                    date: "08/01/2026 10:15",
                    severity: "high",
                    relatedData: {
                        "Valor do Depósito": "R$ 3.500,00",
                        "Status do Depósito": "Pendente",
                        "Valor do Saque": "R$ 3.000,00",
                        "Tempo entre Transações": "15 minutos"
                    },
                    recommendations: [
                        "Aguardar confirmação do depósito antes de processar o saque",
                        "Verificar histórico de transações do usuário",
                        "Solicitar documentação adicional"
                    ]
                },
                {
                    id: 2002,
                    user: "Paulo Mendes",
                    details: "Solicitação de saque de R$ 1.250,00 feita 30 minutos após depósito pendente de R$ 1.500,00",
                    date: "08/01/2026 08:45",
                    severity: "medium",
                    relatedData: {
                        "Valor do Depósito": "R$ 1.500,00",
                        "Status do Depósito": "Pendente",
                        "Valor do Saque": "R$ 1.250,00",
                        "Tempo entre Transações": "30 minutos"
                    },
                    recommendations: [
                        "Aguardar confirmação do depósito antes de processar o saque",
                        "Verificar histórico de transações do usuário"
                    ]
                },
                {
                    id: 2003,
                    user: "Camila Rocha",
                    details: "Solicitação de saque de R$ 800,00 feita 20 minutos após depósito pendente de R$ 1.000,00",
                    date: "07/01/2026 21:30",
                    severity: "medium",
                    relatedData: {
                        "Valor do Depósito": "R$ 1.000,00",
                        "Status do Depósito": "Pendente",
                        "Valor do Saque": "R$ 800,00",
                        "Tempo entre Transações": "20 minutos"
                    },
                    recommendations: [
                        "Aguardar confirmação do depósito antes de processar o saque",
                        "Verificar histórico de transações do usuário"
                    ]
                },
                {
                    id: 2004,
                    user: "Lucas Ferreira",
                    details: "Solicitação de saque de R$ 2.500,00 feita 10 minutos após depósito pendente de R$ 3.000,00",
                    date: "07/01/2026 18:20",
                    severity: "high",
                    relatedData: {
                        "Valor do Depósito": "R$ 3.000,00",
                        "Status do Depósito": "Pendente",
                        "Valor do Saque": "R$ 2.500,00",
                        "Tempo entre Transações": "10 minutos"
                    },
                    recommendations: [
                        "Aguardar confirmação do depósito antes de processar o saque",
                        "Verificar histórico de transações do usuário",
                        "Solicitar documentação adicional"
                    ]
                },
                {
                    id: 2005,
                    user: "Mariana Souza",
                    details: "Solicitação de saque de R$ 1.800,00 feita 25 minutos após depósito pendente de R$ 2.000,00",
                    date: "07/01/2026 16:45",
                    severity: "medium",
                    relatedData: {
                        "Valor do Depósito": "R$ 2.000,00",
                        "Status do Depósito": "Pendente",
                        "Valor do Saque": "R$ 1.800,00",
                        "Tempo entre Transações": "25 minutos"
                    },
                    recommendations: [
                        "Aguardar confirmação do depósito antes de processar o saque",
                        "Verificar histórico de transações do usuário"
                    ]
                }
            ],
            bonusAlerts: [
                {
                    id: 3001,
                    user: "Ricardo Pereira",
                    details: "Recebimento de bônus de R$ 500,00 e solicitação de saque de R$ 1.200,00 no mesmo dia",
                    date: "08/01/2026 09:30",
                    severity: "medium",
                    relatedData: {
                        "Valor do Bônus": "R$ 500,00",
                        "Hora do Bônus": "08/01/2026 08:45",
                        "Valor do Saque": "R$ 1.200,00",
                        "Hora do Saque": "08/01/2026 09:15",
                        "Tempo entre Transações": "30 minutos"
                    },
                    recommendations: [
                        "Verificar termos e condições do bônus",
                        "Verificar se o bônus tem requisito de rollover",
                        "Considerar bloquear o saque até cumprimento dos requisitos"
                    ]
                },
                {
                    id: 3002,
                    user: "Tatiana Gomes",
                    details: "Recebimento de bônus de R$ 300,00 e solicitação de saque de R$ 950,00 no mesmo dia",
                    date: "07/01/2026 21:15",
                    severity: "low",
                    relatedData: {
                        "Valor do Bônus": "R$ 300,00",
                        "Hora do Bônus": "07/01/2026 20:30",
                        "Valor do Saque": "R$ 950,00",
                        "Hora do Saque": "07/01/2026 21:00",
                        "Tempo entre Transações": "30 minutos"
                    },
                    recommendations: [
                        "Verificar termos e condições do bônus",
                        "Verificar se o bônus tem requisito de rollover"
                    ]
                },
                {
                    id: 3003,
                    user: "Eduardo Santos",
                    details: "Recebimento de bônus de R$ 750,00 e solicitação de saque de R$ 1.750,00 no mesmo dia",
                    date: "07/01/2026 18:40",
                    severity: "high",
                    relatedData: {
                        "Valor do Bônus": "R$ 750,00",
                        "Hora do Bônus": "07/01/2026 17:45",
                        "Valor do Saque": "R$ 1.750,00",
                        "Hora do Saque": "07/01/2026 18:30",
                        "Tempo entre Transações": "45 minutos"
                    },
                    recommendations: [
                        "Verificar termos e condições do bônus",
                        "Verificar se o bônus tem requisito de rollover",
                        "Considerar bloquear o saque até cumprimento dos requisitos",
                        "Verificar histórico de transações do usuário"
                    ]
                },
                {
                    id: 3004,
                    user: "Bianca Martins",
                    details: "Recebimento de bônus de R$ 200,00 e solicitação de saque de R$ 600,00 no mesmo dia",
                    date: "07/01/2026 15:55",
                    severity: "low",
                    relatedData: {
                        "Valor do Bônus": "R$ 200,00",
                        "Hora do Bônus": "07/01/2026 15:10",
                        "Valor do Saque": "R$ 600,00",
                        "Hora do Saque": "07/01/2026 15:45",
                        "Tempo entre Transações": "35 minutos"
                    },
                    recommendations: [
                        "Verificar termos e condições do bônus",
                        "Verificar se o bônus tem requisito de rollover"
                    ]
                },
                {
                    id: 3005,
                    user: "Gustavo Lima",
                    details: "Recebimento de bônus de R$ 1.000,00 e solicitação de saque de R$ 2.200,00 no mesmo dia",
                    date: "06/01/2026 22:10",
                    severity: "high",
                    relatedData: {
                        "Valor do Bônus": "R$ 1.000,00",
                        "Hora do Bônus": "06/01/2026 21:15",
                        "Valor do Saque": "R$ 2.200,00",
                        "Hora do Saque": "06/01/2026 22:00",
                        "Tempo entre Transações": "45 minutos"
                    },
                    recommendations: [
                        "Verificar termos e condições do bônus",
                        "Verificar se o bônus tem requisito de rollover",
                        "Considerar bloquear o saque até cumprimento dos requisitos",
                        "Verificar histórico de transações do usuário"
                    ]
                }
            ]
        },
        week: {
            summary: {
                ipAlertsCount: 24,
                withdrawalAlertsCount: 38,
                bonusAlertsCount: 19,
                totalAlerts: 81
            },
            ipAlerts: [
                // Same as day data but with more entries
            ],
            withdrawalAlerts: [
                // Same as day data but with more entries
            ],
            bonusAlerts: [
                // Same as day data but with more entries
            ]
        },
        month: {
            summary: {
                ipAlertsCount: 87,
                withdrawalAlertsCount: 124,
                bonusAlertsCount: 65,
                totalAlerts: 276
            },
            ipAlerts: [
                // Same as day data but with more entries
            ],
            withdrawalAlerts: [
                // Same as day data but with more entries
            ],
            bonusAlerts: [
                // Same as day data but with more entries
            ]
        },
        year: {
            summary: {
                ipAlertsCount: 1045,
                withdrawalAlertsCount: 1487,
                bonusAlertsCount: 782,
                totalAlerts: 3314
            },
            ipAlerts: [
                // Same as day data but with more entries
            ],
            withdrawalAlerts: [
                // Same as day data but with more entries
            ],
            bonusAlerts: [
                // Same as day data but with more entries
            ]
        }
    };

    async getAlertsData(period = 'week') {
        try {
            // In a real implementation, this would call the API
            // return await this.http().get('admin/alerts');
            
            // For now, return mock data based on the selected period
            return {
                status: 200,
                data: this.#mockData[period] || this.#mockData.week
            };
        } catch (error) {
            return error.response;
        }
    }

    async updateAlertStatus(alertId, action) {
        try {
            // In a real implementation, this would call the API
            // return await this.http().post('admin/alerts/update', { alertId, action });
            
            // For now, return a success response
            return {
                status: 200,
                data: {
                    message: `Alert ${alertId} ${action === 'resolve' ? 'resolved' : 'ignored'} successfully`
                }
            };
        } catch (error) {
            return error.response;
        }
    }
}
