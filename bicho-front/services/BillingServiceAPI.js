import ServiceAPI from './ServiceBaseAPI.js';

export default class BillingServiceAPI extends ServiceAPI {
    
    // Mock data for different time periods
    #mockData = {
        day: {
            depositsApproved: 12500.75,
            withdrawalsApproved: 8350.25,
            netProfit: 4150.50,
            totalBonus: 1250.00,
            registeredUsers: 42,
            ftds: 18,
            ftdConversionRate: 42.86,
            totalDeposits: { count: 65, value: 15750.50 },
            totalWithdrawals: { count: 37, value: 9200.75 }
        },
        week: {
            depositsApproved: 87250.50,
            withdrawalsApproved: 52430.25,
            netProfit: 34820.25,
            totalBonus: 8750.00,
            registeredUsers: 284,
            ftds: 126,
            ftdConversionRate: 44.37,
            totalDeposits: { count: 412, value: 103750.25 },
            totalWithdrawals: { count: 245, value: 68930.00 }
        },
        month: {
            depositsApproved: 342780.50,
            withdrawalsApproved: 198450.75,
            netProfit: 144329.75,
            totalBonus: 32500.00,
            registeredUsers: 1248,
            ftds: 523,
            ftdConversionRate: 41.91,
            totalDeposits: { count: 1876, value: 425350.25 },
            totalWithdrawals: { count: 1042, value: 282570.50 }
        },
        year: {
            depositsApproved: 4250680.25,
            withdrawalsApproved: 2458790.50,
            netProfit: 1791889.75,
            totalBonus: 385000.00,
            registeredUsers: 15784,
            ftds: 6532,
            ftdConversionRate: 41.38,
            totalDeposits: { count: 23456, value: 5125350.75 },
            totalWithdrawals: { count: 12875, value: 3333460.50 }
        }
    };

    // Mock transaction data
    #mockTransactions = {
        deposits: [
            { id: 87654, user: "Carlos Silva", amount: 1500.00, date: "08/01/2026 09:45", status: "approved" },
            { id: 87653, user: "Ana Oliveira", amount: 2000.00, date: "08/01/2026 08:30", status: "approved" },
            { id: 87652, user: "Marcos Santos", amount: 500.00, date: "07/01/2026 22:15", status: "approved" },
            { id: 87651, user: "Juliana Costa", amount: 1000.00, date: "07/01/2026 19:20", status: "approved" },
            { id: 87650, user: "Roberto Almeida", amount: 750.00, date: "07/01/2026 15:10", status: "approved" },
            { id: 87649, user: "Fernanda Lima", amount: 3000.00, date: "07/01/2026 14:05", status: "pending" },
            { id: 87648, user: "Paulo Mendes", amount: 1250.00, date: "07/01/2026 11:30", status: "approved" },
            { id: 87647, user: "Camila Rocha", amount: 800.00, date: "06/01/2026 20:45", status: "approved" },
            { id: 87646, user: "Lucas Ferreira", amount: 2500.00, date: "06/01/2026 18:20", status: "approved" },
            { id: 87645, user: "Mariana Souza", amount: 1800.00, date: "06/01/2026 16:15", status: "approved" }
        ],
        withdrawals: [
            { id: 54321, user: "Roberto Almeida", amount: 1200.00, date: "08/01/2026 10:15", status: "pending" },
            { id: 54320, user: "Ana Oliveira", amount: 1500.00, date: "08/01/2026 08:45", status: "approved" },
            { id: 54319, user: "Carlos Silva", amount: 800.00, date: "07/01/2026 21:30", status: "approved" },
            { id: 54318, user: "Juliana Costa", amount: 650.00, date: "07/01/2026 18:20", status: "approved" },
            { id: 54317, user: "Marcos Santos", amount: 300.00, date: "07/01/2026 16:45", status: "approved" },
            { id: 54316, user: "Fernanda Lima", amount: 2000.00, date: "07/01/2026 14:10", status: "rejected" },
            { id: 54315, user: "Paulo Mendes", amount: 950.00, date: "07/01/2026 11:55", status: "approved" },
            { id: 54314, user: "Camila Rocha", amount: 500.00, date: "06/01/2026 19:30", status: "approved" },
            { id: 54313, user: "Lucas Ferreira", amount: 1800.00, date: "06/01/2026 17:15", status: "approved" },
            { id: 54312, user: "Mariana Souza", amount: 1200.00, date: "06/01/2026 15:40", status: "approved" }
        ]
    };

    async getBillingData(period = 'month') {
        try {
            // In a real implementation, this would call the API
            // return await this.http().get('admin/billing');
            
            // For now, return mock data based on the selected period
            return {
                status: 200,
                data: this.#mockData[period] || this.#mockData.month
            };
        } catch (error) {
            return error.response;
        }
    }

    async getBillingDataByDateRange(startDate, endDate) {
        try {
            // In a real implementation, this would call the API
            // return await this.http().get(`admin/billing/range?start=${startDate}&end=${endDate}`);
            
            // For now, return mock data
            return {
                status: 200,
                data: this.#mockData.month
            };
        } catch (error) {
            return error.response;
        }
    }

    async getMonthlyBillingData() {
        try {
            // In a real implementation, this would call the API
            // return await this.http().get('admin/billing/monthly');
            
            // For now, return mock data with monthly breakdown
            const monthlyData = {
                labels: ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez'],
                deposits: [250680, 275430, 298750, 312450, 325780, 342780, 356920, 372450, 389750, 405680, 425350, 450680],
                withdrawals: [145790, 158450, 168750, 175890, 185450, 198450, 212350, 225680, 238450, 248790, 262570, 282570],
                profits: [104890, 116980, 130000, 136560, 140330, 144330, 144570, 146770, 151300, 156890, 162780, 168110]
            };
            
            return {
                status: 200,
                data: monthlyData
            };
        } catch (error) {
            return error.response;
        }
    }

    async getRecentTransactions() {
        try {
            // In a real implementation, this would call the API
            // return await this.http().get('admin/transactions/recent');
            
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
