import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { TrendingUp, Users, DollarSign, Target, CheckCircle, Plus } from 'lucide-react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, LineChart, Line, PieChart, Pie, Cell } from 'recharts';
import axios from 'axios';
import { useAuth } from './contexts/AuthContext';

const AdminDashboard = () => {
  const { user, API_BASE_URL } = useAuth();
  const [dashboardData, setDashboardData] = useState(null);
  const [indications, setIndications] = useState([]);
  const [commissions, setCommissions] = useState([]);
  const [loading, setLoading] = useState(true);

  // Modal state and form data for new indication
  const [showModal, setShowModal] = useState(false);
  const [formData, setFormData] = useState({
    clientName: '',
    companyName: '',
    clientEmail: '',
    clientPhone: '',
    origin: 'website',
    segment: '',
    customSegment: ''
  });

  useEffect(() => {
    fetchDashboardData();
    fetchIndications();
    fetchCommissions();
  }, []);

  const fetchDashboardData = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/dashboard/admin`, {
        credentials: 'include'
      });
      if (response.ok) {
        const data = await response.json();
        setDashboardData(data);
      }
    } catch (error) {
      console.error('Erro ao buscar dados do dashboard:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchIndications = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/indications`);
      setIndications(response.data);
    } catch (error) {
      console.error('Erro ao buscar indicações:', error);
    }
  };

  const fetchCommissions = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/commissions`, {
        credentials: 'include'
      });
      if (response.ok) {
        const data = await response.json();
        setCommissions(data.commissions);
      }
    } catch (error) {
      console.error('Erro ao buscar comissões:', error);
    }
  };

  const updateIndicationStatus = async (indicationId, newStatus) => {
    try {
      const response = await fetch(`${API_BASE_URL}/indications/${indicationId}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include',
        body: JSON.stringify({ status: newStatus }),
      });

      if (response.ok) {
        fetchIndications();
        fetchDashboardData();
        fetchCommissions();
      }
    } catch (error) {
      console.error('Erro ao atualizar status:', error);
    }
  };

  const markCommissionAsPaid = async (commissionId) => {
    try {
      const response = await fetch(`${API_BASE_URL}/commissions/${commissionId}/pay`, {
        method: 'PUT',
        credentials: 'include',
      });

      if (response.ok) {
        fetchCommissions();
        fetchDashboardData();
      }
    } catch (error) {
      console.error('Erro ao marcar comissão como paga:', error);
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'aprovado':
        return 'bg-green-100 text-green-800';
      case 'não aprovado':
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-yellow-100 text-yellow-800';
    }
  };

  const getPaymentStatusColor = (status) => {
    return status === 'pago' ? 'bg-green-100 text-green-800' : 'bg-yellow-100 text-yellow-800';
  };

  const COLORS = ['#f59e0b', '#10b981', '#3b82f6', '#ef4444'];

  // Modal functions
  const handleModalSubmit = async (e) => {
    e.preventDefault();
    try {
      await axios.post(`${API_BASE_URL}/indications`, formData);
      fetchIndications(); // Refresh indications list
      setShowModal(false);
      setFormData({
        clientName: '',
        clientEmail: '',
        clientPhone: '',
        origin: 'website',
        segment: 'geral'
      });
    } catch (error) {
      console.error('Erro ao salvar nova indicação:', error);
    }
  };

  const closeModal = () => {
    setShowModal(false);
    setFormData({
      clientName: '',
      companyName: '',
      clientEmail: '',
      clientPhone: '',
      origin: 'website',
      segment: '',
      customSegment: ''
    });
  };

  if (loading) {
    return <div className="flex justify-center items-center h-64">Carregando...</div>;
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold text-gray-900">Dashboard - Visão da Agência</h1>
        <button
          onClick={() => setShowModal(true)}
          className="bg-orange-500 text-white px-4 py-2 rounded-lg flex items-center space-x-2 hover:bg-orange-600"
        >
          <Plus className="h-4 w-4" />
          <span>Nova Indicação</span>
        </button>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <Card className="bg-green-400">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-gray-900">Comissões a Pagar no Mês</CardTitle>
            <DollarSign className="h-4 w-4 text-gray-900" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-gray-900">
              R$ {dashboardData?.stats?.commissions_to_pay?.toFixed(2) || '0,00'}
            </div>
          </CardContent>
        </Card>

        <Card className="bg-yellow-400">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-gray-900">Taxa de Conversão das Indicações</CardTitle>
            <Target className="h-4 w-4 text-gray-900" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-gray-900">
              {dashboardData?.stats?.conversion_rate?.toFixed(1) || 0}%
            </div>
          </CardContent>
        </Card>

        <Card className="bg-red-400">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-white">Total de Indicações</CardTitle>
            <TrendingUp className="h-4 w-4 text-white" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-white">{dashboardData?.stats?.total_indications || 0}</div>
          </CardContent>
        </Card>

        <Card className="bg-purple-400">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-white">Embaixadoras Ativas</CardTitle>
            <Users className="h-4 w-4 text-white" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-white">{dashboardData?.stats?.total_ambassadors || 0}</div>
          </CardContent>
        </Card>
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Indicações mês a mês */}
        <Card>
          <CardHeader>
            <CardTitle>Indicações mês a mês</CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={dashboardData?.monthly_indications?.slice(0, 12).reverse() || []}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="month" />
                <YAxis />
                <Tooltip />
                <Bar dataKey="count" fill="#8b5cf6" />
              </BarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        {/* Vendas mês a mês */}
        <Card>
          <CardHeader>
            <CardTitle>Vendas mês a mês</CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={dashboardData?.monthly_sales?.slice(0, 12).reverse() || []}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="month" />
                <YAxis />
                <Tooltip />
                <Line type="monotone" dataKey="count" stroke="#10b981" strokeWidth={2} />
              </LineChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        {/* Conversão por segmento */}
        <Card>
          <CardHeader>
            <CardTitle>Conversão por segmento</CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={dashboardData?.charts?.conversionBySegment || []}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ segment, rate }) => `${segment} ${rate}%`}
                  outerRadius={80}
                  fill="#8884d8"
                  dataKey="total"
                >
                  {(dashboardData?.charts?.conversionBySegment || []).map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip formatter={(value, name) => [value, 'Total de indicações']} />
              </PieChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        {/* Top embaixadoras */}
        <Card>
          <CardHeader>
            <CardTitle>Top melhores embaixadoras (por volume de indicação)</CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={dashboardData?.top_ambassadors?.slice(0, 5) || []} layout="horizontal">
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis type="number" />
                <YAxis dataKey="name" type="category" width={80} />
                <Tooltip />
                <Bar dataKey="total_indications" fill="#f59e0b" />
              </BarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      </div>

      {/* Gestão de Indicações */}
      <Card>
        <CardHeader>
          <CardTitle>Gestão de Indicações</CardTitle>
          <CardDescription>Atualize o status das indicações</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {indications.slice(0, 10).map((indication) => (
              <div key={indication.id} className="flex items-center justify-between p-4 border rounded-lg">
                <div className="flex-1">
                  <h3 className="font-medium">{indication.client_name}</h3>
                  <p className="text-sm text-gray-500">{indication.client_contact}</p>
                  <p className="text-xs text-gray-400">
                    Por: {indication.ambassador_name} • {new Date(indication.created_at).toLocaleDateString('pt-BR')}
                  </p>
                </div>
                <div className="flex items-center space-x-2">
                  <Badge className={getStatusColor(indication.status)}>
                    {indication.status}
                  </Badge>
                  <Select
                    value={indication.status}
                    onValueChange={(value) => updateIndicationStatus(indication.id, value)}
                  >
                    <SelectTrigger className="w-32">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="agendado">Agendado</SelectItem>
                      <SelectItem value="aprovado">Aprovado</SelectItem>
                      <SelectItem value="não aprovado">Não Aprovado</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Gestão de Comissões */}
      <Card>
        <CardHeader>
          <CardTitle>Gestão de Comissões</CardTitle>
          <CardDescription>Marque as parcelas como pagas</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {commissions.slice(0, 10).map((commission) => (
              <div key={commission.id} className="flex items-center justify-between p-4 border rounded-lg">
                <div className="flex-1">
                  <h3 className="font-medium">{commission.client_name}</h3>
                  <p className="text-sm text-gray-500">
                    Embaixadora: {commission.ambassador_name} • Parcela {commission.parcel_number}/3
                  </p>
                  <p className="text-xs text-gray-400">
                    Vencimento: {new Date(commission.due_date).toLocaleDateString('pt-BR')}
                  </p>
                </div>
                <div className="flex items-center space-x-2">
                  <div className="text-right">
                    <p className="font-medium">R$ {commission.amount.toFixed(2)}</p>
                    <Badge className={getPaymentStatusColor(commission.payment_status)}>
                      {commission.payment_status}
                    </Badge>
                  </div>
                  {commission.payment_status === 'pendente' && (
                    <Button
                      size="sm"
                      onClick={() => markCommissionAsPaid(commission.id)}
                      className="bg-green-600 hover:bg-green-700"
                    >
                      <CheckCircle className="w-4 h-4 mr-1" />
                      Marcar como Pago
                    </Button>
                  )}
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Modal */}
      {showModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg shadow-xl w-full max-w-md mx-4">
            {/* Header */}
            <div className="px-6 py-4 border-b border-gray-200">
              <h2 className="text-lg font-semibold text-gray-900">
                Nova Indicação
              </h2>
            </div>

            {/* Form */}
            <form onSubmit={handleModalSubmit} className="px-6 py-4 space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Nome do Cliente
                </label>
                <input
                  type="text"
                  required
                  value={formData.clientName}
                  onChange={(e) => setFormData({...formData, clientName: e.target.value})}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  placeholder="Digite o nome completo do cliente"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Nome da Empresa
                </label>
                <input
                  type="text"
                  required
                  value={formData.companyName || ''}
                  onChange={(e) => setFormData({...formData, companyName: e.target.value})}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  placeholder="Digite o nome da empresa"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Email
                </label>
                <input
                  type="email"
                  required
                  value={formData.clientEmail}
                  onChange={(e) => setFormData({...formData, clientEmail: e.target.value})}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  placeholder="exemplo@email.com"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Telefone
                </label>
                <input
                  type="tel"
                  required
                  value={formData.clientPhone}
                  onChange={(e) => setFormData({...formData, clientPhone: e.target.value})}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  placeholder="(11) 99999-9999"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Origem
                </label>
                <select
                  value={formData.origin}
                  onChange={(e) => setFormData({...formData, origin: e.target.value})}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                >
                  <option value="website">Website</option>
                  <option value="whatsapp">WhatsApp</option>
                  <option value="social_media">Redes Sociais</option>
                  <option value="referral">Indicação</option>
                  <option value="event">Evento</option>
                  <option value="other">Outro</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Segmento
                </label>
                <select
                  value={formData.segment}
                  onChange={(e) => setFormData({...formData, segment: e.target.value})}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                >
                  <option value="">Selecione o segmento</option>
                  <option value="saude">🏥 Saúde</option>
                  <option value="educacao_pesquisa">🧠 Educação e Pesquisa</option>
                  <option value="juridico">🏛️ Jurídico</option>
                  <option value="administracao_negocios">💼 Administração e Negócios</option>
                  <option value="engenharias">🏢 Engenharias</option>
                  <option value="tecnologia_informacao">💻 Tecnologia da Informação</option>
                  <option value="financeiro_bancario">🏦 Financeiro e Bancário</option>
                  <option value="marketing_vendas_comunicacao">📣 Marketing, Vendas e Comunicação</option>
                  <option value="industria_producao">🏭 Indústria e Produção</option>
                  <option value="construcao_civil">🧱 Construção Civil</option>
                  <option value="transportes_logistica">🚛 Transportes e Logística</option>
                  <option value="comercio_varejo">🛒 Comércio e Varejo</option>
                  <option value="turismo_hotelaria_eventos">🏨 Turismo, Hotelaria e Eventos</option>
                  <option value="gastronomia_alimentacao">🍳 Gastronomia e Alimentação</option>
                  <option value="agronegocio_meio_ambiente">🌱 Agronegócio e Meio Ambiente</option>
                  <option value="artes_cultura_design">🎭 Artes, Cultura e Design</option>
                  <option value="midias_digitais_criativas">📱 Mídias Digitais e Criativas</option>
                  <option value="seguranca_defesa">👮 Segurança e Defesa</option>
                  <option value="servicos_gerais">🧹 Serviços Gerais</option>
                  <option value="outro">Outro</option>
                </select>
              </div>

              {formData.segment === 'outro' && (
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Especifique o Segmento
                  </label>
                  <input
                    type="text"
                    required
                    value={formData.customSegment || ''}
                    onChange={(e) => setFormData({...formData, customSegment: e.target.value})}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    placeholder="Digite o segmento específico"
                  />
                </div>
              )}
            </form>

            {/* Footer */}
            <div className="px-6 py-4 border-t border-gray-200 flex justify-end space-x-3">
              <button
                type="button"
                onClick={closeModal}
                className="px-4 py-2 text-sm font-medium text-gray-700 bg-gray-100 border border-gray-300 rounded-md hover:bg-gray-200 focus:outline-none focus:ring-2 focus:ring-gray-500"
              >
                Cancelar
              </button>
              <button
                type="submit"
                onClick={handleModalSubmit}
                className="px-4 py-2 text-sm font-medium text-white bg-blue-600 border border-transparent rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                Criar
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default AdminDashboard;
