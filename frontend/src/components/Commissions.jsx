import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import axios from 'axios';
import { Plus, Edit, Trash2, DollarSign, BarChart3, Eye, ArrowRight, Calendar, Link } from 'lucide-react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell, LineChart, Line } from 'recharts';

const Commissions = () => {
  const { user, API_BASE_URL } = useAuth();
  const [commissions, setCommissions] = useState([]);
  const [indications, setIndications] = useState([]);
  const [installments, setInstallments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [editingCommission, setEditingCommission] = useState(null);
  const [showCharts, setShowCharts] = useState(false);
  const [showConnectedView, setShowConnectedView] = useState(false);
  const [selectedCommission, setSelectedCommission] = useState(null);
  const [formData, setFormData] = useState({
    ambassadorId: '',
    indicationId: '',
    value: '',
    status: 'pending'
  });

  useEffect(() => {
    fetchAllData();
  }, []);

  const fetchAllData = async () => {
    try {
      setLoading(true);
      await Promise.all([
        fetchCommissions(),
        fetchIndications(),
        fetchInstallments()
      ]);
    } catch (error) {
      console.error('Erro ao carregar dados:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchInstallments = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/commission-installments`, {
        withCredentials: true
      });
      setInstallments(response.data.installments || []);
    } catch (error) {
      console.error("Erro ao buscar parcelas:", error);
      setInstallments([]);
    }
  };

  const fetchIndications = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/indications`, {
        withCredentials: true
      });
      console.log('Resposta completa da API:', response.data); // Debug
      
      // Verificar se a resposta tem a estrutura esperada
      let indicationsData = [];
      if (Array.isArray(response.data)) {
        indicationsData = response.data;
      } else if (response.data && Array.isArray(response.data.indications)) {
        indicationsData = response.data.indications;
      } else if (response.data && response.data.data && Array.isArray(response.data.data)) {
        indicationsData = response.data.data;
      }
      
      console.log('Indicações processadas:', indicationsData); // Debug
      setIndications(indicationsData);
    } catch (error) {
      console.error('Erro ao buscar indicações:', error);
      setIndications([]); // Definir array vazio em caso de erro
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    try {
      if (editingCommission) {
        await axios.put(`${API_BASE_URL}/commissions/${editingCommission.id}`, formData, {
          withCredentials: true
        });
      } else {
        await axios.post(`${API_BASE_URL}/commissions`, formData, {
          withCredentials: true
        });
      }

      fetchCommissions();
      setShowModal(false);
      setEditingCommission(null);
      setFormData({
        ambassadorId: '',
        indicationId: '',
        value: '',
        status: 'pending'
      });
    } catch (error) {
      console.error('Erro ao salvar comissão:', error);
    }
  };

  const handleEdit = (commission) => {
    setEditingCommission(commission);
    setFormData({
      ambassadorId: commission.ambassadorId,
      indicationId: commission.indicationId,
      value: commission.value,
      status: commission.status
    });
    setShowModal(true);
  };

  const handleDelete = async (id) => {
    if (window.confirm('Tem certeza que deseja excluir esta comissão?')) {
      try {
        await axios.delete(`${API_BASE_URL}/commissions/${id}`, {
          withCredentials: true
        });
        fetchCommissions();
      } catch (error) {
        console.error('Erro ao excluir comissão:', error);
      }
    }
  };

  const toggleStatus = async (commission) => {
    try {
      const newStatus = commission.status === 'paid' ? 'pending' : 'paid';
      const response = await axios.put(`${API_BASE_URL}/commissions/${commission.id}`, {
        status: newStatus
      }, {
        withCredentials: true
      });
      
      if (response.status === 200) {
        fetchCommissions();
      }
    } catch (error) {
      console.error('Erro ao atualizar status:', error);
      alert('Erro ao atualizar status da comissão');
    }
  };

  // Função para gerar dados dos gráficos
  const generateChartsData = () => {
    // Dados por status
    const statusData = {};
    commissions.forEach(commission => {
      const status = commission.status || 'pending';
      statusData[status] = (statusData[status] || 0) + 1;
    });

    const statusChartData = Object.entries(statusData).map(([name, value]) => ({
      name: getStatusText(name),
      value
    }));

    // Dados por embaixadora (top 10)
    const ambassadorData = {};
    commissions.forEach(commission => {
      const ambassadorId = commission.ambassadorId || 'Não informado';
      if (!ambassadorData[ambassadorId]) {
        ambassadorData[ambassadorId] = { count: 0, total: 0 };
      }
      ambassadorData[ambassadorId].count++;
      ambassadorData[ambassadorId].total += commission.value || 0;
    });

    const ambassadorChartData = Object.entries(ambassadorData)
      .map(([ambassadorId, data]) => ({
        ambassador: ambassadorId,
        count: data.count,
        total: data.total
      }))
      .sort((a, b) => b.total - a.total)
      .slice(0, 10);

    // Dados mensais (últimos 6 meses)
    const monthlyData = {};
    const now = new Date();
    for (let i = 5; i >= 0; i--) {
      const date = new Date(now.getFullYear(), now.getMonth() - i, 1);
      const monthKey = date.toLocaleDateString('pt-BR', { month: 'short', year: 'numeric' });
      monthlyData[monthKey] = { count: 0, total: 0 };
    }

    commissions.forEach(commission => {
      if (commission.createdAt) {
        const date = new Date(commission.createdAt);
        const monthKey = date.toLocaleDateString('pt-BR', { month: 'short', year: 'numeric' });
        if (monthlyData.hasOwnProperty(monthKey)) {
          monthlyData[monthKey].count++;
          monthlyData[monthKey].total += commission.value || 0;
        }
      }
    });

    const monthlyChartData = Object.entries(monthlyData).map(([month, data]) => ({
      month,
      count: data.count,
      total: data.total
    }));

    // Distribuição de valores
    const valueRanges = {
      '0-100': 0,
      '101-500': 0,
      '501-1000': 0,
      '1001-2000': 0,
      '2000+': 0
    };

    commissions.forEach(commission => {
      const value = commission.value || 0;
      if (value <= 100) valueRanges['0-100']++;
      else if (value <= 500) valueRanges['101-500']++;
      else if (value <= 1000) valueRanges['501-1000']++;
      else if (value <= 2000) valueRanges['1001-2000']++;
      else valueRanges['2000+']++;
    });

    const valueRangeChartData = Object.entries(valueRanges).map(([range, count]) => ({
      range,
      count
    }));

    return {
      statusChartData,
      ambassadorChartData,
      monthlyChartData,
      valueRangeChartData
    };
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'paid':
        return 'bg-green-100 text-green-800';
      case 'pending':
        return 'bg-yellow-100 text-yellow-800';
      case 'cancelled':
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const getStatusText = (status) => {
    switch (status) {
      case 'paid':
        return 'Paga';
      case 'pending':
        return 'Pendente';
      case 'cancelled':
        return 'Cancelada';
      default:
        return status;
    }
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

  const totalCommissions = commissions.reduce((sum, comm) => sum + (comm.value || 0), 0);
  const paidCommissions = commissions
    .filter(comm => comm.status === 'paid' || comm.status === 'paga')
    .reduce((sum, comm) => sum + (comm.value || 0), 0);
  const pendingCommissions = commissions
    .filter(comm => comm.status === 'pending' || comm.status === 'pendente')
    .reduce((sum, comm) => sum + (comm.value || 0), 0);

  return (
    <div className="p-6">
      <div className="flex flex-col lg:flex-row lg:justify-between lg:items-center mb-6 space-y-4 lg:space-y-0">
        <h1 className="text-2xl lg:text-3xl font-bold text-gray-900">Comissões</h1>
        <div className="flex flex-col sm:flex-row space-y-2 sm:space-y-0 sm:space-x-3">
          <button
            onClick={() => setShowCharts(!showCharts)}
            className="bg-green-600 text-white px-3 py-2 rounded-lg flex items-center justify-center space-x-2 hover:bg-green-700 text-sm"
          >
            <BarChart3 className="h-4 w-4" />
            <span className="hidden sm:inline">{showCharts ? 'Ocultar Gráficos' : 'Mostrar Gráficos'}</span>
            <span className="sm:hidden">{showCharts ? 'Ocultar' : 'Gráficos'}</span>
          </button>
          {user.role === 'admin' && (
            <button
              onClick={() => setShowModal(true)}
              className="bg-blue-600 text-white px-3 py-2 rounded-lg flex items-center justify-center space-x-2 hover:bg-blue-700 text-sm"
            >
              <Plus className="h-4 w-4" />
              <span className="hidden sm:inline">Nova Comissão</span>
              <span className="sm:hidden">Nova</span>
            </button>
          )}
        </div>
      </div>

      {/* Cards de resumo */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
        <div className="bg-white p-6 rounded-lg shadow-md">
          <div className="flex items-center">
            <DollarSign className="h-8 w-8 text-blue-600" />
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Total Comissões</p>
              <p className="text-2xl font-bold text-gray-900">
                R$ {totalCommissions.toLocaleString('pt-BR', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
              </p>
            </div>
          </div>
        </div>

        <div className="bg-white p-6 rounded-lg shadow-md">
          <div className="flex items-center">
            <DollarSign className="h-8 w-8 text-green-600" />
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Pagas</p>
              <p className="text-2xl font-bold text-gray-900">
                R$ {paidCommissions.toLocaleString('pt-BR', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
              </p>
            </div>
          </div>
        </div>

        <div className="bg-white p-6 rounded-lg shadow-md">
          <div className="flex items-center">
            <DollarSign className="h-8 w-8 text-yellow-600" />
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Pendentes</p>
              <p className="text-2xl font-bold text-gray-900">
                R$ {pendingCommissions.toLocaleString('pt-BR', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Seção de Gráficos */}
      {showCharts && (
        <div className="mb-6">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Gráfico por Status */}
            <div className="bg-white p-6 rounded-lg shadow-md">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Comissões por Status</h3>
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

            {/* Gráfico por Embaixadora */}
            <div className="bg-white p-6 rounded-lg shadow-md">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Top Embaixadoras por Valor</h3>
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={generateChartsData().ambassadorChartData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="ambassador" angle={-45} textAnchor="end" height={100} />
                  <YAxis />
                  <Tooltip formatter={(value) => [`R$ ${value.toLocaleString('pt-BR', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`, 'Total']} />
                  <Bar dataKey="total" fill="#3B82F6" />
                </BarChart>
              </ResponsiveContainer>
            </div>

            {/* Gráfico Mensal */}
            <div className="bg-white p-6 rounded-lg shadow-md">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Comissões por Mês</h3>
              <ResponsiveContainer width="100%" height={300}>
                <LineChart data={generateChartsData().monthlyChartData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="month" />
                  <YAxis />
                  <Tooltip formatter={(value, name) => [
                    name === 'total' ? `R$ ${value.toLocaleString('pt-BR', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}` : value,
                    name === 'total' ? 'Valor Total' : 'Quantidade'
                  ]} />
                  <Line type="monotone" dataKey="count" stroke="#8B5CF6" name="count" />
                  <Line type="monotone" dataKey="total" stroke="#F59E0B" name="total" />
                </LineChart>
              </ResponsiveContainer>
            </div>

            {/* Distribuição de Valores */}
            <div className="bg-white p-6 rounded-lg shadow-md">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Distribuição por Faixa de Valor</h3>
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={generateChartsData().valueRangeChartData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="range" />
                  <YAxis />
                  <Tooltip />
                  <Bar dataKey="count" fill="#10B981" />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>
        </div>
      )}

      {/* Tabela para desktop */}
      <div className="hidden lg:block bg-white rounded-lg shadow-md overflow-hidden">
        <div className="overflow-x-auto scrollbar-thin scrollbar-thumb-gray-300 scrollbar-track-gray-100">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider min-w-[200px]">
                  Embaixadora
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider min-w-[200px]">
                  Indicação
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider min-w-[120px]">
                  Valor
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider min-w-[120px]">
                  Parcelas
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider min-w-[120px]">
                  Status
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider min-w-[150px]">
                  Data Criação
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider min-w-[150px]">
                  Última Atualização
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider min-w-[100px]">
                  Ações
                </th>


              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {commissions.map((commission) => {
                const indication = indications.find(ind => ind.id === commission.indicationId);
                const commissionInstallments = installments.filter(inst => inst.commission_id === commission.id);
                return (
                  <React.Fragment key={commission.id}>
                    <tr className="hover:bg-gray-50">
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                        {commission.ambassadorName || 'N/A'}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {indication ? indication.clientName : 'N/A'}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        R$ {commission.value ? commission.value.toLocaleString(
                          'pt-BR',
                          { minimumFractionDigits: 2, maximumFractionDigits: 2 }
                        ) : '0,00'}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {commissionInstallments.length > 0 ? (
                          <ul className="list-disc list-inside">
                            {commissionInstallments.map(inst => (
                              <li key={inst.id} className="text-xs">
                                Parcela {inst.parcel_number}: {inst.value.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })} ({inst.status})
                              </li>
                            ))}
                          </ul>
                        ) : 'N/A'}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${getStatusColor(commission.status)}`}>
                          {getStatusText(commission.status)}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {new Date(commission.created_at).toLocaleDateString('pt-BR')}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {new Date(commission.updated_at).toLocaleDateString('pt-BR')}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                        {user.role === 'admin' && (
                          <div className="flex items-center space-x-2">
                            <button
                              onClick={() => handleEdit(commission)}
                              className="text-indigo-600 hover:text-indigo-900"
                              title="Editar"
                            >
                              <Edit className="h-5 w-5" />
                            </button>
                            <button
                              onClick={() => handleDelete(commission.id)}
                              className="text-red-600 hover:text-red-900"
                              title="Excluir"
                            >
                              <Trash2 className="h-5 w-5" />
                            </button>
                            <button
                              onClick={() => toggleStatus(commission)}
                              className={`${commission.status === 'paid' ? 'text-yellow-600 hover:text-yellow-900' : 'text-green-600 hover:text-green-900'}`}
                              title={commission.status === 'paid' ? 'Marcar como Pendente' : 'Marcar como Paga'}
                            >
                              <DollarSign className="h-5 w-5" />
                            </button>
                          </div>
                        )}
                      </td>
                    </tr>
                  </React.Fragment>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>

      {/* Cards para mobile */}
      <div className="lg:hidden space-y-4">
        {commissions.map((commission) => {
          const indication = indications.find(ind => ind.id === commission.indicationId);

          return (
            <div key={commission.id} className="bg-white rounded-lg shadow-md p-3 card-hover border border-gray-100">
              <div className="flex justify-between items-start mb-3">
                <div className="flex-1 min-w-0">
                  <h3 className="text-base font-medium text-gray-900 truncate">
                    {commission.ambassadorName || 'Nome não disponível'}
                  </h3>
                  <p className="text-sm text-gray-600 truncate">
                    {commission.ambassadorEmail || 'Email não disponível'}
                  </p>
                  <p className="text-xs text-gray-500">
                    Cliente: {indication?.client_name || indication?.clientName || indication?.name || commission.clientName || 'Cliente não informado'}
                  </p>
                </div>
                {user.role === 'admin' && (
                  <div className="flex space-x-1 ml-2 flex-shrink-0">
                    <button
                      onClick={() => handleEdit(commission)}
                      className="text-blue-600 hover:text-blue-900 p-1 btn-hover-scale"
                    >
                      <Edit className="h-4 w-4" />
                    </button>
                    <button
                      onClick={() => handleDelete(commission.id)}
                      className="text-red-600 hover:text-red-900 p-1 btn-hover-scale"
                    >
                      <Trash2 className="h-4 w-4" />
                    </button>
                  </div>
                )}
              </div>
              
              <div className="grid grid-cols-1 gap-2 text-sm">
                <div className="flex justify-between items-start">
                  <span className="text-gray-500 text-xs">Valor:</span>
                  <span className="text-lg font-medium text-gray-900 ml-2">
                    R$ {(commission.value || 0).toLocaleString('pt-BR', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                  </span>
                </div>
                
                <div className="flex justify-between items-start">
                  <span className="text-gray-500 text-xs">Status:</span>
                  <div className="ml-2">
                    <button
                      onClick={() => user.role === 'admin' && toggleStatus(commission)}
                      className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${getStatusColor(commission.status)} ${
                        user.role === 'admin' ? 'cursor-pointer hover:opacity-80' : 'cursor-default'
                      }`}
                    >
                      {getStatusText(commission.status)}
                    </button>
                  </div>
                </div>
                
                {(indication?.status || commission.indicationStatus) && (
                  <div className="flex justify-between items-start">
                    <span className="text-gray-500 text-xs">Status Indicação:</span>
                    <span className="text-xs text-blue-600 ml-2 text-right break-words max-w-[60%]">
                      {indication?.status || commission.indicationStatus}
                    </span>
                  </div>
                )}
              </div>
            </div>
          );
        })}
      </div>

      {/* Modal */}
      {showModal && user.role === 'admin' && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4 animate-fadeIn">
          <div className="bg-white rounded-lg shadow-xl w-full max-w-md transform transition-all duration-300 animate-slideIn">
            {/* Header */}
            <div className="px-4 lg:px-6 py-3 lg:py-4 border-b border-gray-200 bg-gradient-to-r from-green-50 to-emerald-50">
              <h2 className="text-base lg:text-lg font-semibold text-gray-900">
                {editingCommission ? 'Editar Comissão' : 'Nova Comissão'}
              </h2>
            </div>

            {/* Form */}
            <form onSubmit={handleSubmit} className="px-4 lg:px-6 py-3 lg:py-4 space-y-3 lg:space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  ID da Embaixadora
                </label>
                <input
                  type="text"
                  required
                  value={formData.ambassadorId}
                  onChange={(e) => setFormData({...formData, ambassadorId: e.target.value})}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-sm"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Indicação
                </label>
                <select
                  required
                  value={formData.indicationId}
                  onChange={(e) => setFormData({...formData, indicationId: e.target.value})}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-sm"
                >
                  <option value="">Selecione uma indicação</option>
                  {indications.map((indication) => (
                    <option key={indication.id} value={indication.id}>
                      {indication.client_name || indication.clientName || indication.name || indication.email || indication.clientEmail || `Indicação ${indication.id}`}
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Valor
                </label>
                <input
                  type="number"
                  step="0.01"
                  required
                  value={formData.value}
                  onChange={(e) => setFormData({...formData, value: parseFloat(e.target.value)})}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-sm"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Status
                </label>
                <select
                  value={formData.status}
                  onChange={(e) => setFormData({...formData, status: e.target.value})}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-sm"
                >
                  <option value="pending">Pendente</option>
                  <option value="paid">Paga</option>
                  <option value="cancelled">Cancelada</option>
                </select>
              </div>
            </form>

            {/* Footer */}
            <div className="px-4 lg:px-6 py-3 lg:py-4 border-t border-gray-200 flex flex-col sm:flex-row sm:justify-end space-y-2 sm:space-y-0 sm:space-x-3">
              <button
                type="button"
                onClick={() => {
                  setShowModal(false);
                  setEditingCommission(null);
                  setFormData({
                    ambassadorId: '',
                    indicationId: '',
                    value: '',
                    status: 'pending'
                  });
                }}
                className="px-4 py-2 text-sm font-medium text-gray-700 bg-gray-100 border border-gray-300 rounded-md hover:bg-gray-200 focus:outline-none focus:ring-2 focus:ring-gray-500 w-full sm:w-auto"
              >
                Cancelar
              </button>
              <button
                type="submit"
                onClick={handleSubmit}
                className="px-4 py-2 text-sm font-medium text-white bg-blue-600 border border-transparent rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 w-full sm:w-auto"
              >
                {editingCommission ? 'Atualizar' : 'Criar'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Commissions;

