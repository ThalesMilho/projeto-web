import ServiceAPI from './ServiceBaseAPI.js';

export default class GameStatisticsAPI extends ServiceAPI {
    
    // Mock data for different time periods
    #mockData = {
        day: {
            stats: {
                totalBets: 1245,
                totalVolume: 37350.75,
                totalPrizes: 24780.50,
                pendingBets: 87,
                averageProfitPerBet: 10.09,
                averageBetAmount: 30.00,
                newPlayers: 42,
                totalBetsChange: +8.5,
                totalVolumeChange: +7.2,
                totalPrizesChange: +5.8,
                pendingBetsChange: -3.2
            },
            gameModes: [
                { name: 'Grupo', betCount: 485, volume: 14550.25, averageProfit: 12.50, percentage: 39 },
                { name: 'Milhar', betCount: 320, volume: 9600.00, averageProfit: 9.75, percentage: 26 },
                { name: 'Centena', betCount: 210, volume: 6300.00, averageProfit: 8.20, percentage: 17 },
                { name: 'Dezena', betCount: 125, volume: 3750.50, averageProfit: 7.50, percentage: 10 },
                { name: 'Duque de Grupo', betCount: 65, volume: 1950.00, averageProfit: 11.25, percentage: 5 },
                { name: 'Duque de Dezena', betCount: 40, volume: 1200.00, averageProfit: 9.80, percentage: 3 }
            ],
            peakHours: [
                { hour: '08', betCount: 45 },
                { hour: '09', betCount: 78 },
                { hour: '10', betCount: 110 },
                { hour: '11', betCount: 145 },
                { hour: '12', betCount: 132 },
                { hour: '13', betCount: 98 },
                { hour: '14', betCount: 87 },
                { hour: '15', betCount: 95 },
                { hour: '16', betCount: 120 },
                { hour: '17', betCount: 150 },
                { hour: '18', betCount: 175 },
                { hour: '19', betCount: 185 },
                { hour: '20', betCount: 165 },
                { hour: '21', betCount: 120 },
                { hour: '22', betCount: 75 },
                { hour: '23', betCount: 40 }
            ],
            engagement: {
                currentPeriod: {
                    timeOnSite: 18.5,
                    loginFrequency: 3.2,
                    conversionRate: 24.5,
                    betsPerSession: 2.8,
                    userRetention: 68.5
                },
                previousPeriod: {
                    timeOnSite: 16.8,
                    loginFrequency: 2.9,
                    conversionRate: 22.7,
                    betsPerSession: 2.5,
                    userRetention: 65.2
                }
            },
            pendingBets: [
                { id: 12345, user: "Carlos Silva", gameMode: "Grupo", amount: 150.00, date: "08/01/2026 19:45" },
                { id: 12346, user: "Ana Oliveira", gameMode: "Milhar", amount: 200.00, date: "08/01/2026 19:30" },
                { id: 12347, user: "Marcos Santos", gameMode: "Centena", amount: 75.00, date: "08/01/2026 19:15" },
                { id: 12348, user: "Juliana Costa", gameMode: "Grupo", amount: 100.00, date: "08/01/2026 19:00" },
                { id: 12349, user: "Roberto Almeida", gameMode: "Dezena", amount: 50.00, date: "08/01/2026 18:45" }
            ]
        },
        week: {
            stats: {
                totalBets: 8720,
                totalVolume: 261600.50,
                totalPrizes: 173560.75,
                pendingBets: 215,
                averageProfitPerBet: 10.09,
                averageBetAmount: 30.00,
                newPlayers: 287,
                totalBetsChange: +12.3,
                totalVolumeChange: +10.8,
                totalPrizesChange: +8.5,
                pendingBetsChange: -2.1
            },
            gameModes: [
                { name: 'Grupo', betCount: 3400, volume: 102000.00, averageProfit: 12.50, percentage: 39 },
                { name: 'Milhar', betCount: 2240, volume: 67200.00, averageProfit: 9.75, percentage: 26 },
                { name: 'Centena', betCount: 1470, volume: 44100.00, averageProfit: 8.20, percentage: 17 },
                { name: 'Dezena', betCount: 875, volume: 26250.00, averageProfit: 7.50, percentage: 10 },
                { name: 'Duque de Grupo', betCount: 455, volume: 13650.00, averageProfit: 11.25, percentage: 5 },
                { name: 'Duque de Dezena', betCount: 280, volume: 8400.00, averageProfit: 9.80, percentage: 3 }
            ],
            peakHours: [
                // Same structure as day but with different values
            ],
            engagement: {
                currentPeriod: {
                    timeOnSite: 20.2,
                    loginFrequency: 3.8,
                    conversionRate: 26.7,
                    betsPerSession: 3.2,
                    userRetention: 72.4
                },
                previousPeriod: {
                    timeOnSite: 18.5,
                    loginFrequency: 3.5,
                    conversionRate: 24.3,
                    betsPerSession: 2.9,
                    userRetention: 69.8
                }
            },
            pendingBets: [
                // Same structure as day but with more entries
            ]
        },
        month: {
            stats: {
                totalBets: 37450,
                totalVolume: 1123500.25,
                totalPrizes: 745650.50,
                pendingBets: 925,
                averageProfitPerBet: 10.09,
                averageBetAmount: 30.00,
                newPlayers: 1235,
                totalBetsChange: +15.7,
                totalVolumeChange: +14.2,
                totalPrizesChange: +11.8,
                pendingBetsChange: -1.5
            },
            gameModes: [
                { name: 'Grupo', betCount: 14605, volume: 438150.00, averageProfit: 12.50, percentage: 39 },
                { name: 'Milhar', betCount: 9737, volume: 292110.00, averageProfit: 9.75, percentage: 26 },
                { name: 'Centena', betCount: 6366, volume: 190980.00, averageProfit: 8.20, percentage: 17 },
                { name: 'Dezena', betCount: 3745, volume: 112350.00, averageProfit: 7.50, percentage: 10 },
                { name: 'Duque de Grupo', betCount: 1872, volume: 56160.00, averageProfit: 11.25, percentage: 5 },
                { name: 'Duque de Dezena', betCount: 1125, volume: 33750.00, averageProfit: 9.80, percentage: 3 }
            ],
            peakHours: [
                // Same structure as day but with different values
            ],
            engagement: {
                currentPeriod: {
                    timeOnSite: 22.5,
                    loginFrequency: 4.2,
                    conversionRate: 28.3,
                    betsPerSession: 3.5,
                    userRetention: 75.8
                },
                previousPeriod: {
                    timeOnSite: 20.8,
                    loginFrequency: 3.9,
                    conversionRate: 26.5,
                    betsPerSession: 3.2,
                    userRetention: 72.5
                }
            },
            pendingBets: [
                // Same structure as day but with more entries
            ]
        },
        year: {
            stats: {
                totalBets: 449400,
                totalVolume: 13482000.50,
                totalPrizes: 8947800.75,
                pendingBets: 11100,
                averageProfitPerBet: 10.09,
                averageBetAmount: 30.00,
                newPlayers: 14820,
                totalBetsChange: +22.5,
                totalVolumeChange: +20.7,
                totalPrizesChange: +18.3,
                pendingBetsChange: -0.8
            },
            gameModes: [
                { name: 'Grupo', betCount: 175266, volume: 5257980.00, averageProfit: 12.50, percentage: 39 },
                { name: 'Milhar', betCount: 116844, volume: 3505320.00, averageProfit: 9.75, percentage: 26 },
                { name: 'Centena', betCount: 76398, volume: 2291940.00, averageProfit: 8.20, percentage: 17 },
                { name: 'Dezena', betCount: 44940, volume: 1348200.00, averageProfit: 7.50, percentage: 10 },
                { name: 'Duque de Grupo', betCount: 22470, volume: 674100.00, averageProfit: 11.25, percentage: 5 },
                { name: 'Duque de Dezena', betCount: 13482, volume: 404460.00, averageProfit: 9.80, percentage: 3 }
            ],
            peakHours: [
                // Same structure as day but with different values
            ],
            engagement: {
                currentPeriod: {
                    timeOnSite: 25.8,
                    loginFrequency: 4.7,
                    conversionRate: 32.5,
                    betsPerSession: 4.1,
                    userRetention: 82.3
                },
                previousPeriod: {
                    timeOnSite: 23.2,
                    loginFrequency: 4.3,
                    conversionRate: 29.8,
                    betsPerSession: 3.8,
                    userRetention: 78.5
                }
            },
            pendingBets: [
                // Same structure as day but with more entries
            ]
        }
    };

    async getStatisticsData(period = 'month') {
        try {
            // In a real implementation, this would call the API
            // return await this.http().get('admin/game-statistics');
            
            // For now, return mock data based on the selected period
            return {
                status: 200,
                data: this.#mockData[period] || this.#mockData.month
            };
        } catch (error) {
            return error.response;
        }
    }
}
