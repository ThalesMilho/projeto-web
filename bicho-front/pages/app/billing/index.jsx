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
  CreditCard
} from 'lucide-react';
import LoadCenter from "@/components/icons/LoadCenter";
import { toMoney } from "@/helpers/functions";
import BillingServiceAPI from "@/services/BillingServiceAPI";
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

const BillingPage = function() {
  const [loading, setLoading] = useState(true);
  const [selectedPeriod, setSelectedPeriod] = useState('month');
  const [billingData, setBillingData] = useState(null);
  const [chartData, setChartData] = useState(null);
  const [showDropdown, setShowDropdown] = useState(false);
  const [recentDeposits, setRecentDeposits] = useState([]);
  const [recentWithdrawals, setRecentWithdrawals] = useState([]);

  const billingServiceAPI = new BillingServiceAPI();

  useEffect(() => {
    fetchBillingData();
    fetchChartData();
    fetchRecentTransactions();
  }, [selectedPeriod]);

  const fetchBillingData = async () => {
    try {
      setLoading(true);
      const res = await billingServiceAPI.getBillingData(selectedPeriod);
      if (res?.status === 200 && res?.data) {
        setBillingData(res.data);
      } else {
        toast.error("Erro ao carregar dados de faturamento");
      }
    } catch (error) {
      console.error("Error fetching billing data:", error);
      toast.error("Erro ao carregar dados de faturamento");
    } finally {
      setLoading(false);
    }
  };

  const fetchChartData = async () => {
    try {
      const res = await billingServiceAPI.getMonthlyBillingData();
      if (res?.status === 200 && res?.data) {
        setChartData(res.data);
      }
    } catch (error) {
      console.error("Error fetching chart data:", error);
    }
  };

  const fetchRecentTransactions = async () => {
    try {
      const res = await billingServiceAPI.getRecentTransactions();
      if (res?.status === 200 && res?.data) {
        setRecentDeposits(res.data.deposits);
        setRecentWithdrawals(res.data.withdrawals);
      }
    } catch (error) {
      console.error("Error fetching recent transactions:", error);
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
                     transaction.status === 'pending' ? 'Pendente' : 'Recusado'}
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
          Mostrando <span className="text-gray-900">1-5</span> de <span className="text-gray-900">{type === 'deposit' ? billingData?.totalDeposits?.count : billingData?.totalWithdrawals?.count}</span> registros
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
        label: 'Depósitos',
        data: chartData.deposits,
        borderColor: 'rgba(59, 130, 246, 1)',
        backgroundColor: 'rgba(59, 130, 246, 0.1)',
        fill: true,
        tension: 0.4
      },
      {
        label: 'Saques',
        data: chartData.withdrawals,
        borderColor: 'rgba(239, 68, 68, 1)',
        backgroundColor: 'rgba(239, 68, 68, 0.1)',
        fill: true,
        tension: 0.4
      },
      {
        label: 'Lucro',
        data: chartData.profits,
        borderColor: 'rgba(16, 185, 129, 1)',
        backgroundColor: 'rgba(16, 185, 129, 0.1)',
        fill: true,
        tension: 0.4
      }
    ]
  } : null;

  const getDepositMetrics = () => [
    { label: 'Total de Depósitos', value: billingData?.totalDeposits?.count || 0 },
    { label: 'Valor Total', value: toMoney(billingData?.totalDeposits?.value || 0) },
    { label: 'Média por Depósito', value: toMoney((billingData?.totalDeposits?.value || 0) / (billingData?.totalDeposits?.count || 1)) },
    { label: 'Depósitos Hoje', value: Math.round((billingData?.totalDeposits?.count || 0) * 0.05) }
  ];

  const getWithdrawalMetrics = () => [
    { label: 'Total de Saques', value: billingData?.totalWithdrawals?.count || 0 },
    { label: 'Valor Total', value: toMoney(billingData?.totalWithdrawals?.value || 0) },
    { label: 'Média por Saque', value: toMoney((billingData?.totalWithdrawals?.value || 0) / (billingData?.totalWithdrawals?.count || 1)) },
    { label: 'Saques Hoje', value: Math.round((billingData?.totalWithdrawals?.count || 0) * 0.03) }
  ];

  return (
    <div className="container mx-auto p-4 md:p-6">
      <Head>
        <title>Dashboard Financeiro | Admin</title>
      </Head>
      
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center mb-6 md:mb-8">
        <div>
          <h1 className="text-white text-xl md:text-2xl font-bold mb-1 md:mb-2">Dashboard Financeiro</h1>
          <p className="text-gray-400 text-sm">Visão geral do desempenho financeiro</p>
        </div>
        <div className="flex mt-4 md:mt-0 space-x-2 md:space-x-4">
          <PeriodSelector />
          <button
            onClick={fetchBillingData}
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
              value={toMoney(billingData?.depositsApproved || 0)}
              secondaryTitle="vs período anterior"
              secondaryValue="+12.5%"
            />
            <StatCard
              icon={ArrowDownCircle}
              title="Saques Aprovados"
              value={toMoney(billingData?.withdrawalsApproved || 0)}
              secondaryTitle="vs período anterior"
              secondaryValue="-5.2%"
            />
            <StatCard
              icon={TrendingUp}
              title="Lucro Líquido"
              value={toMoney(billingData?.netProfit || 0)}
              secondaryTitle="vs período anterior"
              secondaryValue="+8.7%"
            />
            <StatCard
              icon={Gift}
              title="Total em Bônus"
              value={toMoney(billingData?.totalBonus || 0)}
              secondaryTitle="vs período anterior"
              secondaryValue="+3.2%"
            />
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
            <div className="bg-tertiary rounded-lg shadow-lg p-6 lg:col-span-2">
              <div className="flex items-center justify-between mb-6">
                <h3 className="text-gray-900 text-lg font-medium">Desempenho Financeiro</h3>
                <div className="flex items-center text-sm text-gray-700">
                  <Filter size={16} className="mr-1" />
                  <span>Últimos 12 meses</span>
                </div>
              </div>
              <div className="h-80">
                {lineChartData && <Line options={lineChartOptions} data={lineChartData} />}
              </div>
            </div>

            <div className="bg-tertiary rounded-lg shadow-lg p-6">
              <h3 className="text-gray-900 text-lg font-medium mb-6">Métricas de Usuários</h3>
              <div className="space-y-6">
                <div>
                  <div className="flex justify-between mb-2">
                    <div className="flex items-center">
                      <Users size={16} className="text-primary mr-2" />
                      <span className="text-gray-800">Usuários Registrados</span>
                    </div>
                    <span className="text-gray-900 font-bold">{billingData?.registeredUsers || 0}</span>
                  </div>
                  <div className="w-full bg-gray-300 rounded-full h-2">
                    <div className="bg-primary h-2 rounded-full" style={{ width: '75%' }}></div>
                  </div>
                </div>
                <div>
                  <div className="flex justify-between mb-2">
                    <div className="flex items-center">
                      <Coins size={16} className="text-yellow-600 mr-2" />
                      <span className="text-gray-800">FTDs</span>
                    </div>
                    <span className="text-gray-900 font-bold">{billingData?.ftds || 0}</span>
                  </div>
                  <div className="w-full bg-gray-300 rounded-full h-2">
                    <div className="bg-yellow-500 h-2 rounded-full" style={{ width: '60%' }}></div>
                  </div>
                </div>
                <div>
                  <div className="flex justify-between mb-2">
                    <div className="flex items-center">
                      <BarChart size={16} className="text-green-600 mr-2" />
                      <span className="text-gray-800">Taxa de Conversão FTD</span>
                    </div>
                    <span className="text-gray-900 font-bold">{billingData?.ftdConversionRate || 0}%</span>
                  </div>
                  <div className="w-full bg-gray-300 rounded-full h-2">
                    <div className="bg-green-500 h-2 rounded-full" style={{ width: `${billingData?.ftdConversionRate || 0}%` }}></div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
            <div className="space-y-6">
              <TransactionTable
                title="Total de Depósitos"
                transactions={recentDeposits}
                type="deposit"
              />
               <SummaryMetrics
                title="Resumo de Depósitos"
                metrics={getDepositMetrics()}
              />
            </div>

            <div className="space-y-6">
              <TransactionTable
                title="Total de Saques"
                transactions={recentWithdrawals}
                type="withdrawal"
              />
               <SummaryMetrics
                title="Resumo de Saques"
                metrics={getWithdrawalMetrics()}
              />
            </div>
          </div>
        </>
      )}
    </div>
  );
};

export default BillingPage;
