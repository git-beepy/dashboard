import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import axios from 'axios';
import { Calendar, DollarSign, Clock, Check, AlertTriangle } from 'lucide-react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, LineChart, Line } from 'recharts';

const AmbassadorInstallments = () => {
  const { user, API_BASE_URL } = useAuth();
  const [installments, setInstallments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [summary, setSummary] = useState({
    total_installments: 0,
    pending_installments: 0,
    paid_installments: 0,
    overdue_installments: 0,
    total_pending_value: 0,
    total_paid_value: 0,
    total_overdue_value: 0
  });

  useEffect(() => {
    fetchInstallments();
    fetchSummary();
  }, []);

  const fetchInstallments = async () => {
    try {
      setLoading(true);
      const response = await axios.get(`${API_BASE_URL}/commissions/installments`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });
      
      setInstallments(response.data);
    } catch (error) {
      console.error('Erro ao buscar parcelas:', error);
      setInstallments([]);
    } finally {
      setLoading(false);
    }
  };

  const fetchSummary = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/commissions/installments/summary`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });
      
      setSummary(response.data);
    } catch (error) {
      console.error('Erro ao buscar resumo:', error);
    }
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'pago':
        return <Check className="h-4 w-4 text-green-600" />;
      case 'atrasado':
        return <AlertTriangle className="h-4 w-4 text-red-600" />;
      default:
        return <Clock className="h-4 w-4 text-yellow-600" />;
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'pago':
        return 'bg-green-100 text-green-800';
      case 'atrasado':
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-yellow-100 text-yellow-800';
    }
  };

  const getStatusText = (status) => {
    switch (status) {
      case 'pago':
        return 'Pago';
      case 'atrasado':
        return 'Atrasado';
      default:
        return 'Pendente';
    }
  };

  const formatDate = (dateString) => {
    if (!dateString) return 'Data não informada';
    try {
      const date = new Date(dateString);
      return date.toLocaleDateString('pt-BR');
    } catch {
      return 'Data inválida';
    }
  };

  const generateChartsData = () => {
    // Dados mensais das parcelas
    const monthlyData = {};
    const currentDate = new Date();
    
    // Inicializar últimos 6 meses
    for (let i = 5; i >= 0; i--) {
      const date = new Date(currentDate.getFullYear(), currentDate.getMonth() - i, 1);
      const monthKey = date.toLocaleDateString('pt-BR', { month: 'short', year: 'numeric' });
      monthlyData[monthKey] = { pending: 0, paid: 0, total: 0 };
    }

    installments.forEach(installment => {
      const dueDate = new Date(installment.dueDate);
      const monthKey = dueDate.toLocaleDateString('pt-BR', { month: 'short', year: 'numeric' });
      
      if (monthlyData[monthKey]) {
        const value = installment.value || 0;
        monthlyData[monthKey].total += value;
        
        if (installment.status === 'pago') {
          monthlyData[monthKey].paid += value;
        } else {
          monthlyData[monthKey].pending += value;
        }
      }
    });

    const monthlyChartData = Object.entries(monthlyData).map(([month, data]) => ({
      month,
      pendente: data.pending,
      pago: data.paid,
      total: data.total
    }));

    // Dados por parcela
    const installmentData = { 1: 0, 2: 0, 3: 0 };
    installments.forEach(installment => {
      const number = installment.installmentNumber || 1;
      installmentData[number] += installment.value || 0;
    });

    const installmentChartData = Object.entries(installmentData).map(([number, value]) => ({
      parcela: `${number}ª Parcela`,
      valor: value
    }));

    return {
      monthlyChartData,
      installmentChartData
    };
  };

  if (loading) {
    return (
      <div className="p-6">
        <div className="animate-pulse">
          <div className="h-8 bg-gray-200 rounded w-1/4 mb-6"></div>
          <div className="h-64 bg-gray-200 rounded"></div>
        </div>
      </div>
    );
  }

  return (
    <div className="p-6">
      <div className="flex flex-col lg:flex-row lg:justify-between lg:items-center mb-6 space-y-4 lg:space-y-0">
        <h1 className="text-2xl lg:text-3xl font-bold text-gray-900">Minhas Comissões</h1>
        <p className="text-gray-600">Acompanhe suas parcelas de comissão</p>
      </div>

      {/* Cards de resumo */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-6">
        <div className="bg-white p-6 rounded-lg shadow-md">
          <div className="flex items-center">
            <DollarSign className="h-8 w-8 text-blue-600" />
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Total Esperado</p>
              <p className="text-2xl font-bold text-gray-900">
                R$ {(summary.total_pending_value + summary.total_paid_value).toLocaleString('pt-BR', { minimumFractionDigits: 2 })}
              </p>
              <p className="text-sm text-gray-500">{summary.total_installments} parcelas</p>
            </div>
          </div>
        </div>

        <div className="bg-white p-6 rounded-lg shadow-md">
          <div className="flex items-center">
            <Check className="h-8 w-8 text-green-600" />
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Já Recebido</p>
              <p className="text-2xl font-bold text-gray-900">
                R$ {summary.total_paid_value.toLocaleString('pt-BR', { minimumFractionDigits: 2 })}
              </p>
              <p className="text-sm text-gray-500">{summary.paid_installments} parcelas</p>
            </div>
          </div>
        </div>

        <div className="bg-white p-6 rounded-lg shadow-md">
          <div className="flex items-center">
            <Clock className="h-8 w-8 text-yellow-600" />
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">A Receber</p>
              <p className="text-2xl font-bold text-gray-900">
                R$ {summary.total_pending_value.toLocaleString('pt-BR', { minimumFractionDigits: 2 })}
              </p>
              <p className="text-sm text-gray-500">{summary.pending_installments} parcelas</p>
            </div>
          </div>
        </div>

        <div className="bg-white p-6 rounded-lg shadow-md">
          <div className="flex items-center">
            <AlertTriangle className="h-8 w-8 text-red-600" />
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Em Atraso</p>
              <p className="text-2xl font-bold text-gray-900">
                R$ {summary.total_overdue_value.toLocaleString('pt-BR', { minimumFractionDigits: 2 })}
              </p>
              <p className="text-sm text-gray-500">{summary.overdue_installments} parcelas</p>
            </div>
          </div>
        </div>
      </div>



      {/* Tabela de parcelas */}
      <div className="bg-white rounded-lg shadow-md overflow-hidden">
        <div className="px-6 py-4 border-b border-gray-200">
          <h3 className="text-lg font-semibold text-gray-900">Suas Parcelas</h3>
        </div>
        
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Cliente
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Parcela
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Valor
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Vencimento
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Status
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Pagamento
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {installments.map((installment) => (
                <tr key={installment.id}>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm font-medium text-gray-900">
                      {installment.clientName || 'Cliente não informado'}
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm text-gray-900">
                      {installment.installmentNumber}ª de 3
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm font-medium text-gray-900">
                      R$ {(installment.value || 0).toLocaleString('pt-BR', { minimumFractionDigits: 2 })}
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm text-gray-900">
                      {formatDate(installment.dueDate)}
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getStatusColor(installment.status)}`}>
                      {getStatusIcon(installment.status)}
                      <span className="ml-1">{getStatusText(installment.status)}</span>
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm text-gray-900">
                      {installment.paymentDate ? formatDate(installment.paymentDate) : '-'}
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {installments.length === 0 && (
          <div className="text-center py-12">
            <Calendar className="mx-auto h-12 w-12 text-gray-400" />
            <h3 className="mt-2 text-sm font-medium text-gray-900">Nenhuma parcela encontrada</h3>
            <p className="mt-1 text-sm text-gray-500">
              Suas parcelas de comissão aparecerão aqui quando você tiver indicações aprovadas.
            </p>
          </div>
        )}
      </div>
    </div>
  );
};

export default AmbassadorInstallments;

