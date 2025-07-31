import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import axios from 'axios';
import { Plus, Edit, Trash2, DollarSign, BarChart3, Eye, ArrowRight, Calendar, Link, ToggleLeft, ToggleRight } from 'lucide-react';
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
  const [connectedMode, setConnectedMode] = useState(false);

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

  const fetchCommissions = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/commissions`, {
        withCredentials: true
      });
      setCommissions(response.data || []);
    } catch (error) {
      console.error('Erro ao buscar comissões:', error);
      setCommissions([]);
    }
  };

  const fetchIndications = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/indications`, {
        withCredentials: true
      });
      
      let indicationsData = [];
      if (Array.isArray(response.data)) {
        indicationsData = response.data;
      } else if (response.data && Array.isArray(response.data.indications)) {
        indicationsData = response.data.indications;
      } else if (response.data && response.data.data && Array.isArray(response.data.data)) {
        indicationsData = response.data.data;
      }
      
      setIndications(indicationsData);
    } catch (error) {
      console.error('Erro ao buscar indicações:', error);
      setIndications([]);
    }
  };

  const fetchInstallments = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/commission-installments`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });
      setInstallments(response.data.installments || []);
    } catch (error) {
      console.error('Erro ao buscar parcelas:', error);
      setInstallments([]);
    }
  };

  // Função para conectar dados quando em modo conectado
  const getConnectedData = () => {
    return commissions.map(commission => {
      const relatedIndication = indications.find(ind => ind.id === commission.indicationId);
      const relatedInstallments = installments.filter(inst => 
        inst.indication_id === commission.indicationId || inst.commission_id === commission.id
      );

      const installmentStats = {
        total: relatedInstallments.length,
        paid: relatedInstallments.filter(i => i.status === 'pago').length,
        pending: relatedInstallments.filter(i => i.status === 'pendente').length,
        overdue: relatedInstallments.filter(i => i.status === 'atrasado').length,
        totalValue: relatedInstallments.reduce((sum, i) => sum + (i.value || 0), 0),
        paidValue: relatedInstallments.filter(i => i.status === 'pago').reduce((sum, i) => sum + (i.value || 0), 0)
      };

      return {
        ...commission,
        indication: relatedIndication,
        installments: relatedInstallments,
        installmentStats,
        clientName: relatedIndication?.clientName || relatedIndication?.name || 'Cliente não informado',
        indicationStatus: relatedIndication?.status || 'Não informado',
        indicationDate: relatedIndication?.createdAt || relatedIndication?.date,
        completionRate: installmentStats.total > 0 ? 
                       (installmentStats.paid / installmentStats.total * 100).toFixed(1) : 0
      };
    });
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

      fetchAllData();
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
        fetchAllData();
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
        fetchAllData();
      }
    } catch (error) {
      console.error('Erro ao atualizar status:', error);
      alert('Erro ao atualizar status da comissão');
    }
  };



  // Função para gerar dados dos gráficos
  const generateChartsData = () => {
    const data = getConnectedData();

    // Dados por status
    const statusData = {};
    data.forEach(commission => {
      const status = commission.status || 'pending';
      statusData[status] = (statusData[status] || 0) + 1;
    });

    const statusChartData = Object.entries(statusData).map(([name, value]) => ({
      name: getStatusText(name),
      value
    }));

    // Dados por embaixadora
    const ambassadorData = {};
    data.forEach(commission => {
      const ambassadorId = commission.ambassadorId || 'Não informado';
      const ambassadorName = commission.ambassadorName || `Embaixadora ${ambassadorId}`;
      
      if (!ambassadorData[ambassadorName]) {
        ambassadorData[ambassadorName] = { 
          count: 0, 
          total: 0,
          installments: 0,
          paidInstallments: 0
        };
      }
      ambassadorData[ambassadorName].count++;
      ambassadorData[ambassadorName].total += commission.value || 0;
      
      if (commission.installmentStats) {
        ambassadorData[ambassadorName].installments += commission.installmentStats.total;
        ambassadorData[ambassadorName].paidInstallments += commission.installmentStats.paid;
      }
    });

    const ambassadorChartData = Object.entries(ambassadorData)
      .map(([ambassador, data]) => ({
        ambassador,
        count: data.count,
        total: data.total,
        installments: data.installments,
        paidInstallments: data.paidInstallments,
        completionRate: data.installments > 0 ? (data.paidInstallments / data.installments * 100).toFixed(1) : 0
      }))
      .sort((a, b) => b.total - a.total)
      .slice(0, 10);

    return {
      statusChartData,
      ambassadorChartData
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

  const formatCurrency = (value) => {
    return new Intl.NumberFormat('pt-BR', {
      style: 'currency',
      currency: 'BRL'
    }).format(value || 0);
  };

  const formatDate = (dateString) => {
    if (!dateString) return 'Data não informada';
    const date = new Date(dateString);
    return date.toLocaleDateString('pt-BR');
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

  const displayData = getConnectedData();
  const chartsData = generateChartsData();

  const totalCommissions = displayData.reduce((sum, comm) => sum + (comm.value || 0), 0);
  const paidCommissions = displayData
    .filter(comm => comm.status === 'paid' || comm.status === 'paga')
    .reduce((sum, comm) => sum + (comm.value || 0), 0);
  const pendingCommissions = displayData
    .filter(comm => comm.status === 'pending' || comm.status === 'pendente')
    .reduce((sum, comm) => sum + (comm.value || 0), 0);

  // Métricas conectadas
  const totalInstallments = displayData.reduce((sum, comm) => sum + (comm.installmentStats?.total || 0), 0);
  const paidInstallments = displayData.reduce((sum, comm) => sum + (comm.installmentStats?.paid || 0), 0);

  return (
    <div className="p-6">
      <div className="flex flex-col lg:flex-row lg:justify-between lg:items-center mb-6 space-y-4 lg:space-y-0">
        <div>
          <h1 className="text-2xl lg:text-3xl font-bold text-gray-900">            Comissões</h1>

        </div>
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
      <div className={`grid grid-cols-1 md:grid-cols-3 gap-6 mb-6 justify-items-center`}>
        <div className="bg-white p-6 rounded-lg shadow-md">
          <div className="flex items-center">
            <DollarSign className="h-8 w-8 text-blue-600" />
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Total Comissões</p>
              <p className="text-2xl font-bold text-gray-900">
                {formatCurrency(totalCommissions)}
              </p>
              <p className="text-sm text-gray-500">{displayData.length} comissões</p>
            </div>
          </div>
        </div>

        <div className="bg-white p-6 rounded-lg shadow-md">
          <div className="flex items-center">
            <DollarSign className="h-8 w-8 text-green-600" />
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Pagas</p>
              <p className="text-2xl font-bold text-gray-900">
                {formatCurrency(paidCommissions)}
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
                {formatCurrency(pendingCommissions)}
              </p>

            </div>
          </div>
        </div>



      {/* Fluxo de conversão (apenas no modo conectado) */}


      {/* Seção de Gráficos */}
      {showCharts && (
        <div className="mb-6">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Gráfico por Status */}
            <div className="bg-white p-6 rounded-lg shadow-md">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">
                Comissões por Status
              </h3>
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

            {/* Gráfico por Embaixadora */}
            <div className="bg-white p-6 rounded-lg shadow-md">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">
                Top Embaixadoras por Valor
              </h3>
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={chartsData.ambassadorChartData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="ambassador" angle={-45} textAnchor="end" height={100} />
                  <YAxis />
                  <Tooltip formatter={(value, name) => [
                    name === 'total' ? formatCurrency(value) : 
                    name === 'completionRate' ? `${value}%` : value,
                    name === 'total' ? 'Valor Total' : 
                    name === 'count' ? 'Comissões' :
                    name === 'installments' ? 'Parcelas' :
                    name === 'paidInstallments' ? 'Parcelas Pagas' : 'Taxa de Conclusão'
                  ]} />
                  <Bar dataKey="total" fill="#3B82F6" />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>
        </div>
      )}

      {/* Tabela de comissões */}
      <div className="bg-white rounded-lg shadow-md overflow-hidden">
        <div className="px-6 py-4 border-b border-gray-200">
          <h3 className="text-lg font-semibold text-gray-900">
            Lista de Comissões
          </h3>

        </div>
        
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Embaixadora
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Indicação
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Valor
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Status
                </th>

              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {displayData.map((commission) => {
                const indication = indications.find(ind => ind.id === commission.indicationId);

                return (
                  <tr key={commission.id} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm font-medium text-gray-900">
                        {connectedMode ? commission.clientName : (commission.ambassadorName || 'Nome não disponível')}
                      </div>
                      {connectedMode && commission.indicationDate && (
                        <div className="text-sm text-gray-500">
                          {formatDate(commission.indicationDate)}
                        </div>
                      )}
                    </td>
                    {connectedMode && (
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm text-gray-900">
                          {commission.ambassadorName || 'Nome não disponível'}
                        </div>
                      </td>
                    )}
                    {!connectedMode && (
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm text-gray-900">
                          {indication?.clientName || indication?.name || 'Indicação não encontrada'}
                        </div>
                      </td>
                    )}
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm font-medium text-gray-900">
                        {formatCurrency(commission.value)}
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${getStatusColor(commission.status)}`}>
                        {getStatusText(commission.status)}
                      </span>
                    </td>
                    {connectedMode && (
                      <>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div className="text-sm text-gray-900">
                            {commission.installmentStats.paid}/{commission.installmentStats.total}
                          </div>
                          <div className="text-sm text-gray-500">
                            {formatCurrency(commission.installmentStats.paidValue)} de {formatCurrency(commission.installmentStats.totalValue)}
                          </div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div className="flex items-center">
                            <div className="w-16 bg-gray-200 rounded-full h-2 mr-2">
                              <div 
                                className="bg-green-600 h-2 rounded-full" 
                                style={{ width: `${commission.completionRate}%` }}
                              ></div>
                            </div>
                            <span className="text-sm text-gray-900">{commission.completionRate}%</span>
                          </div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div className="text-sm text-gray-900">
                            {commission.indicationStatus}
                          </div>
                        </td>
                      </>
                    )}
                    {user.role === 'admin' && (
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                        <div className="flex space-x-2">
                          {connectedMode && (
                            <button
                              onClick={() => setSelectedCommission(commission)}
                              className="text-blue-600 hover:text-blue-900"
                              title="Ver detalhes"
                            >
                              <Eye className="h-4 w-4" />
                            </button>
                        </div>
                      </td>
                    )}
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>

        {displayData.length === 0 && (
          <div className="text-center py-12">
            <DollarSign className="mx-auto h-12 w-12 text-gray-400" />
            <h3 className="mt-2 text-sm font-medium text-gray-900">Nenhuma comissão encontrada</h3>
            <p className="mt-1 text-sm text-gray-500">
              As comissões aparecerão aqui quando forem criadas.
            </p>
          </div>
        )}
      </div>

      {/* Modal de detalhes (apenas no modo conectado) */}
      {connectedMode && selectedCommission && (
        <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
          <div className="relative top-20 mx-auto p-5 border w-96 shadow-lg rounded-md bg-white">
            <div className="mt-3">
              <h3 className="text-lg font-medium text-gray-900 mb-4">Detalhes da Comissão Conectada</h3>
              <div className="space-y-3">
                <div>
                  <span className="font-medium">Cliente:</span> {selectedCommission.clientName}
                </div>
                <div>
                  <span className="font-medium">Embaixadora:</span> {selectedCommission.ambassadorName}
                </div>
                <div>
                  <span className="font-medium">Valor da Comissão:</span> {formatCurrency(selectedCommission.value)}
                </div>
                <div>
                  <span className="font-medium">Status da Indicação:</span> {selectedCommission.indicationStatus}
                </div>
                <div>
                  <span className="font-medium">Parcelas:</span> {selectedCommission.installmentStats.paid}/{selectedCommission.installmentStats.total}
                </div>
                <div>
                  <span className="font-medium">Valor Pago:</span> {formatCurrency(selectedCommission.installmentStats.paidValue)}
                </div>
                <div>
                  <span className="font-medium">Taxa de Conclusão:</span> {selectedCommission.completionRate}%
                </div>
                {selectedCommission.indication && (
                  <div>
                    <span className="font-medium">ID da Indicação:</span> {selectedCommission.indication.id}
                  </div>
                )}
                <div>
                  <span className="font-medium">Parcelas Detalhadas:</span>
                  <div className="mt-2 space-y-1">
                    {selectedCommission.installments.map((inst, index) => (
                      <div key={index} className="text-sm text-gray-600">
                        {inst.installment_number || inst.installmentNumber}ª parcela: {formatCurrency(inst.value)} - {inst.status}
                      </div>
                    ))}
                  </div>
                </div>
              </div>
              <div className="flex justify-end mt-6">
                <button
                  onClick={() => setSelectedCommission(null)}
                  className="px-4 py-2 bg-gray-300 text-gray-700 rounded-md hover:bg-gray-400"
                >
                  Fechar
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Modal de formulário */}
      {showModal && (
        <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
          <div className="relative top-20 mx-auto p-5 border w-96 shadow-lg rounded-md bg-white">
            <div className="mt-3">
              <h3 className="text-lg font-medium text-gray-900 mb-4">
                {editingCommission ? 'Editar Comissão' : 'Nova Comissão'}
              </h3>
              <form onSubmit={handleSubmit} className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    ID da Embaixadora
                  </label>
                  <input
                    type="text"
                    value={formData.ambassadorId}
                    onChange={(e) => setFormData({ ...formData, ambassadorId: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    required
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    ID da Indicação
                  </label>
                  <input
                    type="text"
                    value={formData.indicationId}
                    onChange={(e) => setFormData({ ...formData, indicationId: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    required
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Valor
                  </label>
                  <input
                    type="number"
                    step="0.01"
                    value={formData.value}
                    onChange={(e) => setFormData({ ...formData, value: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    required
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Status
                  </label>
                  <select
                    value={formData.status}
                    onChange={(e) => setFormData({ ...formData, status: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="pending">Pendente</option>
                    <option value="paid">Paga</option>
                    <option value="cancelled">Cancelada</option>
                  </select>
                </div>
                <div className="flex justify-end space-x-3 mt-6">
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
                    className="px-4 py-2 bg-gray-300 text-gray-700 rounded-md hover:bg-gray-400"
                  >
                    Cancelar
                  </button>
                  <button
                    type="submit"
                    className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
                  >
                    {editingCommission ? 'Atualizar' : 'Criar'}
                  </button>
                </div>
              </form>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Commissions;

