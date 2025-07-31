import React, { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from ../ui/card';
import { Button } from ../ui/button';
import { Badge } from ../ui/badge';
import { Plus, TrendingUp, Users, DollarSign, Calendar, BarChart3, Eye, UserPlus } from 'lucide-react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell, BarChart, Bar } from 'recharts';
import { StatsCard, IndicationsTable, CommissionsTable, NewIndicationForm } from './SharedComponents';
import { useDashboardRealtime, useFirestoreCRUD } from '../../hooks/useFirestoreRealtime';
import { useRealtime } from '../../contexts/RealtimeContext';
import RealtimeIndicator from './RealtimeIndicator';
import { Select, SelectItem } from ../ui/select'; // Importações corrigidas

const COLORS = ['#f59e0b', '#10b981', '#3b82f6', '#ef4444', '#8b5cf6', '#f97316'];

const UnifiedDashboard = ({ user, isAdmin = false }) => {
  const [showNewIndicationForm, setShowNewIndicationForm] = useState(false);
  const [showCreateUserForm, setShowCreateUserForm] = useState(false);
  const [showGraphs, setShowGraphs] = useState(false);

  const { data: dashboardData, loading, error } = useDashboardRealtime(user?.role);
  const { data: users } = useFirestoreCRUD('users');
  const { notifyChange } = useRealtime();

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
          <p className="mt-4 text-gray-600">Carregando dashboard...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <p className="text-red-600">Erro ao carregar dashboard: {error}</p>
          <Button onClick={() => window.location.reload()} className="mt-4">
            Tentar Novamente
          </Button>
        </div>
      </div>
    );
  }

  const stats = dashboardData?.stats || {};
  const charts = dashboardData?.charts || {};

  // Configurar cards de estatísticas baseado no tipo de usuário
  const getStatsCards = () => {
    if (isAdmin) {
      return [
        {
          title: "Total de Indicações",
          value: stats.totalIndications || 0,
          description: `${stats.approvedIndications || 0} aprovadas, ${stats.pendingIndications || 0} pendentes`,
          icon: TrendingUp,
          color: "blue",
          trend: stats.approvalRate ? (stats.approvalRate - 50) : null
        },
        {
          title: "Embaixadoras Ativas",
          value: stats.activeAmbassadors || 0,
          description: `${stats.activePercentage || 0}% do total`,
          icon: Users,
          color: "green"
        },
        {
          title: "Comissões do Mês",
          value: `R$ ${(stats.monthlyCommissions || 0).toFixed(2)}`,
          description: `${stats.paidCommissions || 0} pagas, ${stats.pendingCommissions || 0} pendentes`,
          icon: DollarSign,
          color: "yellow"
        },
        {
          title: "Taxa de Aprovação",
          value: `${stats.approvalRate || 0}%`,
          description: "Indicações aprovadas vs total",
          icon: BarChart3,
          color: "purple"
        }
      ];
    } else {
      return [
        {
          title: "Suas Indicações",
          value: stats.totalIndications || 0,
          description: `${stats.approvedIndications || 0} aprovadas`,
          icon: TrendingUp,
          color: "blue"
        },
        {
          title: "Taxa de Conversão",
          value: `${stats.conversionRate || 0}%`,
          description: "Suas indicações aprovadas",
          icon: BarChart3,
          color: "green"
        },
        {
          title: "Comissões Totais",
          value: `R$ ${(stats.totalCommissions || 0).toFixed(2)}`,
          description: `R$ ${(stats.monthlyCommission || 0).toFixed(2)} este mês`,
          icon: DollarSign,
          color: "yellow"
        },
        {
          title: "Status Geral",
          value: `${stats.paidCommissions || 0}/${stats.totalIndications || 0}`,
          description: "Comissões pagas vs indicações",
          icon: Calendar,
          color: "purple"
        }
      ];
    }
  };

  const statsCards = getStatsCards();

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center">
              <div className="flex items-center space-x-2">
                <div className="w-8 h-8 bg-yellow-400 rounded-lg flex items-center justify-center">
                  <BarChart3 className="w-5 h-5 text-gray-900" />
                </div>
                <h1 className="text-xl font-bold text-gray-900">Beepy</h1>
                <Badge variant="outline" className="ml-2">
                  {isAdmin ? 'Administrador' : 'Embaixadora'}
                </Badge>
              </div>
            </div>

            <div className="flex items-center space-x-4">
              <RealtimeIndicator />
              
              <div className="flex items-center space-x-2">
                <span className="text-sm text-gray-700">{user?.name}</span>
              </div>

              <div className="flex space-x-2">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setShowGraphs(!showGraphs)}
                  className="flex items-center space-x-1"
                >
                  <BarChart3 className="w-4 h-4" />
                  <span>{showGraphs ? 'Ocultar' : 'Mostrar'} Gráficos</span>
                </Button>

                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setShowNewIndicationForm(true)}
                  className="flex items-center space-x-1"
                >
                  <Plus className="w-4 h-4" />
                  <span>Nova Indicação</span>
                </Button>

                {isAdmin && (
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => setShowCreateUserForm(true)}
                    className="flex items-center space-x-1"
                  >
                    <UserPlus className="w-4 h-4" />
                    <span>Novo Usuário</span>
                  </Button>
                )}
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          {statsCards.map((card, index) => (
            <StatsCard
              key={index}
              title={card.title}
              value={card.value}
              description={card.description}
              icon={card.icon}
              color={card.color}
              trend={card.trend}
            />
          ))}
        </div>

        {/* Gráficos (condicionalmente exibidos) */}
        {showGraphs && charts && (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
            {/* Indicações por mês */}
            {charts.indicationsMonthly && (
              <Card>
                <CardHeader>
                  <CardTitle>
                    {isAdmin ? 'Indicações por Mês' : 'Suas Indicações por Mês'}
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <ResponsiveContainer width="100%" height={300}>
                    <LineChart data={charts.indicationsMonthly}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="month" />
                      <YAxis />
                      <Tooltip />
                      <Line type="monotone" dataKey="count" stroke="#3b82f6" strokeWidth={2} />
                      <Line type="monotone" dataKey="approved" stroke="#10b981" strokeWidth={2} />
                    </LineChart>
                  </ResponsiveContainer>
                </CardContent>
              </Card>
            )}

            {/* Leads por origem */}
            {charts.leadsOrigin && (
              <Card>
                <CardHeader>
                  <CardTitle>Leads por Origem</CardTitle>
                </CardHeader>
                <CardContent>
                  <ResponsiveContainer width="100%" height={300}>
                    <PieChart>
                      <Pie
                        data={charts.leadsOrigin}
                        cx="50%"
                        cy="50%"
                        labelLine={false}
                        label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                        outerRadius={80}
                        fill="#8884d8"
                        dataKey="value"
                      >
                        {charts.leadsOrigin.map((entry, index) => (
                          <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                        ))}
                      </Pie>
                      <Tooltip />
                    </PieChart>
                  </ResponsiveContainer>
                </CardContent>
              </Card>
            )}

            {/* Conversão por segmento */}
            {charts.conversionBySegment && (
              <Card>
                <CardHeader>
                  <CardTitle>Conversão por Segmento</CardTitle>
                </CardHeader>
                <CardContent>
                  <ResponsiveContainer width="100%" height={300}>
                    <BarChart data={charts.conversionBySegment}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="segment" />
                      <YAxis />
                      <Tooltip />
                      <Bar dataKey="rate" fill="#f59e0b" />
                    </BarChart>
                  </ResponsiveContainer>
                </CardContent>
              </Card>
            )}

            {/* Top embaixadoras (apenas admin) */}
            {isAdmin && charts.topAmbassadors && (
              <Card>
                <CardHeader>
                  <CardTitle>Top Embaixadoras</CardTitle>
                </CardHeader>
                <CardContent>
                  <ResponsiveContainer width="100%" height={300}>
                    <BarChart data={charts.topAmbassadors} layout="horizontal">
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis type="number" />
                      <YAxis dataKey="name" type="category" width={80} />
                      <Tooltip />
                      <Bar dataKey="indications" fill="#8b5cf6" />
                    </BarChart>
                  </ResponsiveContainer>
                </CardContent>
              </Card>
            )}
          </div>
        )}

        {/* Tabelas de Dados */}
        <div className="space-y-6">
          <IndicationsTable isAdmin={isAdmin} />
          <CommissionsTable isAdmin={isAdmin} />
        </div>

        {/* Lista de Usuários (apenas admin) */}
        {isAdmin && (
          <Card className="mt-6">
            <CardHeader>
              <CardTitle>Usuários do Sistema</CardTitle>
              <CardDescription>Gerencie embaixadoras e administradores</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {users && users.length > 0 ? (
                  users.map((user) => (
                    <div key={user.id} className="flex items-center justify-between p-4 border rounded-lg">
                      <div className="flex-1">
                        <h3 className="font-medium">{user.name}</h3>
                        <p className="text-sm text-gray-500">{user.email}</p>
                        <p className="text-xs text-gray-400">
                          {new Date(user.createdAt).toLocaleDateString('pt-BR')}
                        </p>
                      </div>
                      <div className="flex items-center space-x-2">
                        <Badge className={user.role === 'admin' ? 'bg-purple-100 text-purple-800' : 'bg-blue-100 text-blue-800'}>
                          {user.role}
                        </Badge>
                        <Badge className={user.active ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}>
                          {user.active ? 'Ativo' : 'Inativo'}
                        </Badge>
                      </div>
                    </div>
                  ))
                ) : (
                  <div className="text-center p-8 text-gray-500">
                    Nenhum usuário encontrado
                  </div>
                )}
              </div>
            </CardContent>
          </Card>
        )}
      </main>

      {/* Modal Nova Indicação */}
      {showNewIndicationForm && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <NewIndicationForm
            onClose={() => setShowNewIndicationForm(false)}
            onSuccess={() => {
              setShowNewIndicationForm(false);
              notifyChange('success', 'Indicação criada com sucesso!');
            }}
          />
        </div>
      )}

      {/* Modal Criar Usuário (apenas admin) */}
      {isAdmin && showCreateUserForm && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <CreateUserForm
            onClose={() => setShowCreateUserForm(false)}
            onSuccess={() => {
              setShowCreateUserForm(false);
              notifyChange('success', 'Usuário criado com sucesso!');
            }}
          />
        </div>
      )}
    </div>
  );
};

// Componente para criar usuário (apenas admin)
const CreateUserForm = ({ onClose, onSuccess }) => {
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    password: '',
    role: 'embaixadora'
  });

  const { create } = useFirestoreCRUD('users');
  const { notifyChange } = useRealtime();
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);

    const result = await create(formData);
    
    if (result.success) {
      notifyChange('success', 'Usuário criado com sucesso!');
      setFormData({
        name: '',
        email: '',
        password: '',
        role: 'embaixadora'
      });
      onSuccess && onSuccess(result.data);
      onClose && onClose();
    } else {
      notifyChange('error', result.error || 'Erro ao criar usuário');
    }

    setLoading(false);
  };

  const handleChange = (field, value) => {
    setFormData(prev => ({ ...prev, [field]: value }));
  };

  return (
    <Card className="w-full max-w-md">
      <CardHeader>
        <CardTitle>Novo Usuário</CardTitle>
        <CardDescription>Cadastre uma nova embaixadora ou administrador</CardDescription>
      </CardHeader>
      <CardContent>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="name">Nome</Label>
            <Input
              id="name"
              value={formData.name}
              onChange={(e) => handleChange('name', e.target.value)}
              placeholder="Digite o nome completo"
              required
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="email">Email</Label>
            <Input
              id="email"
              type="email"
              value={formData.email}
              onChange={(e) => handleChange('email', e.target.value)}
              placeholder="Digite o email"
              required
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="password">Senha</Label>
            <Input
              id="password"
              type="password"
              value={formData.password}
              onChange={(e) => handleChange('password', e.target.value)}
              placeholder="Digite a senha"
              required
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="role">Função</Label>
            <Select value={formData.role} onValueChange={(value) => handleChange('role', value)}>
              <SelectItem value="embaixadora">Embaixadora</SelectItem>
              <SelectItem value="admin">Administrador</SelectItem>
            </Select>
          </div>

          <div className="flex space-x-2">
            <Button type="submit" disabled={loading} className="flex-1">
              {loading ? 'Criando...' : 'Criar Usuário'}
            </Button>
            <Button type="button" variant="outline" onClick={onClose}>
              Cancelar
            </Button>
          </div>
        </form>
      </CardContent>
    </Card>
  );
};

export default UnifiedDashboard;


