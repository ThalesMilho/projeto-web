import ServiceAPI from './ServiceBaseAPI.js';

export default class FinancialDashboardAPI extends ServiceAPI {
    
    // Mock data for different time periods
    #mockData = {
        day: {
            deposits: {
                approved: 125,
                pending: 18,
                canceled: 7,
                approvedValue: 18750.50,
                pendingValue: 4250.25,
                canceledValue: 1500.00,
                averageTicket: 150.00,
                approvedChange: +8.5,
                pendingChange: -2.3
            },
            withdrawals: {
                approved: 87,
                pending: 15,
                canceled: 5,
                approvedValue: 12350.75,
                pendingValue: 3250.50,
                canceledValue: 1100.25,
                averageTicket: 142.00,
                approvedChange: -3.2,
                pendingChange: +5.7
            },
            financials: {
                netProfit: 6399.75,
                profitability: 34.13,
                totalBonus: 1850.00,
                withdrawalDepositRatio: 65.87,
                bonusChange: +2.1,
                profitChange: +4.3,
                profitabilityChange: +1.2,
                ratioChange: -1.5
            }
        },
        week: {
            deposits: {
                approved: 875,
                pending: 124,
                canceled: 48,
                approvedValue: 131250.50,
                pendingValue: 29750.25,
                canceledValue: 10500.00,
                averageTicket: 150.00,
                approvedChange: +10.2,
                pendingChange: -4.5
            },
            withdrawals: {
                approved: 609,
                pending: 105,
                canceled: 35,
                approvedValue: 86450.25,
                pendingValue: 22750.50,
                canceledValue: 7700.75,
                averageTicket: 142.00,
                approvedChange: -2.8,
                pendingChange: +6.3
            },
            financials: {
                netProfit: 44800.25,
                profitability: 34.13,
                totalBonus: 12950.00,
                withdrawalDepositRatio: 65.87,
                bonusChange: +3.5,
                profitChange: +5.7,
                profitabilityChange: +2.1,
                ratioChange: -2.3
            }
        },
        month: {
            deposits: {
                approved: 3750,
                pending: 532,
                canceled: 206,
                approvedValue: 562500.50,
                pendingValue: 127500.25,
                canceledValue: 45000.00,
                averageTicket: 150.00,
                approvedChange: +12.7,
                pendingChange: -5.8
            },
            withdrawals: {
                approved: 2610,
                pending: 450,
                canceled: 150,
                approvedValue: 370750.25,
                pendingValue: 97500.50,
                canceledValue: 33000.75,
                averageTicket: 142.00,
                approvedChange: -3.5,
                pendingChange: +7.2
            },
            financials: {
                netProfit: 191750.25,
                profitability: 34.09,
                totalBonus: 55500.00,
                withdrawalDepositRatio: 65.91,
                bonusChange: +4.2,
                profitChange: +6.8,
                profitabilityChange: +2.5,
                ratioChange: -3.1
            }
        },
        year: {
            deposits: {
                approved: 45000,
                pending: 6384,
                canceled: 2472,
                approvedValue: 6750000.50,
                pendingValue: 1530000.25,
                canceledValue: 540000.00,
                averageTicket: 150.00,
                approvedChange: +15.3,
                pendingChange: -7.2
            },
            withdrawals: {
                approved: 31320,
                pending: 5400,
                canceled: 1800,
                approvedValue: 4449000.25,
                pendingValue: 1170000.50,
                canceledValue: 396000.75,
                averageTicket: 142.00,
                approvedChange: -4.8,
                pendingChange: +8.5
            },
            financials: {
                netProfit: 2301000.25,
                profitability: 34.09,
                totalBonus: 666000.00,
                withdrawalDepositRatio: 65.91,
                bonusChange: +5.7,
                profitChange: +8.3,
                profitabilityChange: +3.2,
                ratioChange: -4.5
            }
        }
    };

    // Mock transaction data
    #mockTransactions = {
        deposits: {
            approved: [
                { id: 87654, user: "Carlos Silva", amount: 1500.00, date: "08/01/2026 09:45", status: "approved" },
                { id: 87653, user: "Ana Oliveira", amount: 2000.00, date: "08/01/2026 08:30", status: "approved" },
                { id: 87652, user: "Marcos Santos", amount: 500.00, date: "07/01/2026 22:15", status: "approved" },
                { id: 87651, user: "Juliana Costa", amount: 1000.00, date: "07/01/2026 19:20", status: "approved" },
                { id: 87650, user: "Roberto Almeida", amount: 750.00, date: "07/01/2026 15:10", status: "approved" }
            ],
            pending: [
                { id: 87649, user: "Fernanda Lima", amount: 3000.00, date: "07/01/2026 14:05", status: "pending" },
                { id: 87648, user: "Paulo Mendes", amount: 1250.00, date: "07/01/2026 11:30", status: "pending" },
                { id: 87647, user: "Camila Rocha", amount: 800.00, date: "06/01/2026 20:45", status: "pending" },
                { id: 87646, user: "Lucas Ferreira", amount: 2500.00, date: "06/01/2026 18:20", status: "pending" },
                { id: 87645, user: "Mariana Souza", amount: 1800.00, date: "06/01/2026 16:15", status: "pending" }
            ],
            canceled: [
                { id: 87644, user: "Ricardo Pereira", amount: 1200.00, date: "06/01/2026 14:30", status: "canceled" },
                { id: 87643, user: "Tatiana Gomes", amount: 950.00, date: "06/01/2026 12:15", status: "canceled" },
                { id: 87642, user: "Eduardo Santos", amount: 1750.00, date: "05/01/2026 22:40", status: "canceled" },
                { id: 87641, user: "Bianca Martins", amount: 600.00, date: "05/01/2026 19:55", status: "canceled" },
                { id: 87640, user: "Gustavo Lima", amount: 2200.00, date: "05/01/2026 17:10", status: "canceled" }
            ]
        },
        withdrawals: {
            approved: [
                { id: 54321, user: "Roberto Almeida", amount: 1200.00, date: "08/01/2026 10:15", status: "approved" },
                { id: 54320, user: "Ana Oliveira", amount: 1500.00, date: "08/01/2026 08:45", status: "approved" },
                { id: 54319, user: "Carlos Silva", amount: 800.00, date: "07/01/2026 21:30", status: "approved" },
                { id: 54318, user: "Juliana Costa", amount: 650.00, date: "07/01/2026 18:20", status: "approved" },
                { id: 54317, user: "Marcos Santos", amount: 300.00, date: "07/01/2026 16:45", status: "approved" }
            ],
            pending: [
                { id: 54316, user: "Fernanda Lima", amount: 2000.00, date: "07/01/2026 14:10", status: "pending" },
                { id: 54315, user: "Paulo Mendes", amount: 950.00, date: "07/01/2026 11:55", status: "pending" },
                { id: 54314, user: "Camila Rocha", amount: 500.00, date: "06/01/2026 19:30", status: "pending" },
                { id: 54313, user: "Lucas Ferreira", amount: 1800.00, date: "06/01/2026 17:15", status: "pending" },
                { id: 54312, user: "Mariana Souza", amount: 1200.00, date: "06/01/2026 15:40", status: "pending" }
            ],
            canceled: [
                { id: 54311, user: "Ricardo Pereira", amount: 900.00, date: "06/01/2026 13:25", status: "canceled" },
                { id: 54310, user: "Tatiana Gomes", amount: 750.00, date: "06/01/2026 11:50", status: "canceled" },
                { id: 54309, user: "Eduardo Santos", amount: 1400.00, date: "05/01/2026 21:35", status: "canceled" },
                { id: 54308, user: "Bianca Martins", amount: 450.00, date: "05/01/2026 18:40", status: "canceled" },
                { id: 54307, user: "Gustavo Lima", amount: 1800.00, date: "05/01/2026 16:20", status: "canceled" }
            ]
        }
    };

    async getDashboardData(period = 'month') {
        try {
            // In a real implementation, this would call the API
            // return await this.http().get('admin/financial-dashboard');
            
            // For now, return mock data based on the selected period
            return {
                status: 200,
                data: this.#mockData[period] || this.#mockData.month
            };
        } catch (error) {
            return error.response;
        }
    }

    async getCashFlowData() {
        try {
            // In a real implementation, this would call the API
            // return await this.http().get('admin/financial-dashboard/cash-flow');
            
            // For now, return mock data with daily breakdown for the last 30 days
            const days = Array.from({ length: 30 }, (_, i) => {
                const date = new Date();
                date.setDate(date.getDate() - (29 - i));
                return date.getDate() + '/' + (date.getMonth() + 1);
            });
            
            // Generate random but realistic data
            const deposits = Array.from({ length: 30 }, () => Math.floor(Math.random() * 20000) + 10000);
            const withdrawals = Array.from({ length: 30 }, (_, i) => Math.floor(deposits[i] * (Math.random() * 0.3 + 0.5))); // 50-80% of deposits
            const netFlow = deposits.map((deposit, i) => deposit - withdrawals[i]);
            
            return {
                status: 200,
                data: {
                    labels: days,
                    deposits,
                    withdrawals,
                    netFlow
                }
            };
        } catch (error) {
            return error.response;
        }
    }

    async getTransactionsData() {
        try {
            // In a real implementation, this would call the API
            // return await this.http().get('admin/financial-dashboard/transactions');
            
            // For now, return mock transaction data
            return {
                status: 200,
                data: this.#mockTransactions
            };
        } catch (error) {
            return error.response;
        }
    }
}
