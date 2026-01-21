import { useEffect, useState } from "react";
import Head from "next/head";
import { ToastContainer, toast } from "react-toastify";
import { 
  DollarSign, 
  ArrowDownCircle,
  Calendar,
  Filter,
  ChevronDown,
  Search,
  Download,
  Eye,
  User,
  CheckCircle,
  XCircle,
  AlertTriangle,
  Clock,
  FileText,
  AlertCircle,
  Info
} from 'lucide-react';
import LoadCenter from "@/components/icons/LoadCenter";
import { toMoney } from "@/helpers/functions";
import TransactionApprovalAPI from "@/services/TransactionApprovalAPI";
import moment from "moment";

const TransactionApprovalPage = function() {
  const [loading, setLoading] = useState(true);
  const [selectedPeriod, setSelectedPeriod] = useState('day');
  const [showDropdown, setShowDropdown] = useState(false);
  const [activeTab, setActiveTab] = useState('deposits');
  const [pendingDeposits, setPendingDeposits] = useState([]);
  const [pendingWithdrawals, setPendingWithdrawals] = useState([]);
  const [suspiciousWithdrawals, setSuspiciousWithdrawals] = useState([]);
  const [decisionLogs, setDecisionLogs] = useState([]);
  const [selectedTransaction, setSelectedTransaction] = useState(null);
  const [showTransactionDetails, setShowTransactionDetails] = useState(false);
  const [approvalNote, setApprovalNote] = useState('');
  const [filterStatus, setFilterStatus] = useState('all');

  const transactionApprovalAPI = new TransactionApprovalAPI();

  useEffect(() => {
    fetchTransactionData();
  }, [selectedPeriod, activeTab, filterStatus]);

  const fetchTransactionData = async () => {
    try {
      setLoading(true);
      const res = await transactionApprovalAPI.getTransactionData(selectedPeriod, activeTab, filterStatus);
      if (res?.status === 200 && res?.data) {
        setPendingDeposits(res.data.pendingDeposits);
        setPendingWithdrawals(res.data.pendingWithdrawals);
        setSuspiciousWithdrawals(res.data.suspiciousWithdrawals);
        setDecisionLogs(res.data.decisionLogs);
      } else {
        toast.error("Erro ao carregar dados de transações");
      }
    } catch (error) {
      console.error("Error fetching transaction data:", error);
      toast.error("Erro ao carregar dados de transações");
    } finally {
      setLoading(false);
    }
  };

  const handleTransactionAction = async (transactionId, action) => {
    try {
      setLoading(true);
      const res = await transactionApprovalAPI.updateTransactionStatus(
        transactionId, 
        action, 
        activeTab === 'deposits' ? 'deposit' : 'withdrawal',
        approvalNote
      );
      if (res?.status === 200) {
        toast.success(`Transação ${action === 'approve' ? 'aprovada' : action === 'reject' ? 'recusada' : 'marcada em análise'} com sucesso`);
        fetchTransactionData();
        setShowTransactionDetails(false);
        setApprovalNote('');
      } else {
        toast.error("Erro ao atualizar status da transação");
      }
    } catch (error) {
      console.error("Error updating transaction status:", error);
      toast.error("Erro ao atualizar status da transação");
    } finally {
      setLoading(false);
    }
  };

  const viewTransactionDetails = (transaction) => {
    setSelectedTransaction(transaction);
    setShowTransactionDetails(true);
  };

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

  const StatusBadge = ({ status }) => {
    let bgColor, textColor, statusText;
    
    switch (status) {
      case 'pending':
        bgColor = 'bg-yellow-100';
        textColor = 'text-yellow-800';
        statusText = 'Pendente';
        break;
      case 'approved':
        bgColor = 'bg-green-100';
        textColor = 'text-green-800';
        statusText = 'Aprovado';
        break;
      case 'rejected':
        bgColor = 'bg-red-100';
        textColor = 'text-red-800';
        statusText = 'Recusado';
        break;
      case 'analyzing':
        bgColor = 'bg-blue-100';
        textColor = 'text-blue-800';
        statusText = 'Em Análise';
        break;
      default:
        bgColor = 'bg-gray-100';
        textColor = 'text-gray-800';
        statusText = 'Desconhecido';
    }
    
    return (
      <span className={`px-2 py-1 rounded-full text-xs ${bgColor} ${textColor}`}>
        {statusText}
      </span>
    );
  };

  const TransactionTable = ({ title, transactions, type, suspicious = false }) => (
    <div className="bg-tertiary rounded-lg shadow-lg p-6">
      <div className="flex justify-between items-center mb-6">
        <div className="flex items-center">
          <div className={`p-2 rounded-full ${suspicious ? 'bg-red-100' : 'bg-background-tertiary'} mr-3`}>
            {type === 'deposit' ? 
              <DollarSign size={18} className={suspicious ? 'text-red-600' : 'text-primary'} /> : 
              <ArrowDownCircle size={18} className={suspicious ? 'text-red-600' : 'text-primary'} />
            }
          </div>
          <h3 className="text-gray-900 text-lg font-medium">{title}</h3>
          {suspicious && (
            <div className="ml-2 bg-red-100 text-red-800 text-xs px-2 py-1 rounded-full">
              Suspeito
            </div>
          )}
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
          <div className="relative">
            <select 
              className="pl-3 pr-8 py-1 rounded-lg bg-background-tertiary text-gray-900 text-sm focus:outline-none focus:ring-1 focus:ring-primary appearance-none"
              value={filterStatus}
              onChange={(e) => setFilterStatus(e.target.value)}
            >
              <option value="all">Todos</option>
              <option value="pending">Pendentes</option>
              <option value="analyzing">Em Análise</option>
              <option value="approved">Aprovados</option>
              <option value="rejected">Recusados</option>
            </select>
            <ChevronDown size={14} className="absolute right-2 top-1/2 transform -translate-y-1/2 text-gray-600 pointer-events-none" />
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
              <th className="pb-2 font-medium">Ações</th>
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
                  <StatusBadge status={transaction.status} />
                </td>
                <td className="py-3">
                  <div className="flex space-x-2 justify-end">
                    <button 
                      onClick={() => viewTransactionDetails(transaction)}
                      className="text-primary hover:text-blue-700"
                      title="Ver detalhes"
                    >
                      <Eye size={16} />
                    </button>
                    {transaction.status === 'pending' && (
                      <>
                        <button 
                          onClick={() => handleTransactionAction(transaction.id, 'approve')}
                          className="text-green-600 hover:text-green-800"
                          title="Aprovar"
                        >
                          <CheckCircle size={16} />
                        </button>
                        <button 
                          onClick={() => handleTransactionAction(transaction.id, 'reject')}
                          className="text-red-600 hover:text-red-800"
                          title="Recusar"
                        >
                          <XCircle size={16} />
                        </button>
                        <button 
                          onClick={() => handleTransactionAction(transaction.id, 'analyze')}
                          className="text-blue-600 hover:text-blue-800"
                          title="Marcar para análise"
                        >
                          <AlertCircle size={16} />
                        </button>
                      </>
                    )}
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div className="mt-4 flex justify-between items-center text-sm">
        <div className="text-gray-700">
          Mostrando <span className="text-gray-900">1-{Math.min(10, transactions.length)}</span> de <span className="text-gray-900">{transactions.length}</span> transações
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

  const DecisionLogTable = ({ logs }) => (
    <div className="bg-tertiary rounded-lg shadow-lg p-6">
      <div className="flex justify-between items-center mb-6">
        <div className="flex items-center">
          <div className="p-2 rounded-full bg-background-tertiary mr-3">
            <FileText size={18} className="text-primary" />
          </div>
          <h3 className="text-gray-900 text-lg font-medium">Log de Decisões</h3>
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
              <th className="pb-2 font-medium">Transação</th>
              <th className="pb-2 font-medium">Tipo</th>
              <th className="pb-2 font-medium">Decisão</th>
              <th className="pb-2 font-medium">Operador</th>
              <th className="pb-2 font-medium">Data</th>
              <th className="pb-2 font-medium">Ações</th>
            </tr>
          </thead>
          <tbody className="text-sm">
            {logs.map((log, index) => (
              <tr key={index} className="border-b border-gray-300 text-gray-900">
                <td className="py-3">#{log.id}</td>
                <td className="py-3">#{log.transactionId}</td>
                <td className="py-3">{log.type === 'deposit' ? 'Depósito' : 'Saque'}</td>
                <td className="py-3">
                  <StatusBadge status={log.decision} />
                </td>
                <td className="py-3">
                  <div className="flex items-center">
                    <div className="w-6 h-6 rounded-full bg-gray-300 flex items-center justify-center mr-2">
                      <User size={12} className="text-gray-700" />
                    </div>
                    {log.operator}
                  </div>
                </td>
                <td className="py-3 text-gray-700">{log.date}</td>
                <td className="py-3 text-right">
                  <button 
                    onClick={() => {
                      // View log details
                      toast.info("Detalhes do log: " + log.notes);
                    }}
                    className="text-primary hover:text-blue-700"
                  >
                    <Info size={16} />
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div className="mt-4 flex justify-between items-center text-sm">
        <div className="text-gray-700">
          Mostrando <span className="text-gray-900">1-{Math.min(10, logs.length)}</span> de <span className="text-gray-900">{logs.length}</span> logs
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

  const TransactionDetailModal = () => {
    if (!selectedTransaction) return null;

    return (
      <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
        <div className="bg-tertiary rounded-lg shadow-xl w-full max-w-2xl">
          <div className="p-6">
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-gray-900 text-xl font-bold">Detalhes da Transação</h3>
              <button 
                onClick={() => setShowTransactionDetails(false)}
                className="text-gray-500 hover:text-gray-700"
              >
                <XCircle size={20} />
              </button>
            </div>
            
            <div className="mb-6">
              <div className="flex items-center mb-4">
                <div className="p-2 rounded-full bg-background-tertiary mr-3">
                  {selectedTransaction.type === 'deposit' ? 
                    <DollarSign size={18} className="text-primary" /> : 
                    <ArrowDownCircle size={18} className="text-primary" />
                  }
                </div>
                <div>
                  <p className="text-gray-700 text-sm">ID #{selectedTransaction.id}</p>
                  <p className="text-gray-900 font-bold">{selectedTransaction.user}</p>
                </div>
              </div>
              
              <div className="grid grid-cols-2 gap-4 mb-4">
                <div className="bg-background-tertiary rounded-lg p-4">
                  <p className="text-gray-700 text-sm">Valor</p>
                  <p className="text-gray-900 text-lg font-bold">{toMoney(selectedTransaction.amount)}</p>
                </div>
                <div className="bg-background-tertiary rounded-lg p-4">
                  <p className="text-gray-700 text-sm">Status</p>
                  <StatusBadge status={selectedTransaction.status} />
                </div>
                <div className="bg-background-tertiary rounded-lg p-4">
                  <p className="text-gray-700 text-sm">Data</p>
                  <p className="text-gray-900">{selectedTransaction.date}</p>
                </div>
                <div className="bg-background-tertiary rounded-lg p-4">
                  <p className="text-gray-700 text-sm">Método</p>
                  <p className="text-gray-900">{selectedTransaction.method || 'Não especificado'}</p>
                </div>
              </div>
              
              {selectedTransaction.suspicious && (
                <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-4">
                  <div className="flex items-center mb-2">
                    <AlertTriangle size={16} className="text-red-600 mr-2" />
                    <h4 className="text-red-800 font-medium">Alerta de Transação Suspeita</h4>
                  </div>
                  <p className="text-red-700">{selectedTransaction.suspiciousReason}</p>
                </div>
              )}
              
              {selectedTransaction.history && (
                <div className="bg-background-tertiary rounded-lg p-4 mb-4">
                  <h4 className="text-gray-900 font-medium mb-2">Histórico de Decisões</h4>
                  <div className="space-y-2">
                    {selectedTransaction.history.map((item, index) => (
                      <div key={index} className="flex items-start">
                        <div className="w-6 h-6 rounded-full bg-gray-300 flex items-center justify-center mr-2 mt-1">
                          <User size={12} className="text-gray-700" />
                        </div>
                        <div>
                          <div className="flex items-center">
                            <p className="text-gray-900 font-medium">{item.operator}</p>
                            <p className="text-gray-700 text-xs ml-2">{item.date}</p>
                          </div>
                          <p className="text-gray-800">{item.action}: {item.notes}</p>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
              
              {selectedTransaction.status === 'pending' && (
                <div className="mb-4">
                  <label className="block text-gray-700 text-sm font-medium mb-2">
                    Nota de Aprovação/Rejeição
                  </label>
                  <textarea
                    className="w-full px-3 py-2 text-gray-700 border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
                    rows="3"
                    placeholder="Adicione uma nota sobre sua decisão..."
                    value={approvalNote}
                    onChange={(e) => setApprovalNote(e.target.value)}
                  ></textarea>
                </div>
              )}
            </div>
            
            {selectedTransaction.status === 'pending' && (
              <div className="flex justify-end space-x-3">
                <button 
                  onClick={() => handleTransactionAction(selectedTransaction.id, 'reject')}
                  className="px-4 py-2 rounded-lg bg-red-500 text-white hover:bg-red-600"
                >
                  Recusar
                </button>
                <button 
                  onClick={() => handleTransactionAction(selectedTransaction.id, 'analyze')}
                  className="px-4 py-2 rounded-lg bg-blue-500 text-white hover:bg-blue-600"
                >
                  Em Análise
                </button>
                <button 
                  onClick={() => handleTransactionAction(selectedTransaction.id, 'approve')}
                  className="px-4 py-2 rounded-lg bg-green-500 text-white hover:bg-green-600"
                >
                  Aprovar
                </button>
              </div>
            )}
          </div>
        </div>
      </div>
    );
  };

  return (
    <div className="container mx-auto p-4 md:p-6">
      <Head>
        <title>Aprovação de Transações | Admin</title>
      </Head>
      
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center mb-6 md:mb-8">
        <div>
          <h1 className="text-white text-xl md:text-2xl font-bold mb-1 md:mb-2">Aprovação de Transações</h1>
          <p className="text-gray-400 text-sm">Gerenciamento de depósitos e saques pendentes</p>
        </div>
        <div className="flex mt-4 md:mt-0 space-x-2 md:space-x-4">
          <PeriodSelector />
          <button
            onClick={fetchTransactionData}
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

      <div className="mb-6">
        <div className="border-b border-gray-300">
          <nav className="flex -mb-px">
            <button
              onClick={() => setActiveTab('deposits')}
              className={`py-2 px-4 text-sm font-medium ${
                activeTab === 'deposits'
                  ? 'border-b-2 border-primary text-primary'
                  : 'text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              Depósitos Pendentes
            </button>
            <button
              onClick={() => setActiveTab('withdrawals')}
              className={`py-2 px-4 text-sm font-medium ${
                activeTab === 'withdrawals'
                  ? 'border-b-2 border-primary text-primary'
                  : 'text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              Saques Pendentes
            </button>
            <button
              onClick={() => setActiveTab('suspicious')}
              className={`py-2 px-4 text-sm font-medium ${
                activeTab === 'suspicious'
                  ? 'border-b-2 border-primary text-primary'
                  : 'text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              Saques Suspeitos
            </button>
            <button
              onClick={() => setActiveTab('logs')}
              className={`py-2 px-4 text-sm font-medium ${
                activeTab === 'logs'
                  ? 'border-b-2 border-primary text-primary'
                  : 'text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              Log de Decisões
            </button>
          </nav>
        </div>
      </div>

      {loading ? (
        <div className="flex justify-center items-center h-64">
          <LoadCenter />
        </div>
      ) : (
        <>
          {activeTab === 'deposits' && (
            <TransactionTable
              title="Depósitos Pendentes"
              transactions={pendingDeposits}
              type="deposit"
            />
          )}
          
          {activeTab === 'withdrawals' && (
            <TransactionTable
              title="Saques Pendentes"
              transactions={pendingWithdrawals}
              type="withdrawal"
            />
          )}
          
          {activeTab === 'suspicious' && (
            <TransactionTable
              title="Saques Suspeitos"
              transactions={suspiciousWithdrawals}
              type="withdrawal"
              suspicious={true}
            />
          )}
          
          {activeTab === 'logs' && (
            <DecisionLogTable logs={decisionLogs} />
          )}

          {showTransactionDetails && <TransactionDetailModal />}
        </>
      )}
    </div>
  );
};

export default TransactionApprovalPage;
