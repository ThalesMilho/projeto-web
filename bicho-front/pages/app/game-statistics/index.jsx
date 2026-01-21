import { useEffect, useState } from "react";
import Head from "next/head";
import { ToastContainer, toast } from "react-toastify";
import { 
  BarChart, 
  TrendingUp, 
  Clock, 
  Award,
  Calendar,
  Filter,
  ChevronDown,
  Search,
  Download,
  Eye,
  User,
  Clock as ClockIcon,
  DollarSign,
  Hash,
  Layers,
  Target,
  Users,
  Activity,
  Timer,
  Zap
} from 'lucide-react';
import LoadCenter from "@/components/icons/LoadCenter";
import { toMoney } from "@/helpers/functions";
import GameStatisticsAPI from "@/services/GameStatisticsAPI";
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend,
  ArcElement,
  Filler,
  RadialLinearScale
} from 'chart.js';
import { Line, Bar, Doughnut, Radar } from 'react-chartjs-2';
import moment from "moment";

// Register ChartJS components
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend,
  ArcElement,
  Filler,
  RadialLinearScale
);

const GameStatisticsPage = function() {
  const [loading, setLoading] = useState(true);
  const [selectedPeriod, setSelectedPeriod] = useState('month');
  const [showDropdown, setShowDropdown] = useState(false);
  const [statsData, setStatsData] = useState(null);
  const [gameModeData, setGameModeData] = useState(null);
  const [peakHoursData, setPeakHoursData] = useState(null);
  const [engagementData, setEngagementData] = useState(null);
  const [pendingBets, setPendingBets] = useState([]);

  const gameStatisticsAPI = new GameStatisticsAPI();

  useEffect(() => {
    fetchStatisticsData();
  }, [selectedPeriod]);

  const fetchStatisticsData = async () => {
    try {
      setLoading(true);
      const res = await gameStatisticsAPI.getStatisticsData(selectedPeriod);
      if (res?.status === 200 && res?.data) {
        setStatsData(res.data.stats);
        setGameModeData(res.data.gameModes);
        setPeakHoursData(res.data.peakHours);
        setEngagementData(res.data.engagement);
        setPendingBets(res.data.pendingBets);
      } else {
        toast.error("Erro ao carregar dados de estatísticas");
      }
    } catch (error) {
      console.error("Error fetching statistics data:", error);
      toast.error("Erro ao carregar dados de estatísticas");
    } finally {
      setLoading(false);
    }
  };

  const StatCard = ({ icon: Icon, title, value, secondaryValue, secondaryTitle }) => (
    <div className="bg-tertiary rounded-lg shadow-lg transition-all duration-300 hover:shadow-xl">
      <div className="p-6">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center">
            <div className="p-3 rounded-full bg-background-tertiary mr-3">
              <Icon size={20} className="text-primary" />
            </div>
            <div>
              <p className="text-gray-800 text-sm font-medium">{title}</p>
              <h3 className="text-gray-900 text-xl font-bold">{value}</h3>
            </div>
          </div>
          {secondaryValue && (
            <div className="text-right">
              <p className="text-gray-700 text-xs">{secondaryTitle}</p>
              <p className="text-gray-900 text-sm font-medium">{secondaryValue}</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );

  const GameModeTable = ({ title, data }) => (
    <div className="bg-tertiary rounded-lg shadow-lg p-6">
      <div className="flex justify-between items-center mb-6">
        <div className="flex items-center">
          <div className="p-2 rounded-full bg-background-tertiary mr-3">
            <Target size={18} className="text-primary" />
          </div>
          <h3 className="text-gray-900 text-lg font-medium">{title}</h3>
        </div>
        <div className="flex space-x-2">
          <div className="relative">
            <input 
              type="text" 
              placeholder="Buscar..." 
              className="pl-8 pr-3 py-1 rounded-lg bg-background-tertiary text-gray-900 text-sm focus:outline-none focus:ring-1 focus:ring-primary"
            />
            <Search size={14} className="absolute left-2 top-1/2 transform -translate-y-1/2 text-gray-600" />
          </div>
          <button className="p-1 rounded-lg bg-background-tertiary text-primary hover:bg-primary hover:text-white">
            <Download size={16} />
          </button>
        </div>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full">
          <thead>
            <tr className="text-left text-gray-700 text-xs border-b border-gray-300">
              <th className="pb-2 font-medium">Modalidade</th>
              <th className="pb-2 font-medium">Total de Apostas</th>
              <th className="pb-2 font-medium">Volume (R$)</th>
              <th className="pb-2 font-medium">Lucro Médio</th>
              <th className="pb-2 font-medium">% do Total</th>
            </tr>
          </thead>
          <tbody className="text-sm">
            {data && data.map((mode, index) => (
              <tr key={index} className="border-b border-gray-300 text-gray-900">
                <td className="py-3 font-medium">{mode.name}</td>
                <td className="py-3">{mode.betCount.toLocaleString()}</td>
                <td className="py-3">{toMoney(mode.volume)}</td>
                <td className="py-3">{toMoney(mode.averageProfit)}</td>
                <td className="py-3">
                  <div className="flex items-center">
                    <span className="mr-2">{mode.percentage}%</span>
                    <div className="w-16 bg-gray-300 rounded-full h-1.5">
                      <div 
                        className="bg-primary h-1.5 rounded-full" 
                        style={{ width: `${mode.percentage}%` }}
                      ></div>
                    </div>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );

  const PendingBetsTable = ({ title, bets }) => (
    <div className="bg-tertiary rounded-lg shadow-lg p-6">
      <div className="flex justify-between items-center mb-6">
        <div className="flex items-center">
          <div className="p-2 rounded-full bg-background-tertiary mr-3">
            <Clock size={18} className="text-primary" />
          </div>
          <h3 className="text-gray-900 text-lg font-medium">{title}</h3>
        </div>
        <div className="flex space-x-2">
          <div className="relative">
            <input 
              type="text" 
              placeholder="Buscar..." 
              className="pl-8 pr-3 py-1 rounded-lg bg-background-tertiary text-gray-900 text-sm focus:outline-none focus:ring-1 focus:ring-primary"
            />
            <Search size={14} className="absolute left-2 top-1/2 transform -translate-y-1/2 text-gray-600" />
          </div>
          <button className="p-1 rounded-lg bg-background-tertiary text-primary hover:bg-primary hover:text-white">
            <Download size={16} />
          </button>
        </div>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full">
          <thead>
            <tr className="text-left text-gray-700 text-xs border-b border-gray-300">
              <th className="pb-2 font-medium">ID</th>
              <th className="pb-2 font-medium">Usuário</th>
              <th className="pb-2 font-medium">Modalidade</th>
              <th className="pb-2 font-medium">Valor</th>
              <th className="pb-2 font-medium">Data</th>
              <th className="pb-2 font-medium">Status</th>
              <th className="pb-2 font-medium"></th>
            </tr>
          </thead>
          <tbody className="text-sm">
            {bets.map((bet, index) => (
              <tr key={index} className="border-b border-gray-300 text-gray-900">
                <td className="py-3">#{bet.id}</td>
                <td className="py-3">
                  <div className="flex items-center">
                    <div className="w-6 h-6 rounded-full bg-gray-300 flex items-center justify-center mr-2">
                      <User size={12} className="text-gray-700" />
                    </div>
                    {bet.user}
                  </div>
                </td>
                <td className="py-3">{bet.gameMode}</td>
                <td className="py-3 font-medium">{toMoney(bet.amount)}</td>
                <td className="py-3 text-gray-700">{bet.date}</td>
                <td className="py-3">
                  <span className="px-2 py-1 rounded-full text-xs bg-yellow-100 text-yellow-800">
                    Pendente
                  </span>
                </td>
                <td className="py-3 text-right">
                  <button className="text-primary hover:text-blue-700">
                    <Eye size={16} />
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div className="mt-4 flex justify-between items-center text-sm">
        <div className="text-gray-700">
          Mostrando <span className="text-gray-900">1-{Math.min(5, bets.length)}</span> de <span className="text-gray-900">{bets.length}</span> apostas
        </div>
        <div className="flex space-x-1">
          <button className="px-3 py-1 rounded bg-background-tertiary text-gray-700 hover:bg-background-secondary">Anterior</button>
          <button className="px-3 py-1 rounded bg-primary text-white">1</button>
          <button className="px-3 py-1 rounded bg-background-tertiary text-gray-700 hover:bg-background-secondary">2</button>
          <button className="px-3 py-1 rounded bg-background-tertiary text-gray-700 hover:bg-background-secondary">3</button>
          <button className="px-3 py-1 rounded bg-background-tertiary text-gray-700 hover:bg-background-secondary">Próximo</button>
        </div>
      </div>
    </div>
  );

  const EngagementMetrics = ({ title, metrics }) => (
    <div className="bg-tertiary rounded-lg shadow-lg p-6">
      <h3 className="text-gray-900 text-lg font-medium mb-4">{title}</h3>
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {metrics.map((metric, index) => (
          <div key={index} className="bg-background-tertiary rounded-lg p-4">
            <p className="text-gray-700 text-xs mb-1">{metric.label}</p>
            <p className="text-gray-900 text-lg font-bold">{metric.value}</p>
          </div>
        ))}
      </div>
    </div>
  );

  const PeriodSelector = () => (
    <div className="relative">
      <button 
        onClick={() => setShowDropdown(!showDropdown)} 
        className="flex items-center bg-primary rounded-lg px-4 py-2 text-white font-medium"
      >
        <Calendar size={16} className="mr-2" />
        {selectedPeriod === 'day' && 'Hoje'}
        {selectedPeriod === 'week' && 'Esta Semana'}
        {selectedPeriod === 'month' && 'Este Mês'}
        {selectedPeriod === 'year' && 'Este Ano'}
        <ChevronDown size={16} className="ml-2" />
      </button>
      
      {showDropdown && (
        <div className="absolute top-full left-0 mt-1 bg-tertiary rounded-lg shadow-lg z-10 w-full">
          <div className="py-1">
            <button 
              onClick={() => { setSelectedPeriod('day'); setShowDropdown(false); }} 
              className="block w-full text-left px-4 py-2 text-sm text-gray-600 hover:bg-primary hover:text-white"
            >
              Hoje
            </button>
            <button 
              onClick={() => { setSelectedPeriod('week'); setShowDropdown(false); }} 
              className="block w-full text-left px-4 py-2 text-sm text-gray-600 hover:bg-primary hover:text-white"
            >
              Esta Semana
            </button>
            <button 
              onClick={() => { setSelectedPeriod('month'); setShowDropdown(false); }} 
              className="block w-full text-left px-4 py-2 text-sm text-gray-600 hover:bg-primary hover:text-white"
            >
              Este Mês
            </button>
            <button 
              onClick={() => { setSelectedPeriod('year'); setShowDropdown(false); }} 
              className="block w-full text-left px-4 py-2 text-sm text-gray-600 hover:bg-primary hover:text-white"
            >
              Este Ano
            </button>
          </div>
        </div>
      )}
    </div>
  );

  // Doughnut chart configuration for game modes
  const doughnutChartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'right',
        labels: {
          color: 'rgba(0, 0, 0, 0.7)',
          usePointStyle: true,
          pointStyle: 'circle',
          padding: 20
        }
      },
      tooltip: {
        callbacks: {
          label: function(context) {
            let label = context.label || '';
            if (label) {
              label += ': ';
            }
            if (context.parsed !== null) {
              label += context.parsed + '%';
            }
            return label;
          }
        }
      }
    }
  };

  const doughnutChartData = gameModeData ? {
    labels: gameModeData.map(mode => mode.name),
    datasets: [
      {
        data: gameModeData.map(mode => mode.percentage),
        backgroundColor: [
          'rgba(59, 130, 246, 0.8)',
          'rgba(16, 185, 129, 0.8)',
          'rgba(245, 158, 11, 0.8)',
          'rgba(239, 68, 68, 0.8)',
          'rgba(139, 92, 246, 0.8)',
          'rgba(236, 72, 153, 0.8)',
          'rgba(14, 165, 233, 0.8)',
          'rgba(168, 85, 247, 0.8)'
        ],
        borderColor: [
          'rgba(59, 130, 246, 1)',
          'rgba(16, 185, 129, 1)',
          'rgba(245, 158, 11, 1)',
          'rgba(239, 68, 68, 1)',
          'rgba(139, 92, 246, 1)',
          'rgba(236, 72, 153, 1)',
          'rgba(14, 165, 233, 1)',
          'rgba(168, 85, 247, 1)'
        ],
        borderWidth: 1
      }
    ]
  } : null;

  // Bar chart configuration for peak hours
  const barChartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    scales: {
      x: {
        grid: {
          display: false
        },
        ticks: {
          color: 'rgba(0, 0, 0, 0.7)'
        }
      },
      y: {
        grid: {
          color: 'rgba(0, 0, 0, 0.1)'
        },
        ticks: {
          color: 'rgba(0, 0, 0, 0.7)'
        }
      }
    },
    plugins: {
      legend: {
        display: false
      },
      tooltip: {
        callbacks: {
          label: function(context) {
            return `${context.parsed.y} apostas`;
          }
        }
      }
    }
  };

  const barChartData = peakHoursData ? {
    labels: peakHoursData.map(hour => `${hour.hour}h`),
    datasets: [
      {
        data: peakHoursData.map(hour => hour.betCount),
        backgroundColor: 'rgba(59, 130, 246, 0.8)',
        borderColor: 'rgba(59, 130, 246, 1)',
        borderWidth: 1,
        borderRadius: 4
      }
    ]
  } : null;

  // Radar chart configuration for engagement
  const radarChartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    scales: {
      r: {
        angleLines: {
          color: 'rgba(0, 0, 0, 0.1)'
        },
        grid: {
          color: 'rgba(0, 0, 0, 0.1)'
        },
        pointLabels: {
          color: 'rgba(0, 0, 0, 0.7)',
          font: {
            size: 10
          }
        },
        ticks: {
          backdropColor: 'transparent',
          color: 'rgba(0, 0, 0, 0.7)',
          showLabelBackdrop: false
        }
      }
    },
    plugins: {
      legend: {
        position: 'top',
        labels: {
          color: 'rgba(0, 0, 0, 0.7)',
          usePointStyle: true,
          pointStyle: 'circle'
        }
      }
    }
  };

  const radarChartData = engagementData ? {
    labels: [
      'Tempo no Site (min)',
      'Frequência de Login',
      'Taxa de Conversão',
      'Apostas por Sessão',
      'Retenção de Usuários'
    ],
    datasets: [
      {
        label: 'Atual',
        data: [
          engagementData.currentPeriod.timeOnSite,
          engagementData.currentPeriod.loginFrequency,
          engagementData.currentPeriod.conversionRate,
          engagementData.currentPeriod.betsPerSession,
          engagementData.currentPeriod.userRetention
        ],
        backgroundColor: 'rgba(59, 130, 246, 0.2)',
        borderColor: 'rgba(59, 130, 246, 1)',
        borderWidth: 2,
        pointBackgroundColor: 'rgba(59, 130, 246, 1)',
        pointRadius: 3
      },
      {
        label: 'Período Anterior',
        data: [
          engagementData.previousPeriod.timeOnSite,
          engagementData.previousPeriod.loginFrequency,
          engagementData.previousPeriod.conversionRate,
          engagementData.previousPeriod.betsPerSession,
          engagementData.previousPeriod.userRetention
        ],
        backgroundColor: 'rgba(16, 185, 129, 0.2)',
        borderColor: 'rgba(16, 185, 129, 1)',
        borderWidth: 2,
        pointBackgroundColor: 'rgba(16, 185, 129, 1)',
        pointRadius: 3
      }
    ]
  } : null;

  return (
    <div className="container mx-auto p-4 md:p-6">
      <Head>
        <title>Estatísticas de Jogos | Admin</title>
      </Head>
      
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center mb-6 md:mb-8">
        <div>
          <h1 className="text-white text-xl md:text-2xl font-bold mb-1 md:mb-2">Estatísticas de Jogos</h1>
          <p className="text-gray-400 text-sm">Análise de desempenho e engajamento</p>
        </div>
        <div className="flex mt-4 md:mt-0 space-x-2 md:space-x-4">
          <PeriodSelector />
          <button
            onClick={fetchStatisticsData}
            className="bg-primary hover:bg-blue-700 text-white font-medium py-2 px-3 md:px-4 rounded-lg flex items-center"
          >
            <svg className="w-4 h-4 mr-1 md:mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"></path>
            </svg>
            <span className="text-sm md:text-base">Atualizar</span>
          </button>
        </div>
      </div>
      
      <ToastContainer />

      {loading ? (
        <div className="flex justify-center items-center h-64">
          <LoadCenter />
        </div>
      ) : (
        <>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 md:gap-6 mb-6 md:mb-8">
            <StatCard
              icon={Target}
              title="Total de Apostas"
              value={statsData?.totalBets.toLocaleString() || "0"}
              secondaryTitle="vs período anterior"
              secondaryValue={`${statsData?.totalBetsChange || 0}%`}
            />
            <StatCard
              icon={DollarSign}
              title="Volume Total (R$)"
              value={toMoney(statsData?.totalVolume || 0)}
              secondaryTitle="vs período anterior"
              secondaryValue={`${statsData?.totalVolumeChange || 0}%`}
            />
            <StatCard
              icon={Award}
              title="Total em Prêmios"
              value={toMoney(statsData?.totalPrizes || 0)}
              secondaryTitle="vs período anterior"
              secondaryValue={`${statsData?.totalPrizesChange || 0}%`}
            />
            <StatCard
              icon={Clock}
              title="Apostas Pendentes"
              value={statsData?.pendingBets || 0}
              secondaryTitle="vs período anterior"
              secondaryValue={`${statsData?.pendingBetsChange || 0}%`}
            />
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
            <div className="bg-tertiary rounded-lg shadow-lg p-6">
              <div className="flex items-center justify-between mb-6">
                <h3 className="text-gray-900 text-lg font-medium">Modalidades mais Jogadas</h3>
                <div className="flex items-center text-sm text-gray-700">
                  <Filter size={16} className="mr-1" />
                  <span>Por volume de apostas</span>
                </div>
              </div>
              <div className="h-80">
                {doughnutChartData && <Doughnut options={doughnutChartOptions} data={doughnutChartData} />}
              </div>
            </div>

            <div className="bg-tertiary rounded-lg shadow-lg p-6">
              <div className="flex items-center justify-between mb-6">
                <h3 className="text-gray-900 text-lg font-medium">Horários de Pico de Apostas</h3>
                <div className="flex items-center text-sm text-gray-700">
                  <Filter size={16} className="mr-1" />
                  <span>Últimos 7 dias</span>
                </div>
              </div>
              <div className="h-80">
                {barChartData && <Bar options={barChartOptions} data={barChartData} />}
              </div>
            </div>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
            <div className="lg:col-span-2">
              <GameModeTable 
                title="Desempenho por Modalidade" 
                data={gameModeData || []}
              />
            </div>

            <div className="bg-tertiary rounded-lg shadow-lg p-6">
              <div className="flex items-center justify-between mb-6">
                <h3 className="text-gray-900 text-lg font-medium">Indicadores de Engajamento</h3>
                <div className="flex items-center text-sm text-gray-700">
                  <Filter size={16} className="mr-1" />
                  <span>Comparativo</span>
                </div>
              </div>
              <div className="h-80">
                {radarChartData && <Radar options={radarChartOptions} data={radarChartData} />}
              </div>
            </div>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
            <EngagementMetrics
              title="Métricas de Engajamento"
              metrics={[
                { label: 'Tempo Médio no Site', value: `${engagementData?.currentPeriod?.timeOnSite || 0} min` },
                { label: 'Frequência de Login', value: `${engagementData?.currentPeriod?.loginFrequency || 0}/semana` },
                { label: 'Taxa de Conversão', value: `${engagementData?.currentPeriod?.conversionRate || 0}%` },
                { label: 'Apostas por Sessão', value: engagementData?.currentPeriod?.betsPerSession || 0 }
              ]}
            />
            <EngagementMetrics
              title="Métricas de Desempenho"
              metrics={[
                { label: 'Lucro Médio por Aposta', value: toMoney(statsData?.averageProfitPerBet || 0) },
                { label: 'Valor Médio de Aposta', value: toMoney(statsData?.averageBetAmount || 0) },
                { label: 'Taxa de Retenção', value: `${engagementData?.currentPeriod?.userRetention || 0}%` },
                { label: 'Novos Jogadores', value: statsData?.newPlayers || 0 }
              ]}
            />
          </div>

          <div className="mb-8">
            <PendingBetsTable 
              title="Apostas Pendentes" 
              bets={pendingBets || []}
            />
          </div>
        </>
      )}
    </div>
  );
};

export default GameStatisticsPage;
