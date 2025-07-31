import React, { useState, useEffect } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import axios from 'axios';
import { Calendar, DollarSign, CheckCircle, Clock, AlertTriangle, TrendingUp, Eye } from 'lucide-react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, LineChart, Line, PieChart, Pie, Cell } from 'recharts';

const AmbassadorCommissionView = () => {
  const { user, API_BASE_URL } = useAuth();
  const [installments, setInstallments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [summary, setSummary] = useState({});
  const [showDetails, setShowDetails] = useState(false);

  useEffect(() => {
    fetchInstallments();
    fetchSummary();
  }, []);

  const fetchInstallments = async () => {
    try {
      setLoading(true);
      const response = await axios.get(`${API_BASE_URL}/commission-installments`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });
      
      setInstallments(response.data.installments || []);
    } catch (error) {
      console.error('Erro ao buscar parcelas:', error);
      setInstallments([]);
    } finally {
      setLoading(false);
    }
  };

  const fetchSummary = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/commission-installments/summary`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });
      
      setSummary(response.data);
    } catch (error) {
      console.error('Erro ao buscar resumo:', error);
      setSummary({});
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'pago':
        return 'bg-green-100 text-green-800';
      case 'pendente':
        return 'bg-yellow-100 text-yellow-800';
      case 'atrasado':
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'pago':
        return <CheckCircle className="h-4 w-4" />;
      case 'pendente':
        return <Clock className="h-4 w-4" />;
      case 'atrasado':
        return <AlertTriangle className="h-4 w-4" />;
      default:
        return <Clock className="h-4 w-4" />;
    }
  };

  const formatDate = (dateString) => {
    if (!dateString) return 'Data não informada';
    const date = new Date(dateString);
    return date.toLocaleDateString('pt-BR');
  };

  const formatCurrency = (value) => {
    return new Intl.NumberFormat('pt-BR', {
      style: 'currency',
      currency: 'BRL'
    }).format(value || 0);
  };

  const generateChartsData = () => {
    // Dados por status
    const statusData = {
      'pago': 0,
      'pendente': 0,
      'atrasado': 0
    };

    installments.forEach(installment => {
      const status = installment.status || 'pendente';
      statusData[status] = (statusData[status] || 0) + 1;
    });

    const statusChartData = Object.entries(statusData).map(([name, value]) => ({
      name: name.charAt(0).toUpperCase() + name.slice(1),
      value
    }));

    // Dados por mês de vencimento
    const monthlyData = {};
    installments.forEach(installment => {
      if (installment.due_date) {
        const date = new Date(installment.due_date);
        const monthKey = date.toLocaleDateString('pt-BR', { month: 'short', year: 'numeric' });
        if (!monthlyData[monthKey]) {
          monthlyData[monthKey] = { count: 0, value: 0 };
        }
        monthlyData[monthKey].count++;
        monthlyData[monthKey].value += installment.value || 0;
      }
    });

    const monthlyChartData = Object.entries(monthlyData)
      .map(([month, data]) => ({
        month,
        count: data.count,
        value: data.value
      }))
      .sort((a, b) => new Date(a.month) - new Date(b.month));

    return {
      statusChartData,
      monthlyChartData
    };
  };

  const getNextPayments = () => {
    const now = new Date();
    return installments
      .filter(installment => installment.status === 'pendente')
      .sort((a, b) => new Date(a.due_date) - new Date(b.due_date))
      .slice(0, 3);
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

      </div>

      {/* Cards de resumo */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6 justify-items-center">
        <div className="bg-white p-6 rounded-lg shadow-md">
          <div className="flex items-center">
            <DollarSign className="h-8 w-8 text-blue-600" />
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Total a Receber</p>
              <p className="text-2xl font-bold text-gray-900">
                {formatCurrency(summary.total_value)}
              </p>
              <p className="text-sm text-gray-500">
                {summary.total_installments || 0} parcelas
              </p>
            </div>
          </div>
        </div>

        <div className="bg-white p-6 rounded-lg shadow-md">
          <div className="flex items-center">
            <CheckCircle className="h-8 w-8 text-green-600" />
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Já Recebido</p>
              <p className="text-2xl font-bold text-gray-900">
                {formatCurrency(summary.paid_value)}
              </p>
              <p className="text-sm text-gray-500">
                {summary.paid_installments || 0} parcelas
              </p>
            </div>
          </div>
        </div>

        <div className="bg-white p-6 rounded-lg shadow-md">
          <div className="flex items-center">
            <Clock className="h-8 w-8 text-yellow-600" />
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Pendente</p>
              <p className="text-2xl font-bold text-gray-900">
                {formatCurrency(summary.pending_value)}
              </p>
              <p className="text-sm text-gray-500">
                {summary.pending_installments || 0} parcelas
              </p>
            </div>
          </div>
        </div>


      </div>



      {/* Gráficos */}
      {showDetails && (
        <div className="mb-6">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Gráfico por Status */}
            <div className="bg-white p-6 rounded-lg shadow-md">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Status das Parcelas</h3>
              <ResponsiveContainer width="100%" height={300}>
                <PieChart>
                  <Pie
                    data={generateChartsData().statusChartData}
                    cx="50%"
                    cy="50%"
                    outerRadius={100}
                    fill="#8884d8"
                    dataKey="value"
                    label={({ name, value }) => `${name}: ${value}`}
                  >
                    {generateChartsData().statusChartData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={['#10B981', '#F59E0B', '#EF4444'][index % 3]} />
                    ))}
                  </Pie>
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>
            </div>

            {/* Gráfico Mensal */}
            <div className="bg-white p-6 rounded-lg shadow-md">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Comissões por Mês</h3>
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={generateChartsData().monthlyChartData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="month" />
                  <YAxis />
                  <Tooltip formatter={(value) => [formatCurrency(value), 'Valor Total']} />
                  <Bar dataKey="value" fill="#3B82F6" />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>
        </div>
      )}

      {/* Tabela de Parcelas */}
      {showDetails && (
        <div className="bg-white rounded-lg shadow-md overflow-hidden">
          <div className="px-6 py-4 border-b border-gray-200">
            <h3 className="text-lg font-semibold text-gray-900">Histórico de Parcelas</h3>
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

                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {installments.map((installment) => (
                  <tr key={installment.id}>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm font-medium text-gray-900">
                        {installment.client_name}
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm text-gray-900">
                        {installment.installment_number}/3
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm font-medium text-gray-900">
                        {formatCurrency(installment.value)}
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm text-gray-900">
                        {formatDate(installment.due_date)}
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getStatusColor(installment.status)}`}>
                        {getStatusIcon(installment.status)}
                        <span className="ml-1">{installment.status}</span>
                      </span>
                    </td>

                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {installments.length === 0 && (
            <div className="text-center py-12">
              <DollarSign className="mx-auto h-12 w-12 text-gray-400" />
              <h3 className="mt-2 text-sm font-medium text-gray-900">Nenhuma comissão encontrada</h3>
              <p className="mt-1 text-sm text-gray-500">
                Você ainda não possui comissões registradas.
              </p>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default AmbassadorCommissionView;

