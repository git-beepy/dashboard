import React, { useState, useEffect } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import { getOriginOptions } from '../../constants/origins';
import { getSegmentOptions } from '../../constants/segments';
import axios from 'axios';
import { Plus, Edit, Trash2, Check, X, BarChart3, PieChart } from 'lucide-react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart as RechartsPieChart, Pie, Cell } from 'recharts';

const Indications = () => {
  const { user, API_BASE_URL } = useAuth();
  const [indications, setIndications] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [editingIndication, setEditingIndication] = useState(null);
  const [showCharts, setShowCharts] = useState(false);
  const [formData, setFormData] = useState({
    client_name: '',
    email: '',
    phone: '',
    origin: 'website',
    segment: 'saude',
    customSegment: ''
  });

  useEffect(() => {
    fetchIndications();
  }, []);

  const fetchIndications = async () => {
    try {
      console.log('Buscando indicações...');
      const response = await axios.get(`${API_BASE_URL}/indications`);
      console.log('Indicações recebidas:', response.data);
      setIndications(response.data);
    } catch (error) {
      console.error('Erro ao buscar indicações:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    console.log('handleSubmit chamado');
    console.log('editingIndication:', editingIndication);
    console.log('formData:', formData);

    try {
      const submitData = { ...formData };

      // Se o segmento for "outro" e há um segmento customizado, usar o customizado
      if (formData.segment === 'outro' && formData.customSegment.trim()) {
        submitData.segment = formData.customSegment.trim();
      }

      // Remover o campo customSegment antes de enviar
      delete submitData.customSegment;

      console.log('submitData:', submitData);

      if (editingIndication) {
        console.log('Editando indicação:', editingIndication.id);
        console.log('URL da requisição:', `${API_BASE_URL}/indications/${editingIndication.id}`);
        console.log('Dados sendo enviados:', submitData);

        const response = await axios.put(`${API_BASE_URL}/indications/${editingIndication.id}`, submitData);
        console.log('Resposta da API:', response.status, response.data);
      } else {
        console.log('Criando nova indicação');
        await axios.post(`${API_BASE_URL}/indications`, submitData);
      }

      console.log('Chamando fetchIndications após salvar...');
      fetchIndications();
      setShowModal(false);
      setEditingIndication(null);
      setFormData({
        client_name: '',
        email: '',
        phone: '',
        origin: 'website',
        segment: 'saude',
        customSegment: ''
      });
    } catch (error) {
      console.error("Erro ao salvar indicação:", error);
      alert("Erro ao salvar indicação. Verifique o console para mais detalhes.");
    }
  };

  const handleEdit = (indication) => {
    setEditingIndication(indication);

    // Verificar se o segmento é um dos padrões ou customizado
    const standardSegments = [
      'saude', 'educacao_pesquisa', 'juridico', 'administracao_negocios', 'engenharias',
      'tecnologia_informacao', 'financeiro_bancario', 'marketing_vendas_comunicacao',
      'industria_producao', 'construcao_civil', 'transportes_logistica', 'comercio_varejo',
      'turismo_hotelaria_eventos', 'gastronomia_alimentacao', 'agronegocio_meio_ambiente',
      'artes_cultura_design', 'midias_digitais_criativas', 'seguranca_defesa', 'servicos_gerais'
    ];
    const isStandardSegment = standardSegments.includes(indication.segment);

    setFormData({
      client_name: indication.client_name,
      email: indication.email,
      phone: indication.phone,
      origin: indication.origin,
      segment: isStandardSegment ? indication.segment : 'outro',
      customSegment: isStandardSegment ? '' : indication.segment
    });
    setShowModal(true);
  };

  const handleDelete = async (id) => {
    if (window.confirm('Tem certeza que deseja excluir esta indicação?')) {
      try {
        await axios.delete(`${API_BASE_URL}/indications/${id}`);
        fetchIndications();
      } catch (error) {
        console.error("Erro ao excluir indicação:", error);
      alert("Erro ao excluir indicação. Verifique o console para mais detalhes.");
      }
    }
  };

  const toggleConversion = async (indication) => {
    try {
      await axios.put(`${API_BASE_URL}/indications/${indication.id}`, {
        converted: !indication.converted
      });
      fetchIndications();
    } catch (error) {
      console.error("Erro ao atualizar conversão:", error);
      alert("Erro ao atualizar conversão. Verifique o console para mais detalhes.");
    }
  };

  const updateIndicationStatus = async (indicationId, newStatus) => {
    try {
      await axios.put(`${API_BASE_URL}/indications/${indicationId}/status`, {
        status: newStatus
      });
      fetchIndications();
    } catch (error) {
      console.error("Erro ao atualizar status da indicação:", error);
      alert("Erro ao atualizar status da indicação. Verifique o console para mais detalhes.");
    }
  };

  // Função para gerar dados dos gráficos
  const generateChartsData = () => {
    // Dados por origem
    const originData = {};
    indications.forEach(indication => {
      const originKey = indication.origin || 'Não informado';
      const originDisplayName = getOriginDisplayName(originKey);
      originData[originDisplayName] = (originData[originDisplayName] || 0) + 1;
    });

    const originChartData = Object.entries(originData).map(([name, value]) => ({
      name,
      value
    }));

    // Dados por segmento
    const segmentData = {};
    indications.forEach(indication => {
      const segmentKey = indication.segment || "Não informado";
      const segmentDisplayName = getSegmentDisplayName(segmentKey);
      segmentData[segmentDisplayName] = (segmentData[segmentDisplayName] || 0) + 1;
    });

    const segmentChartData = Object.entries(segmentData).map(([name, value]) => ({
      name,
      value
    }));

    // Dados por mês (últimos 6 meses)
    const monthlyData = {};
    const now = new Date();
    for (let i = 5; i >= 0; i--) {
      const date = new Date(now.getFullYear(), now.getMonth() - i, 1);
      const monthKey = date.toLocaleDateString('pt-BR', { month: 'short', year: 'numeric' });
      monthlyData[monthKey] = 0;
    }

    indications.forEach(indication => {
      if (indication.createdAt) {
        const date = new Date(indication.createdAt);
        const monthKey = date.toLocaleDateString('pt-BR', { month: 'short', year: 'numeric' });
        if (monthlyData.hasOwnProperty(monthKey)) {
          monthlyData[monthKey]++;
        }
      }
    });

    const monthlyChartData = Object.entries(monthlyData).map(([month, count]) => ({
      month,
      count
    }));

    // Dados por Status
    const statusData = {};
    indications.forEach(indication => {
      const statusKey = indication.status || 'Pendente';
      statusData[statusKey] = (statusData[statusKey] || 0) + 1;
    });

    const statusChartData = Object.entries(statusData).map(([name, value]) => ({
      name,
      value
    }));

    return {
      originChartData,
      segmentChartData,
      statusChartData,
      monthlyChartData
    };
  };

  // Função auxiliar para obter nome de exibição da origem
  const getOriginDisplayName = (originKey) => {
    const originOptions = getOriginOptions();
    const option = originOptions.find(opt => opt.value === originKey);
    return option ? option.label : originKey;
  };

  // Função auxiliar para obter nome de exibição do segmento
  const getSegmentDisplayName = (segmentKey) => {
    const segmentOptions = getSegmentOptions();
    const option = segmentOptions.find(opt => opt.value === segmentKey);
    return option ? option.label : segmentKey;
  };

  const closeModal = () => {
    setShowModal(false);
    setEditingIndication(null);
    setFormData({
      client_name: '',
      email: '',
      phone: '',
      origin: 'website',
      segment: 'saude',
      customSegment: ''
    });
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
        <h1 className="text-2xl lg:text-3xl font-bold text-gray-900">Indicações</h1>
        <div className="flex flex-col sm:flex-row space-y-2 sm:space-y-0 sm:space-x-3">
          <button
            onClick={() => setShowCharts(!showCharts)}
            className="bg-green-600 text-white px-3 py-2 rounded-lg flex items-center justify-center space-x-2 hover:bg-green-700 text-sm"
          >
            <BarChart3 className="h-4 w-4" />
            <span className="hidden sm:inline">{showCharts ? 'Ocultar Gráficos' : 'Mostrar Gráficos'}</span>
            <span className="sm:hidden">{showCharts ? 'Ocultar' : 'Gráficos'}</span>
          </button>
          <button
            onClick={() => setShowModal(true)}
            className="bg-blue-600 text-white px-3 py-2 rounded-lg flex items-center justify-center space-x-2 hover:bg-blue-700 text-sm"
          >
            <Plus className="h-4 w-4" />
            <span className="hidden sm:inline">Nova Indicação</span>
            <span className="sm:hidden">Nova</span>
          </button>
        </div>
      </div>

      {/* Seção de Gráficos */}
      {showCharts && (
        <div className="mb-6">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Gráfico por Origem */}
            <div className="bg-white p-6 rounded-lg shadow-md">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Indicações por Origem</h3>
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={generateChartsData().originChartData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="name" />
                  <YAxis />
                  <Tooltip />
                  <Bar dataKey="value" fill="#3B82F6" />
                </BarChart>
              </ResponsiveContainer>
            </div>

            {/* Gráfico por Status */}
            <div className="bg-white p-6 rounded-lg shadow-md">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Indicações por Status</h3>
              <ResponsiveContainer width="100%" height={300}>
                <RechartsPieChart>
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
                      <Cell key={`cell-${index}`} fill={['#10B981', '#F59E0B', '#EF4444', '#8B5CF6'][index % 4]} />
                    ))}
                  </Pie>
                  <Tooltip />
                </RechartsPieChart>
              </ResponsiveContainer>
            </div>

            {/* Gráfico por Segmento */}
            <div className="bg-white p-6 rounded-lg shadow-md">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Indicações por Segmento</h3>
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={generateChartsData().segmentChartData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="name" angle={-45} textAnchor="end" height={100} />
                  <YAxis />
                  <Tooltip />
                  <Bar dataKey="value" fill="#8B5CF6" />
                </BarChart>
              </ResponsiveContainer>
            </div>

            {/* Gráfico Mensal */}
            <div className="bg-white p-6 rounded-lg shadow-md">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Indicações por Mês</h3>
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={generateChartsData().monthlyChartData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="month" />
                  <YAxis />
                  <Tooltip />
                  <Bar dataKey="count" fill="#F59E0B" />
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
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider min-w-[150px]">
                  Cliente
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider min-w-[200px]">
                  Contato
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider min-w-[120px]">
                  Origem
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider min-w-[150px]">
                  Segmento
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider min-w-[120px]">
                  Status
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider min-w-[100px]">
                  Ações
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {indications.map((indication) => (
                <tr key={indication.id}>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div>
                      <div className="text-sm font-medium text-gray-900">
                        {indication.client_name}
                      </div>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm text-gray-900">{indication.email}</div>
                    <div className="text-sm text-gray-500">{indication.phone}</div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-blue-100 text-blue-800">
                      {indication.origin}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {indication.segment}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    {user.role === 'admin' ? (
                      <select
                        value={indication.status || 'pendente'}
                        onChange={(e) => updateIndicationStatus(indication.id, e.target.value)}
                        className="px-2 py-1 text-xs font-semibold rounded-full border-0 bg-gray-100 focus:ring-2 focus:ring-blue-500"
                      >
                        <option value="agendado">Agendado</option>
                        <option value="aprovado">Aprovado</option>
                        <option value="não aprovado">Não Aprovado</option>
                      </select>
                    ) : (
                      <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${
                        indication.status === 'aprovado' ? 'bg-green-100 text-green-800' :
                        indication.status === 'não aprovado' ? 'bg-red-100 text-red-800' :
                        indication.status === 'agendado' ? 'bg-yellow-100 text-yellow-800' :
                        'bg-gray-100 text-gray-800'
                      }`}>
                        {indication.status || 'Pendente'}
                      </span>
                    )}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                    <div className="flex space-x-2">
                      <button
                        onClick={() => handleEdit(indication)}
                        className="text-blue-600 hover:text-blue-900"
                      >
                        <Edit className="h-4 w-4" />
                      </button>
                      {user.role === 'admin' && (
                        <button
                          onClick={() => handleDelete(indication.id)}
                          className="text-red-600 hover:text-red-900"
                        >
                          <Trash2 className="h-4 w-4" />
                        </button>
                      )}
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Cards para mobile */}
      <div className="lg:hidden space-y-4">
        {indications.map((indication) => (
          <div key={indication.id} className="bg-white rounded-lg shadow-md p-3 card-hover border border-gray-100">
            <div className="flex justify-between items-start mb-3">
              <div className="flex-1 min-w-0">
                <h3 className="text-base font-medium text-gray-900 truncate">
                  {indication.client_name}
                </h3>
                <p className="text-sm text-gray-600 truncate">{indication.email}</p>
                <p className="text-xs text-gray-500">{indication.phone}</p>
              </div>
              <div className="flex space-x-1 ml-2 flex-shrink-0">
                <button
                  onClick={() => handleEdit(indication)}
                  className="text-blue-600 hover:text-blue-900 p-1 btn-hover-scale"
                >
                  <Edit className="h-4 w-4" />
                </button>
                {user.role === 'admin' && (
                  <button
                    onClick={() => handleDelete(indication.id)}
                    className="text-red-600 hover:text-red-900 p-1 btn-hover-scale"
                  >
                    <Trash2 className="h-4 w-4" />
                  </button>
                )}
              </div>
            </div>

            <div className="grid grid-cols-1 gap-2 text-sm">
              <div className="flex justify-between items-start">
                <span className="text-gray-500 text-xs">Origem:</span>
                <span className="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-blue-100 text-blue-800 ml-2">
                  {indication.origin}
                </span>
              </div>

              <div className="flex justify-between items-start">
                <span className="text-gray-500 text-xs">Segmento:</span>
                <span className="text-gray-900 text-xs text-right ml-2 break-words max-w-[60%]">{indication.segment}</span>
              </div>

              <div className="flex justify-between items-start">
                <span className="text-gray-500 text-xs">Status:</span>
                <div className="ml-2">
                  {user.role === 'admin' ? (
                    <select
                      value={indication.status || 'pendente'}
                      onChange={(e) => updateIndicationStatus(indication.id, e.target.value)}
                      className="px-2 py-1 text-xs font-semibold rounded-full border-0 bg-gray-100 focus:ring-2 focus:ring-blue-500 max-w-[120px]"
                    >
                      <option value="agendado">Agendado</option>
                      <option value="aprovado">Aprovado</option>
                      <option value="não aprovado">Não Aprovado</option>
                    </select>
                  ) : (
                    <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${
                      indication.status === 'aprovado' ? 'bg-green-100 text-green-800' :
                      indication.status === 'não aprovado' ? 'bg-red-100 text-red-800' :
                      indication.status === 'agendado' ? 'bg-yellow-100 text-yellow-800' :
                      'bg-gray-100 text-gray-800'
                    }`}>
                      {indication.status || 'Pendente'}
                    </span>
                  )}
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Modal */}
      {showModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4 animate-fadeIn">
          <div className="bg-white rounded-lg shadow-xl w-full max-w-md transform transition-all duration-300 animate-slideIn">
            {/* Header */}
            <div className="px-4 lg:px-6 py-3 lg:py-4 border-b border-gray-200 bg-gradient-to-r from-blue-50 to-indigo-50">
              <h2 className="text-base lg:text-lg font-semibold text-gray-900">
                {editingIndication ? 'Editar Indicação' : 'Nova Indicação'}
              </h2>
            </div>

            {/* Form */}
            <form onSubmit={handleSubmit} className="px-4 lg:px-6 py-3 lg:py-4 space-y-3 lg:space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Nome do Cliente
                </label>
                <input
                  type="text"
                  required
                  value={formData.client_name}
                  onChange={(e) => setFormData({...formData, client_name: e.target.value})}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-sm"
                  placeholder=""
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Email
                </label>
                <input
                  type="email"
                  required
                  value={formData.email}
                  onChange={(e) => setFormData({...formData, email: e.target.value})}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-sm"
                  placeholder=""
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Telefone
                </label>
                <input
                  type="tel"
                  required
                  value={formData.phone}
                  onChange={(e) => setFormData({...formData, phone: e.target.value})}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-sm"
                  placeholder=""
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Origem
                </label>
                <select
                  value={formData.origin}
                  onChange={(e) => setFormData({...formData, origin: e.target.value})}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-sm"
                >
                  {getOriginOptions().map((option) => (
                    <option key={option.value} value={option.value}>
                      {option.label}
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Segmento
                </label>
                <select
                  value={formData.segment}
                  onChange={(e) => setFormData({...formData, segment: e.target.value, customSegment: ''})}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-sm"
                >
                  {getSegmentOptions().map((option) => (
                    <option key={option.value} value={option.value}>
                      {option.label}
                    </option>
                  ))}
                </select>
              </div>

              {formData.segment === 'outro' && (
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Especificar Segmento
                  </label>
                  <input
                    type="text"
                    required
                    value={formData.customSegment}
                    onChange={(e) => setFormData({...formData, customSegment: e.target.value})}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-sm"
                    placeholder="Digite o segmento específico"
                  />
                </div>
              )}
            </form>

            {/* Footer */}
            <div className="px-4 lg:px-6 py-3 lg:py-4 border-t border-gray-200 flex flex-col sm:flex-row sm:justify-end space-y-2 sm:space-y-0 sm:space-x-3">
              <button
                type="button"
                onClick={closeModal}
                className="px-4 py-2 text-sm font-medium text-gray-700 bg-gray-100 border border-gray-300 rounded-md hover:bg-gray-200 focus:outline-none focus:ring-2 focus:ring-gray-500 w-full sm:w-auto"
              >
                Cancelar
              </button>
              <button
                type="submit"
                onClick={handleSubmit}
                className="px-4 py-2 text-sm font-medium text-white bg-blue-600 border border-transparent rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 w-full sm:w-auto"
              >
                {editingIndication ? 'Salvar' : 'Criar'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Indications;

