import { useEffect, useState } from "react";
import Head from "next/head";
import { ToastContainer, toast } from "react-toastify";
import { 
  AlertTriangle, 
  Shield, 
  Users, 
  Clock, 
  Gift, 
  ArrowDownCircle,
  Calendar,
  Filter,
  ChevronDown,
  Search,
  Download,
  Eye,
  User,
  Activity,
  AlertCircle,
  Bell,
  CheckCircle,
  XCircle,
  Info
} from 'lucide-react';
import LoadCenter from "@/components/icons/LoadCenter";
import { toMoney } from "@/helpers/functions";
import AlertsServiceAPI from "@/services/AlertsServiceAPI";
import moment from "moment";

const AlertsPage = function() {
  const [loading, setLoading] = useState(true);
  const [selectedPeriod, setSelectedPeriod] = useState('week');
  const [showDropdown, setShowDropdown] = useState(false);
  const [alertsData, setAlertsData] = useState(null);
  const [ipAlerts, setIpAlerts] = useState([]);
  const [withdrawalAlerts, setWithdrawalAlerts] = useState([]);
  const [bonusAlerts, setBonusAlerts] = useState([]);
  const [selectedAlert, setSelectedAlert] = useState(null);
  const [showAlertDetails, setShowAlertDetails] = useState(false);

  const alertsServiceAPI = new AlertsServiceAPI();

  useEffect(() => {
    fetchAlertsData();
  }, [selectedPeriod]);

  const fetchAlertsData = async () => {
    try {
      setLoading(true);
      const res = await alertsServiceAPI.getAlertsData(selectedPeriod);
      if (res?.status === 200 && res?.data) {
        setAlertsData(res.data);
        setIpAlerts(res.data.ipAlerts);
        setWithdrawalAlerts(res.data.withdrawalAlerts);
        setBonusAlerts(res.data.bonusAlerts);
      } else {
        toast.error("Erro ao carregar dados de alertas");
      }
    } catch (error) {
      console.error("Error fetching alerts data:", error);
      toast.error("Erro ao carregar dados de alertas");
    } finally {
      setLoading(false);
    }
  };

  const handleAlertAction = async (alertId, action) => {
    try {
      setLoading(true);
      const res = await alertsServiceAPI.updateAlertStatus(alertId, action);
      if (res?.status === 200) {
        toast.success(`Alerta ${action === 'resolve' ? 'resolvido' : 'ignorado'} com sucesso`);
        fetchAlertsData();
      } else {
        toast.error("Erro ao atualizar status do alerta");
      }
    } catch (error) {
      console.error("Error updating alert status:", error);
      toast.error("Erro ao atualizar status do alerta");
    } finally {
      setLoading(false);
    }
  };

  const viewAlertDetails = (alert) => {
    setSelectedAlert(alert);
    setShowAlertDetails(true);
  };

  const AlertCard = ({ icon: Icon, title, count, color, description }) => (
    <div className="bg-tertiary rounded-lg shadow-lg transition-all duration-300 hover:shadow-xl">
      <div className="p-6">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center">
            <div className={`p-3 rounded-full bg-${color}-100 mr-3`}>
              <Icon size={20} className={`text-${color}-600`} />
            </div>
            <div>
              <p className="text-gray-800 text-sm font-medium">{title}</p>
              <h3 className="text-gray-900 text-xl font-bold">{count}</h3>
            </div>
          </div>
          <div className="text-right">
            <p className="text-gray-700 text-xs">Últimas 24h</p>
            <p className={`text-${count > 5 ? 'red' : 'green'}-600 text-sm font-medium`}>
              {count > 5 ? '+' : '-'}{Math.abs(count - 5)}
            </p>
          </div>
        </div>
        <p className="text-gray-600 text-sm">{description}</p>
      </div>
    </div>
  );

  const AlertTable = ({ title, alerts, icon: Icon, color }) => (
    <div className="bg-tertiary rounded-lg shadow-lg p-6">
      <div className="flex justify-between items-center mb-6">
        <div className="flex items-center">
          <div className={`p-2 rounded-full bg-${color}-100 mr-3`}>
            <Icon size={18} className={`text-${color}-600`} />
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
              <th className="pb-2 font-medium">Detalhes</th>
              <th className="pb-2 font-medium">Data</th>
              <th className="pb-2 font-medium">Severidade</th>
              <th className="pb-2 font-medium">Ações</th>
            </tr>
          </thead>
          <tbody className="text-sm">
            {alerts.map((alert, index) => (
              <tr key={index} className="border-b border-gray-300 text-gray-900">
                <td className="py-3">#{alert.id}</td>
                <td className="py-3">
                  <div className="flex items-center">
                    <div className="w-6 h-6 rounded-full bg-gray-300 flex items-center justify-center mr-2">
                      <User size={12} className="text-gray-700" />
                    </div>
                    {alert.user}
                  </div>
                </td>
                <td className="py-3 max-w-xs truncate">{alert.details}</td>
                <td className="py-3 text-gray-700">{alert.date}</td>
                <td className="py-3">
                  <span className={`px-2 py-1 rounded-full text-xs ${
                    alert.severity === 'high' ? 'bg-red-100 text-red-800' : 
                    alert.severity === 'medium' ? 'bg-yellow-100 text-yellow-800' : 
                    'bg-blue-100 text-blue-800'
                  }`}>
                    {alert.severity === 'high' ? 'Alta' : 
                     alert.severity === 'medium' ? 'Média' : 'Baixa'}
                  </span>
                </td>
                <td className="py-3 text-right">
                  <div className="flex space-x-2 justify-end">
                    <button 
                      onClick={() => viewAlertDetails(alert)}
                      className="text-primary hover:text-blue-700"
                    >
                      <Eye size={16} />
                    </button>
                    <button 
                      onClick={() => handleAlertAction(alert.id, 'resolve')}
                      className="text-green-600 hover:text-green-800"
                    >
                      <CheckCircle size={16} />
                    </button>
                    <button 
                      onClick={() => handleAlertAction(alert.id, 'ignore')}
                      className="text-red-600 hover:text-red-800"
                    >
                      <XCircle size={16} />
                    </button>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div className="mt-4 flex justify-between items-center text-sm">
        <div className="text-gray-700">
          Mostrando <span className="text-gray-900">1-{Math.min(5, alerts.length)}</span> de <span className="text-gray-900">{alerts.length}</span> alertas
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

  const AlertDetailModal = () => {
    if (!selectedAlert) return null;

    return (
      <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
        <div className="bg-tertiary rounded-lg shadow-xl w-full max-w-2xl">
          <div className="p-6">
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-gray-900 text-xl font-bold">Detalhes do Alerta</h3>
              <button 
                onClick={() => setShowAlertDetails(false)}
                className="text-gray-500 hover:text-gray-700"
              >
                <XCircle size={20} />
              </button>
            </div>
            
            <div className="mb-6">
              <div className="flex items-center mb-4">
                <div className={`p-2 rounded-full bg-${
                  selectedAlert.severity === 'high' ? 'red' : 
                  selectedAlert.severity === 'medium' ? 'yellow' : 'blue'
                }-100 mr-3`}>
                  <AlertTriangle size={18} className={`text-${
                    selectedAlert.severity === 'high' ? 'red' : 
                    selectedAlert.severity === 'medium' ? 'yellow' : 'blue'
                  }-600`} />
                </div>
                <div>
                  <p className="text-gray-700 text-sm">ID #{selectedAlert.id}</p>
                  <p className="text-gray-900 font-bold">{selectedAlert.user}</p>
                </div>
              </div>
              
              <div className="bg-background-tertiary rounded-lg p-4 mb-4">
                <h4 className="text-gray-900 font-medium mb-2">Detalhes</h4>
                <p className="text-gray-800">{selectedAlert.details}</p>
              </div>
              
              <div className="grid grid-cols-2 gap-4 mb-4">
                <div>
                  <p className="text-gray-700 text-sm">Data de Detecção</p>
                  <p className="text-gray-900">{selectedAlert.date}</p>
                </div>
                <div>
                  <p className="text-gray-700 text-sm">Severidade</p>
                  <span className={`px-2 py-1 rounded-full text-xs ${
                    selectedAlert.severity === 'high' ? 'bg-red-100 text-red-800' : 
                    selectedAlert.severity === 'medium' ? 'bg-yellow-100 text-yellow-800' : 
                    'bg-blue-100 text-blue-800'
                  }`}>
                    {selectedAlert.severity === 'high' ? 'Alta' : 
                     selectedAlert.severity === 'medium' ? 'Média' : 'Baixa'}
                  </span>
                </div>
              </div>
              
              {selectedAlert.relatedData && (
                <div className="bg-background-tertiary rounded-lg p-4 mb-4">
                  <h4 className="text-gray-900 font-medium mb-2">Dados Relacionados</h4>
                  <div className="space-y-2">
                    {Object.entries(selectedAlert.relatedData).map(([key, value], index) => (
                      <div key={index} className="flex justify-between">
                        <span className="text-gray-700">{key}:</span>
                        <span className="text-gray-900 font-medium">{value}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}
              
              {selectedAlert.recommendations && (
                <div className="bg-background-tertiary rounded-lg p-4">
                  <h4 className="text-gray-900 font-medium mb-2">Recomendações</h4>
                  <ul className="list-disc pl-5 space-y-1">
                    {selectedAlert.recommendations.map((rec, index) => (
                      <li key={index} className="text-gray-800">{rec}</li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
            
            <div className="flex justify-end space-x-3">
              <button 
                onClick={() => {
                  handleAlertAction(selectedAlert.id, 'ignore');
                  setShowAlertDetails(false);
                }}
                className="px-4 py-2 rounded-lg bg-gray-200 text-gray-800 hover:bg-gray-300"
              >
                Ignorar
              </button>
              <button 
                onClick={() => {
                  handleAlertAction(selectedAlert.id, 'resolve');
                  setShowAlertDetails(false);
                }}
                className="px-4 py-2 rounded-lg bg-primary text-white hover:bg-blue-700"
              >
                Marcar como Resolvido
              </button>
            </div>
          </div>
        </div>
      </div>
    );
  };

  return (
    <div className="container mx-auto p-4 md:p-6">
      <Head>
        <title>Alertas de Segurança | Admin</title>
      </Head>
      
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center mb-6 md:mb-8">
        <div>
          <h1 className="text-white text-xl md:text-2xl font-bold mb-1 md:mb-2">Alertas de Segurança</h1>
          <p className="text-gray-400 text-sm">Monitoramento de atividades suspeitas</p>
        </div>
        <div className="flex mt-4 md:mt-0 space-x-2 md:space-x-4">
          <PeriodSelector />
          <button
            onClick={fetchAlertsData}
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
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 md:gap-6 mb-6 md:mb-8">
            <AlertCard
              icon={Users}
              title="Múltiplos Cadastros no IP"
              count={alertsData?.summary?.ipAlertsCount || 0}
              color="red"
              description="Usuários diferentes registrados no mesmo endereço IP"
            />
            <AlertCard
              icon={Clock}
              title="Depósito + Saque Rápido"
              count={alertsData?.summary?.withdrawalAlertsCount || 0}
              color="yellow"
              description="Depósitos pendentes seguidos de solicitação de saque"
            />
            <AlertCard
              icon={Gift}
              title="Bônus + Saque no Mesmo Dia"
              count={alertsData?.summary?.bonusAlertsCount || 0}
              color="blue"
              description="Recebimento de bônus e solicitação de saque no mesmo dia"
            />
          </div>

          <div className="space-y-6 mb-8">
            <AlertTable
              title="Múltiplos Cadastros no Mesmo IP"
              alerts={ipAlerts}
              icon={Users}
              color="red"
            />
            
            <AlertTable
              title="Depósitos Pendentes + Saque Rápido"
              alerts={withdrawalAlerts}
              icon={Clock}
              color="yellow"
            />
            
            <AlertTable
              title="Bônus + Saque no Mesmo Dia"
              alerts={bonusAlerts}
              icon={Gift}
              color="blue"
            />
          </div>

          {showAlertDetails && <AlertDetailModal />}
        </>
      )}
    </div>
  );
};

export default AlertsPage;
