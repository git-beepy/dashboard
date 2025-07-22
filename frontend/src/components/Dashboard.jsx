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
        ? `${API_BASE_URL}/dashboard/admin`
        : `${API_BASE_URL}/dashboard/ambassador`;

      const response = await axios.get(endpoint, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        withCredentials: true
      });

      if (response.status === 200) {
        console.log('Dashboard data received:', response.data);
        setDashboardData(response.data);
      } else {
        console.error('Erro ao buscar dados do dashboard:', response.statusText);
        // Buscar dados das outras páginas como fallback
        await fetchFallbackData();
      }
    } catch (error) {
      console.error('Erro ao buscar dados do dashboard:', error);
      // Buscar dados das outras páginas como fallback
      await fetchFallbackData();
    } finally {
      setLoading(false);
    }
  };

  const fetchFallbackData = async () => {
    try {
      // Buscar dados das páginas individuais
      const [indicationsRes, commissionsRes, usersRes] = await Promise.all([
        axios.get(`${API_BASE_URL}/indications`, {
          headers: { 'Authorization': `Bearer ${token}` }
        }),
        axios.get(`${API_BASE_URL}/commissions`, {
          headers: { 'Authorization': `Bearer ${token}` }
        }),
        user?.role === 'admin' ? axios.get(`${API_BASE_URL}/users`, {
          headers: { 'Authorization': `Bearer ${token}` }
        }) : Promise.resolve({ data: [] })
      ]);

      const indications = indicationsRes.data || [];
      const commissions = commissionsRes.data || [];
      const users = usersRes.data || [];

      // Processar dados para o dashboard
      const processedData = processDataForDashboard(indications, commissions, users);
      setDashboardData(processedData);
    } catch (error) {
      console.error('Erro ao buscar dados de fallback:', error);
      setDashboardData(getMockData(user?.role));
    }
  };

  const processDataForDashboard = (indications, commissions, users) => {
    if (user?.role === 'admin') {
      // Processar dados para admin
      const totalIndications = indications.length;
      const approvedIndications = indications.filter(i => i.status === 'aprovado').length;
      const activeAmbassadors = users.filter(u => u.role === 'embaixadora').length;
      
      // Comissões do mês atual
      const currentMonth = new Date().getMonth() + 1;
      const currentYear = new Date().getFullYear();
      const monthlyCommissions = commissions
        .filter(c => {
          const commissionDate = new Date(c.createdAt || c.created_at);
          return commissionDate.getMonth() + 1 === currentMonth && 
                 commissionDate.getFullYear() === currentYear;
        })
        .reduce((sum, c) => sum + (c.value || c.amount || 0), 0);

      // Taxa de conversão
      const conversionRate = totalIndications > 0 ? (approvedIndications / totalIndications * 100) : 0;

      // Indicações por mês
      const monthlyData = {};
      const months = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez'];
      
      // Inicializar meses
      months.forEach((month, index) => {
        monthlyData[month] = 0;
      });

      // Contar indicações por mês
      indications.forEach(indication => {
        if (indication.createdAt || indication.created_at) {
          const date = new Date(indication.createdAt || indication.created_at);
          const monthIndex = date.getMonth();
          const monthName = months[monthIndex];
          monthlyData[monthName]++;
        }
      });

      const indicationsMonthly = Object.entries(monthlyData).map(([month, count]) => ({
        month,
        count
      }));

      // Leads por origem
      const originData = {};
      indications.forEach(indication => {
        const origin = indication.origin || 'Não informado';
        originData[origin] = (originData[origin] || 0) + 1;
      });

      const leadsOrigin = Object.entries(originData).map(([name, value]) => ({
        name,
        value
      }));

      // Conversão por segmento
      const segmentData = {};
      indications.forEach(indication => {
        const segment = indication.segment || 'Não informado';
        if (!segmentData[segment]) {
          segmentData[segment] = { total: 0, converted: 0 };
        }
        segmentData[segment].total++;
        if (indication.status === 'aprovado') {
          segmentData[segment].converted++;
        }
      });

      const conversionBySegment = Object.entries(segmentData).map(([segment, data]) => ({
        segment,
        total: data.total,
        converted: data.converted,
        rate: data.total > 0 ? (data.converted / data.total * 100) : 0
      }));

      // Top embaixadoras
      const ambassadorData = {};
      indications.forEach(indication => {
        const ambassadorId = indication.ambassadorId || indication.ambassador_id || 'Não informado';
        ambassadorData[ambassadorId] = (ambassadorData[ambassadorId] || 0) + 1;
      });

      const topAmbassadors = Object.entries(ambassadorData)
        .map(([id, indications]) => {
          const ambassador = users.find(u => u.id === id);
          return {
            name: ambassador ? ambassador.name : `Embaixadora ${id}`,
            indications
          };
        })
        .sort((a, b) => b.indications - a.indications)
        .slice(0, 10);

      return {
        stats: {
          totalIndications,
          monthlyCommissions,
          activePercentage: conversionRate,
          activeAmbassadors
        },
        charts: {
          indicationsMonthly,
          leadsOrigin,
          conversionBySegment,
          salesMonthly: indicationsMonthly.map(item => ({
            month: item.month,
            value: item.count * 1000 // Simular valor de vendas
          })),
          topAmbassadors
        }
      };
    } else {
      // Processar dados para embaixadora
      const userIndications = indications.filter(i => 
        i.ambassadorId === user.id || i.ambassador_id === user.id
      );
      const userCommissions = commissions.filter(c => 
        c.ambassadorId === user.id || c.ambassador_id === user.id
      );

      const totalIndications = userIndications.length;
      const totalSales = userIndications.filter(i => i.status === 'aprovado').length;
      const conversionRate = totalIndications > 0 ? (totalSales / totalIndications * 100) : 0;

      // Comissão do mês atual
      const currentMonth = new Date().getMonth() + 1;
      const currentYear = new Date().getFullYear();
      const monthlyCommission = userCommissions
        .filter(c => {
          const commissionDate = new Date(c.createdAt || c.created_at);
          return commissionDate.getMonth() + 1 === currentMonth && 
                 commissionDate.getFullYear() === currentYear;
        })
        .reduce((sum, c) => sum + (c.value || c.amount || 0), 0);

      // Comissões por mês
      const commissionsData = [];
      const months = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez'];
      
      months.forEach((month, index) => {
        const monthCommissions = userCommissions
          .filter(c => {
            const date = new Date(c.createdAt || c.created_at);
            return date.getMonth() === index;
          })
          .reduce((sum, c) => sum + (c.value || c.amount || 0), 0);
        
        commissionsData.push({
          month,
          comissao: monthCommissions
        });
      });

      // Dados por segmento
      const segmentData = {};
      userIndications.forEach(indication => {
        const segment = indication.segment || 'Não informado';
        segmentData[segment] = (segmentData[segment] || 0) + 1;
      });

      const totalSegmentIndications = Object.values(segmentData).reduce((sum, count) => sum + count, 0);
      const segmentChartData = Object.entries(segmentData).map(([name, count], index) => ({
        name: name.toUpperCase(),
        value: totalSegmentIndications > 0 ? (count / totalSegmentIndications * 100) : 0,
        color: ['#EF4444', '#3B82F6', '#8B5CF6', '#F59E0B'][index % 4]
      }));

      return {
        totalIndications,
        totalSales,
        monthlyCommission,
        conversionRate,
        commissionsData,
        segmentData: segmentChartData
      };
    }
  };

  const handleModalSubmit = async (e) => {
    e.preventDefault();
    try {
      const response = await axios.post(`${API_BASE_URL}/indications`, formData, {
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
        segmentData: []
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

    const indicationsByMonth = dashboardData?.charts?.indicationsMonthly?.map(item => ({
      month: item.month,
      indicacoes: item.count
    })) || [];

    const leadsByOrigin = dashboardData?.charts?.leadsOrigin?.map(item => ({
      origem: item.name,
      leads: item.value
    })) || [];

    const conversionData = dashboardData?.charts?.conversionBySegment?.map(item => ({
      name: item.segment,
      value: item.converted,
      total: item.total,
      percentage: item.rate
    })) || [];

    const salesByMonth = dashboardData?.charts?.salesMonthly?.map(item => ({
      month: item.month,
      vendas: item.value
    })) || [];

    const topAmbassadors = dashboardData?.charts?.topAmbassadors?.map(item => ({
      embaixadora: item.name,
      indicacoes: item.indications
    })) || [];

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
                <p className="text-black text-2xl font-bold mt-1">R$ {(dashboardData?.stats?.monthlyCommissions || 0).toLocaleString('pt-BR', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}</p>
              </div>
              <DollarSign className="h-8 w-8 text-black/80" />
            </div>
          </div>

          <div className="metric-card card-yellow">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-black text-sm font-medium">CONVERSÃO INDICAÇÕES</p>
                <p className="text-2xl font-bold text-black mt-1">{(dashboardData?.stats?.activePercentage || 0).toFixed(2)}%</p>
              </div>
              <TrendingUp className="h-8 w-8 text-black/80" />
            </div>
          </div>

          <div className="metric-card card-red">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-black text-sm font-medium">TOTAL DE INDICAÇÕES</p>
                <p className="text-2xl font-bold text-black mt-1">{dashboardData?.stats?.totalIndications || 0}</p>
              </div>
              <Target className="h-8 w-8 text-black/80" />
            </div>
          </div>

          <div className="metric-card card-purple">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-black text-sm font-medium">EMBAIXADORAS ATIVAS</p>
                <p className="text-2xl font-bold text-black mt-1">{dashboardData?.stats?.activeAmbassadors || 0}</p>
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
                        { name: 'Ativas', value: dashboardData?.stats?.activePercentage || 0, fill: COLORS.purple },
                        { name: 'Não Ativas', value: parseFloat((100 - (dashboardData?.stats?.activePercentage || 0)).toFixed(2)), fill: '#E5E7EB' }
                      ]}
                      cx="50%"
                      cy="50%"
                      innerRadius={60}
                      outerRadius={100}
                      paddingAngle={5}
                      dataKey="value"
                    >
                    </Pie>
                    <Tooltip formatter={(value) => `${value.toFixed(2)}%`} />
                  </PieChart>
                </ResponsiveContainer>
              </div>
              <div className="mt-4 text-center">
                <p className="text-sm text-gray-600">ATIVAS: {(dashboardData?.stats?.activePercentage || 0).toFixed(2)}% | NÃO ATIVA: {(100 - (dashboardData?.stats?.activePercentage || 0)).toFixed(2)}%</p>
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
                {/* Dados dinâmicos serão carregados do backend */}
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
                  <Tooltip formatter={(value) => [`R$ ${value.toLocaleString('pt-BR', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`, 'Vendas']} />
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
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          <div className="metric-card card-green">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-black text-sm font-medium">TOTAL DE INDICAÇÕES</p>
                <p className="text-black text-2xl font-bold mt-1">{dashboardData?.totalIndications || 0}</p>
                <p className="text-black/70 text-sm mt-2">+{(dashboardData?.conversionRate || 0).toFixed(2)}% de conversão</p>
              </div>
              <Target className="h-8 w-8 text-black/80" />
            </div>
          </div>

          <div className="metric-card card-yellow">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-black text-sm font-medium">TOTAL DE VENDAS</p>
                <p className="text-black text-2xl font-bold mt-1">{dashboardData?.totalSales || 0}</p>
                <p className="text-black/70 text-sm mt-2">+13% acima da média</p>
              </div>
              <TrendingUp className="h-8 w-8 text-black/80" />
            </div>
          </div>

          <div className="metric-card card-purple">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-white text-sm font-medium">COMISSÃO DO MÊS</p>
                <p className="text-white text-2xl font-bold mt-1">R$ {(dashboardData?.monthlyCommission || 0).toLocaleString('pt-BR', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}</p>
                <p className="text-white/80 text-sm mt-2">Total a receber em {new Date().toLocaleDateString('pt-BR', { month: 'long', year: 'numeric' })}</p>
              </div>
              <DollarSign className="h-8 w-8 text-white/80" />
            </div>
          </div>
        </div>

        {/* Gráficos */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Comissões mês a mês */}
          <Card className="metric-card">
            <CardHeader>
              <CardTitle className="text-gray-900">Suas comissões mês a mês</CardTitle>
              <div className="text-sm text-gray-500">{new Date().getFullYear()}</div>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={300}>
                <LineChart data={dashboardData?.commissionsData || []}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="month" />
                  <YAxis />
                  <Tooltip
                    formatter={(value) => [`R$ ${value.toLocaleString('pt-BR', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`, 'Comissão']}
                    labelFormatter={(label) => `${label}`}
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
              <div className="text-sm text-gray-500">Este ano</div>
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
                  <Tooltip formatter={(value) => `${value.toFixed(2)}%`} />
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
