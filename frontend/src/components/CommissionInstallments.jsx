import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import axios from 'axios';
import { Calendar, DollarSign, Filter, CheckCircle, Clock, AlertTriangle, BarChart3, Eye, Trash2 } from 'lucide-react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell, LineChart, Line } from 'recharts';
import { useMemo } from 'react';

const CommissionInstallments = () => {
  const { user, API_BASE_URL } = useAuth();
  const [installments, setInstallments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showCharts, setShowCharts] = useState(false);
  const [filters, setFilters] = useState({
    status: '',
    ambassador_id: '',
    month: '',
    year: ''
  });
  const [summary, setSummary] = useState({});
  const [ambassadors, setAmbassadors] = useState([]);
  const chartsData = generateChartsData();
  const isAdmin = user?.role === 'admin';
  const currentYear = useMemo(() => new Date().getFullYear(), []);
  const years = useMemo(() =>
    Array.from({ length: 5 }, (_, i) => currentYear - 2 + i), [currentYear]);
  useEffect(() => {
    if (!user) return;

    fetchInstallments();
    fetchSummary();
    if (user.role === 'admin') {
      fetchAmbassadors();
    }
  }, [filters, user]);

  const fetchInstallments = async () => {
    try {
      setLoading(true);
      const params = new URLSearchParams();

      Object.entries(filters).forEach(([key, value]) => {
        if (value) {
          params.append(key, value);
        }
      });

      const response = await axios.get(`${API_BASE_URL}/commission-installments?${params}`, {
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
      const params = new URLSearchParams();
      if (filters.ambassador_id && isAdmin) {
        params.append('ambassador_id', filters.ambassador_id);
      }

      const response = await axios.get(`${API_BASE_URL}/commission-installments/summary?${params}`, {
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

  const fetchAmbassadors = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/users`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });

      const ambassadorUsers = response.data.filter(user => user.role === 'E' || user.role === 'embaixadora');
      setAmbassadors(ambassadorUsers);
    } catch (error) {
      console.error('Erro ao buscar embaixadoras:', error);
      setAmbassadors([]);
    }
  };

  const updateInstallmentStatus = async (installmentId, newStatus) => {
    try {
      await axios.put(`${API_BASE_URL}/commission-installments/${installmentId}/status`, {
        status: newStatus
      }, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });

      fetchInstallments();
      fetchSummary();
    } catch (error) {
      console.error('Erro ao atualizar status:', error);
      alert('Erro ao atualizar status da parcela');
    }
  };

  const deleteInstallment = async (installmentId) => {
    if (!window.confirm('Tem certeza que deseja excluir esta parcela? Esta ação não pode ser desfeita.')) {
      return;
    }

    try {
      await axios.delete(`${API_BASE_URL}/commission-installments/${installmentId}`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });

      fetchInstallments();
      fetchSummary();
      alert('Parcela excluída com sucesso');
    } catch (error) {
      console.error('Erro ao excluir parcela:', error);
      alert('Erro ao excluir parcela');
    }
  };

  const checkOverdueInstallments = async () => {
    try {
      await axios.post(`${API_BASE_URL}/commission-installments/check-overdue`, {}, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });

      fetchInstallments();
      fetchSummary();
      alert('Verificação de parcelas em atraso concluída');
    } catch (error) {
      console.error('Erro ao verificar parcelas em atraso:', error);
      alert('Erro ao verificar parcelas em atraso');
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

    // Dados por embaixadora
    const ambassadorData = {};
    installments.forEach(installment => {
      const ambassadorName = installment.ambassador_name || 'Não informado';
      if (!ambassadorData[ambassadorName]) {
        ambassadorData[ambassadorName] = { count: 0, value: 0 };
      }
      ambassadorData[ambassadorName].count++;
      ambassadorData[ambassadorName].value += installment.value || 0;
    });

    const ambassadorChartData = Object.entries(ambassadorData)
      .map(([name, data]) => ({
        ambassador: name,
        count: data.count,
        value: data.value
      }))
      .sort((a, b) => b.value - a.value)
      .slice(0, 10);

    return {
      statusChartData,
      monthlyChartData,
      ambassadorChartData
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

  const months = [
    { value: '1', label: 'Janeiro' },
    { value: '2', label: 'Fevereiro' },
    { value: '3', label: 'Março' },
    { value: '4', label: 'Abril' },
    { value: '5', label: 'Maio' },
    { value: '6', label: 'Junho' },
    { value: '7', label: 'Julho' },
    { value: '8', label: 'Agosto' },
    { value: '9', label: 'Setembro' },
    { value: '10', label: 'Outubro' },
    { value: '11', label: 'Novembro' },
    { value: '12', label: 'Dezembro' }
  ];

  return (
    <div className="p-6">
      <div className="flex flex-col lg:flex-row lg:justify-between lg:items-center mb-6 space-y-4 lg:space-y-0">
        <h1 className="text-2xl lg:text-3xl font-bold text-gray-900">Comissões Parceladas</h1>
        {isAdmin && (
          <div className="flex flex-col sm:flex-row space-y-2 sm:space-y-0 sm:space-x-3">
            <button
              onClick={() => setShowCharts(!showCharts)}
              className="bg-green-600 text-white px-3 py-2 rounded-lg flex items-center justify-center space-x-2 hover:bg-green-700 text-sm"
            >
              <BarChart3 className="h-4 w-4" />
              <span>{showCharts ? 'Ocultar Gráficos' : 'Mostrar Gráficos'}</span>
            </button>
            {isAdmin && (
              <button
                onClick={checkOverdueInstallments}
                className="bg-orange-600 text-white px-3 py-2 rounded-lg flex items-center justify-center space-x-2 hover:bg-orange-700 text-sm"
              >
                <AlertTriangle className="h-4 w-4" />
                <span>Verificar Atrasos</span>
              </button>
            )}
          </div>)}
      </div>

      {/* Cards de resumo */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-6">
        <div className="bg-white p-6 rounded-lg shadow-md">
          <div className="flex items-center">
            <DollarSign className="h-8 w-8 text-blue-600" />
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Total Parcelas</p>
              <p className="text-2xl font-bold text-gray-900">
                {summary.total_installments || 0}
              </p>
              <p className="text-sm text-gray-500">
                {formatCurrency(summary.total_value)}
              </p>
            </div>
          </div>
        </div>

        <div className="bg-white p-6 rounded-lg shadow-md">
          <div className="flex items-center">
            <CheckCircle className="h-8 w-8 text-green-600" />
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Pagas</p>
              <p className="text-2xl font-bold text-gray-900">
                {summary.paid_installments || 0}
              </p>
              <p className="text-sm text-gray-500">
                {formatCurrency(summary.paid_value)}
              </p>
            </div>
          </div>
        </div>

        <div className="bg-white p-6 rounded-lg shadow-md">
          <div className="flex items-center">
            <Clock className="h-8 w-8 text-yellow-600" />
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Pendentes</p>
              <p className="text-2xl font-bold text-gray-900">
                {summary.pending_installments || 0}
              </p>
              <p className="text-sm text-gray-500">
                {formatCurrency(summary.pending_value)}
              </p>
            </div>
          </div>
        </div>

        <div className="bg-white p-6 rounded-lg shadow-md">
          <div className="flex items-center">
            <AlertTriangle className="h-8 w-8 text-red-600" />
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Atrasadas</p>
              <p className="text-2xl font-bold text-gray-900">
                {summary.overdue_installments || 0}
              </p>
              <p className="text-sm text-gray-500">
                {formatCurrency(summary.overdue_value)}
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Filtros - Apenas para Admin */}
      {isAdmin && (
        <div className="bg-white p-6 rounded-lg shadow-md mb-6">
          <div className="flex items-center mb-4">
            <Filter className="h-5 w-5 text-gray-600 mr-2" />
            <h3 className="text-lg font-semibold text-gray-900">Filtros</h3>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Status</label>
              <select
                value={filters.status}
                onChange={(e) => setFilters({ ...filters, status: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="">Todos</option>
                <option value="pendente">Pendente</option>
                <option value="pago">Pago</option>
                <option value="atrasado">Atrasado</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Embaixadora</label>
              <select
                value={filters.ambassador_id}
                onChange={(e) => setFilters({ ...filters, ambassador_id: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="">Todas</option>
                {ambassadors.map(ambassador => (
                  <option key={ambassador.id} value={ambassador.id}>
                    {ambassador.name}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Mês</label>
              <select
                value={filters.month}
                onChange={(e) => setFilters({ ...filters, month: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="">Todos</option>
                {months.map(month => (
                  <option key={month.value} value={month.value}>
                    {month.label}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Ano</label>
              <select
                value={filters.year}
                onChange={(e) => setFilters({ ...filters, year: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="">Todos</option>
                {years.map(year => (
                  <option key={year} value={year}>
                    {year}
                  </option>
                ))}
              </select>
            </div>
          </div>
        </div>
      )}

      {/* Seção de Gráficos */}
      {showCharts && (
        <div className="mb-6">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Gráfico por Status */}
            <div className="bg-white p-6 rounded-lg shadow-md">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Parcelas por Status</h3>
              <ResponsiveContainer width="100%" height={300}>
                <PieChart>
                  <Pie
                    data={chartsData.statusChartData}
                    cx="50%"
                    cy="50%"
                    outerRadius={100}
                    fill="#8884d8"
                    dataKey="value"
                    label={({ name, value }) => `${name}: ${value}`}
                  >
                    {chartsData.statusChartData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={['#10B981', '#F59E0B', '#EF4444'][index % 3]} />
                    ))}
                  </Pie>
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>
            </div>

            {/* Gráfico Mensal */}
            <div className="bg-white p-6 rounded-lg shadow-md">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Parcelas por Mês de Vencimento</h3>
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={chartsData.monthlyChartData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="month" />
                  <YAxis />
                  <Tooltip formatter={(value, name) => [
                    name === 'value' ? formatCurrency(value) : value,
                    name === 'value' ? 'Valor Total' : 'Quantidade'
                  ]} />
                  <Bar dataKey="count" fill="#3B82F6" name="count" />
                </BarChart>
              </ResponsiveContainer>
            </div>

            {/* Gráfico por Embaixadora */}
            <div className="bg-white p-6 rounded-lg shadow-md lg:col-span-2">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Top Embaixadoras por Valor</h3>
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={chartsData.ambassadorChartData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="ambassador" angle={-45} textAnchor="end" height={100} />
                  <YAxis />
                  <Tooltip formatter={(value) => [formatCurrency(value), 'Valor Total']} />
                  <Bar dataKey="value" fill="#10B981" />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>
        </div>
      )}

      {/* Tabela de Parcelas */}
      {isAdmin && (
        <div className="bg-white rounded-lg shadow-md overflow-hidden">
          <div className="px-6 py-4 border-b border-gray-200">
            <h3 className="text-lg font-semibold text-gray-900">
              Parcelas de Comissão ({installments.length})
            </h3>
          </div>

          {installments.length > 0 ? (
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Embaixadora
                    </th>
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
                    {isAdmin && (
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Ações
                      </th>
                    )}
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {installments.map((installment) => (
                    <tr key={installment.id}>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm font-medium text-gray-900">
                          {installment.ambassador_name}
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm text-gray-900">
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
                      {isAdmin && (
                        <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                          <div className="flex space-x-2">
                            {installment.status !== 'pago' && (
                              <button
                                onClick={() => updateInstallmentStatus(installment.id, 'pago')}
                                className="text-green-600 hover:text-green-900"
                                title="Marcar como pago"
                              >
                                <CheckCircle className="h-4 w-4" />
                              </button>
                            )}
                            {installment.status === 'pago' && (
                              <button
                                onClick={() => updateInstallmentStatus(installment.id, 'pendente')}
                                className="text-yellow-600 hover:text-yellow-900"
                                title="Marcar como pendente"
                              >
                                <Clock className="h-4 w-4" />
                              </button>
                            )}
                            <button
                              onClick={() => deleteInstallment(installment.id)}
                              className="text-red-600 hover:text-red-900"
                              title="Excluir parcela"
                            >
                              <Trash2 className="h-4 w-4" />
                            </button>
                          </div>
                        </td>
                      )}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <div className="text-center py-12">
              <DollarSign className="mx-auto h-12 w-12 text-gray-400" />
              <h3 className="mt-2 text-sm font-medium text-gray-900">Nenhuma parcela encontrada</h3>
              <p className="mt-1 text-sm text-gray-500">
                Não há parcelas de comissão com os filtros selecionados.
              </p>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default CommissionInstallments;


