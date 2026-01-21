import { useEffect, useState } from "react";
import Head from "next/head";
import { ToastContainer, toast } from "react-toastify";
import { 
  DollarSign, 
  TrendingDown, 
  Gift, 
  Users, 
  Coins, 
  BarChart, 
  Receipt, 
  ArrowDownCircle,
  Calendar,
  TrendingUp,
  Filter,
  ChevronDown,
  Search,
  Download,
  Eye,
  Clock,
  User,
  CreditCard,
  Activity,
  Percent,
  AlertCircle
} from 'lucide-react';
import LoadCenter from "@/components/icons/LoadCenter";
import { toMoney } from "@/helpers/functions";
import FinancialDashboardAPI from "@/services/FinancialDashboardAPI";
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
  Filler
} from 'chart.js';
import { Line, Bar, Doughnut } from 'react-chartjs-2';
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
  Filler
);

const FinancialDashboardPage = function() {
  const [loading, setLoading] = useState(true);
  const [selectedPeriod, setSelectedPeriod] = useState('month');
  const [dashboardData, setDashboardData] = useState(null);
  const [chartData, setChartData] = useState(null);
  const [showDropdown, setShowDropdown] = useState(false);
  const [approvedDeposits, setApprovedDeposits] = useState([]);
  const [pendingDeposits, setPendingDeposits] = useState([]);
  const [canceledDeposits, setCanceledDeposits] = useState([]);
  const [approvedWithdrawals, setApprovedWithdrawals] = useState([]);
  const [pendingWithdrawals, setPendingWithdrawals] = useState([]);
  const [canceledWithdrawals, setCanceledWithdrawals] = useState([]);

  const financialDashboardAPI = new FinancialDashboardAPI();

  useEffect(() => {
    fetchDashboardData();
    fetchChartData();
    fetchTransactionsData();
  }, [selectedPeriod]);

  const fetchDashboardData = async () => {
    try {
      setLoading(true);
      const res = await financialDashboardAPI.getDashboardData(selectedPeriod);
      if (res?.status === 200 && res?.data) {
        setDashboardData(res.data);
      } else {
        toast.error("Erro ao carregar dados do dashboard");
      }
    } catch (error) {
      console.error("Error fetching dashboard data:", error);
      toast.error("Erro ao carregar dados do dashboard");
    } finally {
      setLoading(false);
    }
  };

  const fetchChartData = async () => {
    try {
      const res = await financialDashboardAPI.getCashFlowData();
      if (res?.status === 200 && res?.data) {
        setChartData(res.data);
      }
    } catch (error) {
      console.error("Error fetching chart data:", error);
    }
  };

  const fetchTransactionsData = async () => {
    try {
      const res = await financialDashboardAPI.getTransactionsData();
      if (res?.status === 200 && res?.data) {
        setApprovedDeposits(res.data.deposits.approved);
        setPendingDeposits(res.data.deposits.pending);
        setCanceledDeposits(res.data.deposits.canceled);
        setApprovedWithdrawals(res.data.withdrawals.approved);
        setPendingWithdrawals(res.data.withdrawals.pending);
        setCanceledWithdrawals(res.data.withdrawals.canceled);
      }
    } catch (error) {
      console.error("Error fetching transactions data:", error);
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

  const TransactionTable = ({ title, transactions, type }) => (
    <div className="bg-tertiary rounded-lg shadow-lg p-6">
      <div className="flex justify-between items-center mb-6">
        <div className="flex items-center">
          <div className="p-2 rounded-full bg-background-tertiary mr-3">
            {type === 'deposit' ? 
              <DollarSign size={18} className="text-primary" /> : 
              <ArrowDownCircle size={18} className="text-primary" />
            }
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
              <th className="pb-2 font-medium">Valor</th>
              <th className="pb-2 font-medium">Data</th>
              <th className="pb-2 font-medium">Status</th>
              <th className="pb-2 font-medium"></th>
            </tr>
          </thead>
          <tbody className="text-sm">
            {transactions.map((transaction, index) => (
              <tr key={index} className="border-b border-gray-300 text-gray-900">
                <td className="py-3">#{transaction.id}</td>
                <td className="py-3">
                  <div className="flex items-center">
                    <div className="w-6 h-6 rounded-full bg-gray-300 flex items-center justify-center mr-2">
                      <User size={12} className="text-gray-700" />
                    </div>
                    {transaction.user}
                  </div>
                </td>
                <td className="py-3 font-medium">{toMoney(transaction.amount)}</td>
                <td className="py-3 text-gray-700">{transaction.date}</td>
                <td className="py-3">
                  <span className={`px-2 py-1 rounded-full text-xs ${
                    transaction.status === 'approved' ? 'bg-green-100 text-green-800' : 
                    transaction.status === 'pending' ? 'bg-yellow-100 text-yellow-800' : 
                    'bg-red-100 text-red-800'
                  }`}>
                    {transaction.status === 'approved' ? 'Aprovado' : 
                     transaction.status === 'pending' ? 'Pendente' : 'Cancelado'}
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
          Mostrando <span className="text-gray-900">1-5</span> de <span className="text-gray-900">{transactions.length}</span> registros
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

  const SummaryMetrics = ({ title, metrics }) => (
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

  // Line chart configuration
  const lineChartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    scales: {
      x: {
        grid: {
          display: false,
          color: 'rgba(0, 0, 0, 0.1)'
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
          color: 'rgba(0, 0, 0, 0.7)',
          callback: function(value) {
            return 'R$ ' + (value / 1000) + 'k';
          }
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
      },
      tooltip: {
        mode: 'index',
        intersect: false,
        callbacks: {
          label: function(context) {
            let label = context.dataset.label || '';
            if (label) {
              label += ': ';
            }
            if (context.parsed.y !== null) {
              label += 'R$ ' + context.parsed.y.toLocaleString('pt-BR');
            }
            return label;
          }
        }
      }
    }
  };

  const lineChartData = chartData ? {
    labels: chartData.labels,
    datasets: [
      {
        label: 'Entradas',
        data: chartData.deposits,
        borderColor: 'rgba(59, 130, 246, 1)',
        backgroundColor: 'rgba(59, 130, 246, 0.1)',
        fill: true,
        tension: 0.4
      },
      {
        label: 'Saídas',
        data: chartData.withdrawals,
        borderColor: 'rgba(239, 68, 68, 1)',
        backgroundColor: 'rgba(239, 68, 68, 0.1)',
        fill: true,
        tension: 0.4
      },
      {
        label: 'Fluxo Líquido',
        data: chartData.netFlow,
        borderColor: 'rgba(16, 185, 129, 1)',
        backgroundColor: 'rgba(16, 185, 129, 0.1)',
        fill: true,
        tension: 0.4
      }
    ]
  } : null;

  const getDepositMetrics = () => [
    { label: 'Aprovados', value: dashboardData?.deposits?.approved || 0 },
    { label: 'Pendentes', value: dashboardData?.deposits?.pending || 0 },
    { label: 'Cancelados', value: dashboardData?.deposits?.canceled || 0 },
    { label: 'Ticket Médio', value: toMoney(dashboardData?.deposits?.averageTicket || 0) }
  ];

  const getWithdrawalMetrics = () => [
    { label: 'Aprovados', value: dashboardData?.withdrawals?.approved || 0 },
    { label: 'Pendentes', value: dashboardData?.withdrawals?.pending || 0 },
    { label: 'Cancelados', value: dashboardData?.withdrawals?.canceled || 0 },
    { label: 'Ticket Médio', value: toMoney(dashboardData?.withdrawals?.averageTicket || 0) }
  ];

  const getFinancialMetrics = () => [
    { label: 'Lucro Líquido', value: toMoney(dashboardData?.financials?.netProfit || 0) },
    { label: 'Rentabilidade', value: `${dashboardData?.financials?.profitability || 0}%` },
    { label: 'Total em Bônus', value: toMoney(dashboardData?.financials?.totalBonus || 0) },
    { label: 'Rácio Saque/Depósito', value: `${dashboardData?.financials?.withdrawalDepositRatio || 0}%` }
  ];

  return (
    <div className="container mx-auto p-4 md:p-6">
      <Head>
        <title>Dashboard Financeiro | Admin</title>
      </Head>
      
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center mb-6 md:mb-8">
        <div>
          <h1 className="text-white text-xl md:text-2xl font-bold mb-1 md:mb-2">Dashboard Financeiro</h1>
          <p className="text-gray-400 text-sm">Visão geral do fluxo financeiro</p>
        </div>
        <div className="flex mt-4 md:mt-0 space-x-2 md:space-x-4">
          <PeriodSelector />
          <button
            onClick={fetchDashboardData}
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
              icon={DollarSign}
              title="Depósitos Aprovados"
              value={toMoney(dashboardData?.deposits?.approvedValue || 0)}
              secondaryTitle="vs período anterior"
              secondaryValue={`${dashboardData?.deposits?.approvedChange || 0}%`}
            />
            <StatCard
              icon={AlertCircle}
              title="Depósitos Pendentes"
              value={toMoney(dashboardData?.deposits?.pendingValue || 0)}
              secondaryTitle="vs período anterior"
              secondaryValue={`${dashboardData?.deposits?.pendingChange || 0}%`}
            />
            <StatCard
              icon={ArrowDownCircle}
              title="Saques Aprovados"
              value={toMoney(dashboardData?.withdrawals?.approvedValue || 0)}
              secondaryTitle="vs período anterior"
              secondaryValue={`${dashboardData?.withdrawals?.approvedChange || 0}%`}
            />
            <StatCard
              icon={Clock}
              title="Saques Pendentes"
              value={toMoney(dashboardData?.withdrawals?.pendingValue || 0)}
              secondaryTitle="vs período anterior"
              secondaryValue={`${dashboardData?.withdrawals?.pendingChange || 0}%`}
            />
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 md:gap-6 mb-6 md:mb-8">
            <StatCard
              icon={Gift}
              title="Total em Bônus"
              value={toMoney(dashboardData?.financials?.totalBonus || 0)}
              secondaryTitle="vs período anterior"
              secondaryValue={`${dashboardData?.financials?.bonusChange || 0}%`}
            />
            <StatCard
              icon={TrendingUp}
              title="Lucro Líquido"
              value={toMoney(dashboardData?.financials?.netProfit || 0)}
              secondaryTitle="vs período anterior"
              secondaryValue={`${dashboardData?.financials?.profitChange || 0}%`}
            />
            <StatCard
              icon={Percent}
              title="Rentabilidade"
              value={`${dashboardData?.financials?.profitability || 0}%`}
              secondaryTitle="vs período anterior"
              secondaryValue={`${dashboardData?.financials?.profitabilityChange || 0}%`}
            />
            <StatCard
              icon={Activity}
              title="Rácio Saque/Depósito"
              value={`${dashboardData?.financials?.withdrawalDepositRatio || 0}%`}
              secondaryTitle="vs período anterior"
              secondaryValue={`${dashboardData?.financials?.ratioChange || 0}%`}
            />
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
            <div className="bg-tertiary rounded-lg shadow-lg p-6 lg:col-span-3">
              <div className="flex items-center justify-between mb-6">
                <h3 className="text-gray-900 text-lg font-medium">Fluxo Diário de Caixa</h3>
                <div className="flex items-center text-sm text-gray-700">
                  <Filter size={16} className="mr-1" />
                  <span>Últimos 30 dias</span>
                </div>
              </div>
              <div className="h-80">
                {lineChartData && <Line options={lineChartOptions} data={lineChartData} />}
              </div>
            </div>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
            <div className="lg:col-span-1">
              <SummaryMetrics
                title="Métricas de Depósitos"
                metrics={getDepositMetrics()}
              />
            </div>
            <div className="lg:col-span-1">
              <SummaryMetrics
                title="Métricas de Saques"
                metrics={getWithdrawalMetrics()}
              />
            </div>
            <div className="lg:col-span-1">
              <SummaryMetrics
                title="Métricas Financeiras"
                metrics={getFinancialMetrics()}
              />
            </div>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
            <div className="space-y-6">
              <TransactionTable
                title="Depósitos Aprovados"
                transactions={approvedDeposits}
                type="deposit"
              />
              <TransactionTable
                title="Depósitos Pendentes"
                transactions={pendingDeposits}
                type="deposit"
              />
            </div>

            <div className="space-y-6">
              <TransactionTable
                title="Saques Aprovados"
                transactions={approvedWithdrawals}
                type="withdrawal"
              />
              <TransactionTable
                title="Saques Pendentes"
                transactions={pendingWithdrawals}
                type="withdrawal"
              />
            </div>
          </div>
        </>
      )}
    </div>
  );
};

export default FinancialDashboardPage;
