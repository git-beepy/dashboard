import React, { useState, useEffect } from 'react';
import { useAuth } from "../contexts/AuthContext";
import { Card, CardContent, CardHeader, CardTitle } from "../components/ui/card";
import { Button } from "../components/ui/button";
import { Input } from "../components/ui/input";
import { Label } from "../components/ui/label";
import { Textarea } from "../components/ui/textarea";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "../components/ui/select";
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell, LineChart, Line } from 'recharts';
import { TrendingUp, Users, DollarSign, Target, ArrowUpRight, ArrowDownRight, Plus } from 'lucide-react';
import axios from 'axios';

const Dashboard = () => {
  const { user, token, API_BASE_URL } = useAuth();
  const [dashboardData, setDashboardData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [formData, setFormData] = useState({
    client_name: '',
    email: '',
    phone: '',
    origin: '',
    segment: ''
  });

  useEffect(() => {
    fetchDashboardData();
  }, [user, token]);

  const fetchDashboardData = async () => {
    try {
      const endpoint = user?.role === 'admin'
        ? `${API_BASE_URL}/api/dashboard/admin`
        : `${API_BASE_URL}/api/dashboard/embaixadora`;

      const response = await axios.get(endpoint, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        withCredentials: true
      });

      if (response.status === 200) {
        setDashboardData(response.data);
      } else {
        console.error('Erro ao buscar dados do dashboard:', response.statusText);
        setDashboardData(getMockData(user?.role));
      }
    } catch (error) {
      console.error('Erro ao buscar dados do dashboard:', error);
      setDashboardData(getMockData(user?.role));
    } finally {
      setLoading(false);
    }
  };

  const handleModalSubmit = async (e) => {
    e.preventDefault();
    try {
      const response = await axios.post(`${API_BASE_URL}/api/indications`, formData, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        withCredentials: true
      });

      if (response.status === 201) {
        alert('Indicação criada com sucesso!');
        setShowModal(false);
        setFormData({
          client_name: '',
          email: '',
          phone: '',
          origin: '',
          segment: ''
        });
        fetchDashboardData(); // Refresh dashboard data
      } else {
        alert('Erro ao criar indicação: ' + response.statusText);
      }
    } catch (error) {
      console.error('Erro ao criar indicação:', error);
      alert('Erro ao criar indicação. Verifique o console para mais detalhes.');
    }
  };

  const closeModal = () => {
    setShowModal(false);
    setFormData({
      client_name: '',
      email: '',
      phone: '',
      origin: '',
      segment: ''
    });
  };

  const getMockData = (role) => {
    if (role === 'admin') {
      return {
        totalCommissions: 6300,
        conversionRate: 36.2,
        totalIndications: 36,
        activeAmbassadors: 29,
        indicationsByMonth: {
          '2025-01': 5,
          '2025-02': 8,
          '2025-03': 6,
          '2025-04': 12,
          '2025-05': 15,
          '2025-06': 18,
          '2025-07': 22,
          '2025-08': 16,
          '2025-09': 14,
          '2025-10': 20,
          '2025-11': 25,
          '2025-12': 28
        },
        leadsByOrigin: {
          'WhatsApp': 60,
          'Email': 30,
          'Instagram': 25,
          'TikTok': 20,
          'Pinterest': 15
        },
        conversionBySegment: {
          'Roupa': { converted: 15, total: 50 },
          'Clínicas': { converted: 25, total: 40 },
          'Loja de Roupa': { converted: 20, total: 35 },
          'Óticas': { converted: 30, total: 45 }
        },
        salesByMonth: {
          '2025-01': 25000,
          '2025-02': 32000,
          '2025-03': 28000,
          '2025-04': 45000,
          '2025-05': 38000,
          '2025-06': 52000,
          '2025-07': 48000,
          '2025-08': 35000,
          '2025-09': 42000,
          '2025-10': 55000,
          '2025-11': 48000,
          '2025-12': 62000
        },
        topAmbassadorsByIndications: {
          'amb1': 45,
          'amb2': 38,
          'amb3': 32,
          'amb4': 28,
          'amb5': 25,
          'amb6': 22,
          'amb7': 20,
          'amb8': 18,
          'amb9': 15,
          'amb10': 12
        }
      };
    } else {
      return {
        totalIndications: 120,
        totalSales: 36,
        monthlyCommission: 900,
        conversionRate: 30,
        commissionsData: [
          { month: 'Jan', comissao: 300 },
          { month: 'Fev', comissao: 350 },
          { month: 'Mar', comissao: 600 },
          { month: 'Abr', comissao: 900 },
          { month: 'Mai', comissao: 300 },
          { month: 'Jun', comissao: 600 },
          { month: 'Jul', comissao: 150 },
          { month: 'Ago', comissao: 200 },
          { month: 'Set', comissao: 250 },
          { month: 'Out', comissao: 250 },
          { month: 'Nov', comissao: 250 },
          { month: 'Dez', comissao: 250 }
        ],
        segmentData: [
          { name: 'ROUPA', value: 15.8, color: '#EF4444' },
          { name: 'CLÍNICAS', value: 29.1, color: '#3B82F6' },
          { name: 'LOJA DE ROUPA', value: 22.2, color: '#8B5CF6' },
          { name: 'ÓTICAS', value: 32.9, color: '#F59E0B' }
        ]
      };
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-lg">Carregando dashboard...</div>
      </div>
    );
  }

  const AdminDashboardContent = () => {
    const COLORS = {
      green: '#10B981',
      orange: '#F59E0B',
      red: '#EF4444',
      purple: '#8B5CF6',
      blue: '#3B82F6'
    };

    const indicationsByMonth = Object.entries(dashboardData?.indicationsByMonth || {}).map(([month, count]) => ({
      month: month.split('-')[1],
      indicacoes: count
    }));

    const leadsByOrigin = Object.entries(dashboardData?.leadsByOrigin || {}).map(([origin, count]) => ({
      origem: origin,
      leads: count
    }));

    const conversionData = Object.entries(dashboardData?.conversionBySegment || {}).map(([segment, data]) => ({
      name: segment,
      value: data.converted,
      total: data.total,
      percentage: ((data.converted / data.total) * 100).toFixed(1)
    }));

    const salesByMonth = Object.entries(dashboardData?.salesByMonth || {}).map(([month, value]) => ({
      month: month.split('-')[1],
      vendas: value
    }));

    const topAmbassadors = Object.entries(dashboardData?.topAmbassadorsByIndications || {}).slice(0, 10).map(([id, count]) => ({
      embaixadora: `Emb ${id.slice(-4)}`,
      indicacoes: count
    }));

    return (
      <div className="p-6 space-y-6 bg-gray-50 min-h-screen">
        {/* Header */}
        <div className="header-gradient p-6 rounded-lg">
          <div className="flex justify-between items-center">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">Dashboard - Visão da agência</h1>
              <p className="text-gray-600 mt-1">Acompanhe as métricas gerais do sistema</p>
            </div>
            <Button
              onClick={() => setShowModal(true)}
              className="btn-primary"
            >
              <Plus className="w-4 h-4 mr-2" />
              NOVA INDICAÇÃO
            </Button>
          </div>
        </div>

        {/* Métricas principais */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <div className="metric-card card-green">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-black text-sm font-medium">COMISSÕES DO MÊS</p>
                <p className="text-black text-2xl font-bold mt-1">R$ {dashboardData?.totalCommissions?.toLocaleString('pt-BR') || '6.300'},00</p>
              </div>
              <DollarSign className="h-8 w-8 text-black/80" />
            </div>
          </div>

          <div className="metric-card card-yellow">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-black text-sm font-medium">CONVERSÃO INDICAÇÕES</p>
                <p className="text-2xl font-bold text-black mt-1">{dashboardData?.conversionRate || 36.2}%</p>
              </div>
              <TrendingUp className="h-8 w-8 text-black/80" />
            </div>
          </div>

          <div className="metric-card card-red">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-black text-sm font-medium">TOTAL DE INDICAÇÕES</p>
                <p className="text-2xl font-bold text-black mt-1">{dashboardData?.totalIndications || 36}</p>
              </div>
              <Target className="h-8 w-8 text-black/80" />
            </div>
          </div>

          <div className="metric-card card-purple">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-black text-sm font-medium">EMBAIXADORAS ATIVAS</p>
                <p className="text-2xl font-bold text-black mt-1">{dashboardData?.activeAmbassadors || 29}</p>
              </div>
              <Users className="h-8 w-8 text-black/80" />
            </div>
          </div>
        </div>

        {/* Gráficos */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* % de Embaixadoras Ativas */}
          <Card className="metric-card">
            <CardHeader>
              <CardTitle className="text-gray-900">% DE EMBAIXADORAS ATIVAS (60 DIAS)</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex items-center justify-center h-64">
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie
                      data={[
                        { name: 'Ativas', value: 38.2, fill: COLORS.purple },
                        { name: 'Não Ativas', value: 61.8, fill: '#E5E7EB' }
                      ]}
                      cx="50%"
                      cy="50%"
                      innerRadius={60}
                      outerRadius={100}
                      paddingAngle={5}
                      dataKey="value"
                    >
                    </Pie>
                    <Tooltip formatter={(value) => `${value}%`} />
                  </PieChart>
                </ResponsiveContainer>
              </div>
              <div className="mt-4 text-center">
                <p className="text-sm text-gray-600">ATIVAS: 38,2% | NÃO ATIVA: 61,8%</p>
              </div>
            </CardContent>
          </Card>

          {/* Indicações Mês a Mês */}
          <Card className="metric-card">
            <CardHeader>
              <CardTitle className="text-gray-900">INDICAÇÕES MÊS A MÊS</CardTitle>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={250}>
                <BarChart data={indicationsByMonth}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="month" />
                  <YAxis />
                  <Tooltip />
                  <Bar dataKey="indicacoes" fill={COLORS.purple} radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>

          {/* Leads Origem da Prospecção */}
          <Card className="metric-card">
            <CardHeader>
              <CardTitle className="text-gray-900">LEADS ORIGEM DA PROSPECÇÃO DA EMBAIXADORA</CardTitle>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={250}>
                <BarChart data={leadsByOrigin}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="origem" />
                  <YAxis />
                  <Tooltip />
                  <Bar dataKey="leads" fill={COLORS.purple} radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>

          {/* Conversão por Segmento */}
          <Card className="metric-card">
            <CardHeader>
              <CardTitle className="text-gray-900">CONVERSÃO POR SEGMENTO</CardTitle>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={250}>
                <PieChart>
                  <Pie
                    data={conversionData}
                    cx="50%"
                    cy="50%"
                    innerRadius={60}
                    outerRadius={100}
                    paddingAngle={5}
                    dataKey="value"
                  >
                    {conversionData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={Object.values(COLORS)[index % Object.values(COLORS).length]} />
                    ))}
                  </Pie>
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>
              <div className="mt-4 grid grid-cols-2 gap-2 text-sm">
                <div className="flex items-center">
                  <div className="w-3 h-3 bg-red-500 rounded-full mr-2"></div>
                  <span>ROUPA</span>
                </div>
                <div className="flex items-center">
                  <div className="w-3 h-3 bg-blue-500 rounded-full mr-2"></div>
                  <span>CLÍNICAS</span>
                </div>
                <div className="flex items-center">
                  <div className="w-3 h-3 bg-purple-500 rounded-full mr-2"></div>
                  <span>LOJA DE ROUPA</span>
                </div>
                <div className="flex items-center">
                  <div className="w-3 h-3 bg-orange-500 rounded-full mr-2"></div>
                  <span>ÓTICAS</span>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Vendas Mês a Mês */}
          <Card className="metric-card">
            <CardHeader>
              <CardTitle className="text-gray-900">VENDAS MÊS A MÊS</CardTitle>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={250}>
                <BarChart data={salesByMonth}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="month" />
                  <YAxis />
                  <Tooltip formatter={(value) => [`R$ ${value.toLocaleString('pt-BR')}`, 'Vendas']} />
                  <Bar dataKey="vendas" fill={COLORS.purple} radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>

          {/* Top Embaixadoras */}
          <Card className="metric-card">
            <CardHeader>
              <CardTitle className="text-gray-900">TOP MELHORES EMBAIXADORAS (POR VOLUME DE INDICAÇÃO)</CardTitle>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={250}>
                <BarChart data={topAmbassadors}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="embaixadora" />
                  <YAxis />
                  <Tooltip />
                  <Bar dataKey="indicacoes" fill={COLORS.purple} radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </div>
      </div>
    );
  };

  const AmbassadorDashboardContent = () => {
    const COLORS = {
      green: '#10B981',
      orange: '#F59E0B',
      red: '#EF4444',
      purple: '#8B5CF6',
      blue: '#3B82F6'
    };

    return (
      <div className="p-6 space-y-6 bg-gray-50 min-h-screen">
        {/* Header */}
        <div className="header-gradient p-6 rounded-lg">
          <div className="flex justify-between items-center">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
              <p className="text-gray-600 mt-1">Acompanhe suas métricas pessoais</p>
            </div>
            <Button
              onClick={() => setShowModal(true)}
              className="btn-primary"
            >
              <Plus className="w-4 h-4 mr-2" />
              Nova Indicação
            </Button>
          </div>
        </div>

        {/* Métricas principais */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="metric-card card-light-green">
            <div className="p-6">
              <p className="text-gray-700 text-sm font-medium">TOTAL DE</p>
              <p className="text-gray-700 text-sm font-medium">INDICAÇÕES</p>
              <p className="text-4xl font-bold text-gray-900 mt-2">{dashboardData?.totalIndications || 120}</p>
              <p className="text-green-600 text-sm mt-2">+{dashboardData?.conversionRate || 30}% de conversão</p>
            </div>
          </div>

          <div className="metric-card card-light-yellow">
            <div className="p-6">
              <p className="text-gray-700 text-sm font-medium">TOTAL DE</p>
              <p className="text-gray-700 text-sm font-medium">VENDAS</p>
              <p className="text-4xl font-bold text-gray-900 mt-2">{dashboardData?.totalSales || 36}</p>
              <p className="text-orange-600 text-sm mt-2">+13% acima da média</p>
            </div>
          </div>

          <div className="metric-card card-yellow">
            <div className="p-6 relative">
              <p className="text-white text-sm font-medium">COMISSÃO DO MÊS</p>
              <p className="text-4xl font-bold text-white mt-2">R$ {dashboardData?.monthlyCommission || 900},00</p>
              <p className="text-white/80 text-sm mt-2">Total a receber em julho /2025</p>
              <p className="text-white/80 text-xs">pagamento até 31/07/2025</p>
              <div className="absolute top-4 right-4 bg-white/20 rounded-lg p-2">
                <span className="text-white text-xs font-bold">20/30</span>
              </div>
            </div>
          </div>
        </div>

        {/* Gráficos */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Comissões mês a mês */}
          <Card className="metric-card">
            <CardHeader>
              <CardTitle className="text-gray-900">Suas comissões mês a mês</CardTitle>
              <div className="text-sm text-gray-500">JUNHO</div>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={300}>
                <LineChart data={dashboardData?.commissionsData || []}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="month" />
                  <YAxis />
                  <Tooltip
                    formatter={(value) => [`R$ ${value}`, 'Comissão']}
                    labelFormatter={(label) => `${label}: Comissão: 600`}
                  />
                  <Line
                    type="monotone"
                    dataKey="comissao"
                    stroke={COLORS.blue}
                    strokeWidth={3}
                    dot={{ fill: COLORS.blue, strokeWidth: 2, r: 6 }}
                    activeDot={{ r: 8, fill: COLORS.blue }}
                  />
                </LineChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>

          {/* Indicações por segmento */}
          <Card className="metric-card">
            <CardHeader>
              <CardTitle className="text-gray-900">Indicações por segmento do cliente</CardTitle>
              <div className="text-sm text-gray-500">This year</div>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={300}>
                <PieChart>
                  <Pie
                    data={dashboardData?.segmentData || []}
                    cx="50%"
                    cy="50%"
                    innerRadius={60}
                    outerRadius={120}
                    paddingAngle={5}
                    dataKey="value"
                  >
                    {(dashboardData?.segmentData || []).map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                  <Tooltip formatter={(value) => `${value}%`} />
                </PieChart>
              </ResponsiveContainer>
              <div className="mt-4 grid grid-cols-2 gap-2 text-sm">
                {(dashboardData?.segmentData || []).map((item, index) => (
                  <div key={index} className="flex items-center">
                    <div className="w-3 h-3 rounded-full mr-2" style={{ backgroundColor: item.color }}></div>
                    <span>{item.name}</span>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    );
  };

  return (
    <div className="relative">
      {user?.role === 'admin' ? <AdminDashboardContent /> : <AmbassadorDashboardContent />}

      {/* Modal Nova Indicação */}
      {showModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-lg shadow-xl w-full max-w-md mx-auto">
            {/* Header do Modal */}
            <div className="px-6 py-4 border-b border-gray-200">
              <h3 className="text-lg font-semibold text-gray-900">Nova Indicação</h3>
            </div>

            {/* Corpo do Formulário */}
            <form onSubmit={handleModalSubmit} className="p-6 space-y-4">
              <div>
                <label htmlFor="client_name" className="block text-sm font-medium text-gray-700">Nome do Cliente</label>
                <input
                  type="text"
                  id="client_name"
                  name="client_name"
                  value={formData.client_name}
                  onChange={(e) => setFormData({ ...formData, client_name: e.target.value })}
                  className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                  required
                />
              </div>
              <div>
                <label htmlFor="email" className="block text-sm font-medium text-gray-700">Email</label>
                <input
                  type="email"
                  id="email"
                  name="email"
                  value={formData.email}
                  onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                  className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                  required
                />
              </div>
              <div>
                <label htmlFor="phone" className="block text-sm font-medium text-gray-700">Telefone</label>
                <input
                  type="tel"
                  id="phone"
                  name="phone"
                  value={formData.phone}
                  onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
                  className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                  required
                />
              </div>
              <div>
                <label htmlFor="origin" className="block text-sm font-medium text-gray-700">Origem</label>
                <select
                  id="origin"
                  name="origin"
                  value={formData.origin}
                  onChange={(e) => setFormData({ ...formData, origin: e.target.value })}
                  className="mt-1 block w-full pl-3 pr-10 py-2 text-base border border-gray-300 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm rounded-md"
                  required
                >
                  <option value="">Selecione a origem</option>
                  <option value="website">Website</option>
                  <option value="instagram">Instagram</option>
                  <option value="facebook">Facebook</option>
                  <option value="indicacao">Indicação</option>
                  <option value="outros">Outros</option>
                </select>
              </div>
              <div>
                <label htmlFor="segment" className="block text-sm font-medium text-gray-700">Segmento</label>
                <select
                  id="segment"
                  name="segment"
                  value={formData.segment}
                  onChange={(e) => setFormData({ ...formData, segment: e.target.value })}
                  className="mt-1 block w-full pl-3 pr-10 py-2 text-base border border-gray-300 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm rounded-md"
                  required
                >
                  <option value="">Selecione o segmento</option>
                  <option value="geral">Geral</option>
                  <option value="premium">Premium</option>
                  <option value="corporativo">Corporativo</option>
                  <option value="startup">Startup</option>
                </select>
              </div>
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

export default Dashboard;
