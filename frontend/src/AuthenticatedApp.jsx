import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Badge } from '@/components/ui/badge';
import { Plus, TrendingUp, Users, DollarSign, Calendar, LogOut, User, BarChart3, Lock, UserPlus, Eye, EyeOff } from 'lucide-react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell, BarChart, Bar } from 'recharts';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;

const AuthenticatedApp = () => {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [currentUser, setCurrentUser] = useState(null);
  const [userType, setUserType] = useState('admin');
  const [showNewIndicationForm, setShowNewIndicationForm] = useState(false);
  const [showCreateUserForm, setShowCreateUserForm] = useState(false);
  const [showPassword, setShowPassword] = useState(false);

  // Estados para login
  const [loginData, setLoginData] = useState({
    username: '',
    password: ''
  });

  // Estados para criação de usuário
  const [newUserData, setNewUserData] = useState({
    name: '',
    email: '',
    user_type: 'embaixadora',
    password: ''
  });

  // Estados para indicação
  const [formData, setFormData] = useState({
    client_name: '',
    company_name: '',
    client_email: '',
    client_contact: '',
    origin: 'website',
    niche: '',
    custom_segment: '',
    observations: ''
  });

  // Lista de usuários (simulada)
  const [users, setUsers] = useState([
    { id: 1, name: 'Admin Beepy', email: 'admin@beepy.com', user_type: 'admin' },
    { id: 2, name: 'Mariana Lopes', email: 'mariana@teste.com', user_type: 'embaixadora' },
    { id: 3, name: 'Julia Santos', email: 'julia@teste.com', user_type: 'embaixadora' }
  ]);

  // Dados mockados (mesmo do componente anterior)
  const ambassadorData = {
    stats: {
      total_indications: 120,
      approved_sales: 36,
      current_month_commission: 900,
      conversion_rate: 30
    },
    monthly_commissions: [
      { month: '2024-01', total: 300 },
      { month: '2024-02', total: 600 },
      { month: '2024-03', total: 900 },
      { month: '2024-04', total: 300 },
      { month: '2024-05', total: 600 },
      { month: '2024-06', total: 900 },
      { month: '2024-07', total: 900 }
    ],
    niche_stats: [
      { niche: 'Roupa', count: 40 },
      { niche: 'Clínicas', count: 30 },
      { niche: 'Loja de Roupa', count: 25 },
      { niche: 'Óticas', count: 25 }
    ]
  };

  const adminData = {
    stats: {
      total_indications: 36,
      total_sales: 29,
      total_ambassadors: users.filter(u => u.user_type === 'embaixadora').length,
      commissions_to_pay: 6300,
      conversion_rate: 36.2
    },
    monthly_indications: [
      { month: '2024-01', count: 10 },
      { month: '2024-02', count: 15 },
      { month: '2024-03', count: 20 },
      { month: '2024-04', count: 25 },
      { month: '2024-05', count: 30 },
      { month: '2024-06', count: 35 },
      { month: '2024-07', count: 36 }
    ],
    monthly_sales: [
      { month: '2024-01', count: 8 },
      { month: '2024-02', count: 12 },
      { month: '2024-03', count: 18 },
      { month: '2024-04', count: 22 },
      { month: '2024-05', count: 26 },
      { month: '2024-06', count: 28 },
      { month: '2024-07', count: 29 }
    ],
    niche_conversion: [
      { niche: 'Salão', total: 15, conversion_rate: 13.1 },
      { niche: 'Médico', total: 12, conversion_rate: 30.3 },
      { niche: 'Clínica', total: 8, conversion_rate: 28.6 },
      { niche: 'Loja', total: 6, conversion_rate: 28 }
    ],
    top_ambassadors: [
      { name: 'Mariana Lopes', total_indications: 45000 },
      { name: 'Julia Santos', total_indications: 40000 },
      { name: 'Ana Costa', total_indications: 35000 },
      { name: 'Carla Silva', total_indications: 30000 },
      { name: 'Beatriz Lima', total_indications: 25000 }
    ]
  };

  const indications = [
    {
      id: 1,
      client_name: 'Studio Shodwe',
      client_contact: '#123-456-7890',
      niche: 'roupa',
      status: 'agendado',
      created_at: '2024-05-02T19:00:00Z',
      ambassador_name: 'Mariana Lopes'
    },
    {
      id: 2,
      client_name: 'Borcelle',
      client_contact: '$ 900,50',
      niche: 'clinicas',
      status: 'aprovado',
      created_at: '2024-05-02T18:00:00Z',
      ambassador_name: 'Mariana Lopes'
    },
    {
      id: 3,
      client_name: 'Fauget',
      client_contact: '$ 1.000,50',
      niche: 'loja de roupa',
      status: 'não aprovado',
      created_at: '2024-05-02T17:00:00Z',
      ambassador_name: 'Mariana Lopes'
    },
    {
      id: 4,
      client_name: 'Larana, Inc.',
      client_contact: '$ 900,50',
      niche: 'oticas',
      status: 'não aprovado',
      created_at: '2024-05-01T16:00:00Z',
      ambassador_name: 'Mariana Lopes'
    }
  ];

  const commissions = [
    {
      id: 1,
      client_name: 'Borcelle',
      ambassador_name: 'Mariana Lopes',
      parcel_number: 1,
      amount: 300,
      due_date: '2024-05-02',
      payment_status: 'pago'
    },
    {
      id: 2,
      client_name: 'Borcelle',
      ambassador_name: 'Mariana Lopes',
      parcel_number: 2,
      amount: 300,
      due_date: '2024-06-02',
      payment_status: 'pendente'
    },
    {
      id: 3,
      client_name: 'Ótica Vision',
      ambassador_name: 'Julia Santos',
      parcel_number: 1,
      amount: 300,
      due_date: '2024-07-02',
      payment_status: 'pendente'
    }
  ];

  // Função de login
  const handleLogin = async (e) => {
    e.preventDefault();
    try {
      const response = await fetch(`${API_BASE_URL}/auth/login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          email: loginData.username,
          password: loginData.password
        }),
      });
      const data = await response.json();
      if (response.ok) {
        setIsAuthenticated(true);
        setCurrentUser(data.user);
        setUserType(data.user.user_type);
        setLoginData({ username: '', password: '' });
      } else {
        alert(data.message || 'Erro ao fazer login. Credenciais inválidas.');
      }
    } catch (error) {
      console.error('Erro de rede ou servidor:', error);
      alert('Erro de conexão. Tente novamente mais tarde.');
    }
  };

  // Função de logout
  const handleLogout = () => {
    setIsAuthenticated(false);
    setCurrentUser(null);
    setUserType('admin');
    setLoginData({ username: '', password: '' });
  };

  // Função para criar usuário
  const handleCreateUser = async (e) => {
    e.preventDefault();
    try {
      const response = await fetch(`${API_BASE_URL}/auth/register`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(newUserData),
      });
      const data = await response.json();
      if (response.ok) {
        setUsers([...users, data.user]);
        setNewUserData({
          name: '',
          email: '',
          user_type: 'embaixadora',
          password: ''
        });
        setShowCreateUserForm(false);
        alert('Usuário criado com sucesso!');
      } else {
        alert(data.message || 'Erro ao criar usuário.');
      }
    } catch (error) {
      console.error('Erro de rede ou servidor:', error);
      alert('Erro de conexão. Tente novamente mais tarde.');
    }
  };

  // Função para criar indicação
  const handleSubmitIndication = (e) => {
    e.preventDefault();
    setFormData({
      client_name: '',
      client_contact: '',
      niche: '',
      observations: ''
    });
    setShowNewIndicationForm(false);
    alert('Indicação criada com sucesso!');
  };

  // Função para trocar usuário (simulação)
  const switchUser = (user) => {
    setCurrentUser(user);
    setUserType(user.user_type);
  };

  const handleUpdateIndicationStatus = async (indicationId, newStatus) => {
    try {
      const response = await fetch(`${API_BASE_URL}/indications/${indicationId}/status`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        },
        body: JSON.stringify({ status: newStatus })
      });
      const data = await response.json();
      if (response.ok) {
        // Atualizar o estado local das indicações (simulado)
        const updatedIndications = indications.map(ind =>
          ind.id === indicationId ? { ...ind, status: newStatus } : ind
        );
        // Note: 'indications' é um array mockado, em um app real você atualizaria o estado com setIndications
        console.log('Indicação atualizada:', updatedIndications);
        alert('Status da indicação atualizado com sucesso!');
      } else {
        alert(data.message || 'Erro ao atualizar status da indicação.');
      }
    } catch (error) {
      console.error('Erro de rede ou servidor:', error);
      alert('Erro de conexão. Tente novamente mais tarde.');
    }
  };

  const handleUpdateUserStatus = async (userId, newStatus) => {
    try {
      const response = await fetch(`${API_BASE_URL}/users/${userId}/status`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        },
        body: JSON.stringify({ status: newStatus })
      });
      const data = await response.json();
      if (response.ok) {
        const updatedUsers = users.map(user =>
          user.id === userId ? { ...user, status: newStatus } : user
        );
        setUsers(updatedUsers);
        alert('Status do usuário atualizado com sucesso!');
      } else {
        alert(data.message || 'Erro ao atualizar status do usuário.');
      }
    } catch (error) {
      console.error('Erro de rede ou servidor:', error);
      alert('Erro de conexão. Tente novamente mais tarde.');
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

  // Tela de Login
  if (!isAuthenticated) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-yellow-50 to-orange-100 flex items-center justify-center p-4">
        <Card className="w-full max-w-md shadow-2xl">
          <CardHeader className="text-center space-y-4">
            <div className="mx-auto w-16 h-16 bg-yellow-400 rounded-full flex items-center justify-center">
              <BarChart3 className="w-8 h-8 text-gray-900" />
            </div>
            <div>
              <CardTitle className="text-2xl font-bold text-gray-900">Beepy</CardTitle>
              <CardDescription className="text-gray-600">
                Sistema de Indicações e Comissões
              </CardDescription>
            </div>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleLogin} className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="username">Usuário</Label>
                <Input
                  id="username"
                  type="text"
                  value={loginData.username}
                  onChange={(e) => setLoginData({ ...loginData, username: e.target.value })}
                  placeholder="Digite seu usuário"
                  required
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="password">Senha</Label>
                <div className="relative">
                  <Input
                    id="password"
                    type={showPassword ? "text" : "password"}
                    value={loginData.password}
                    onChange={(e) => setLoginData({ ...loginData, password: e.target.value })}
                    placeholder="Digite sua senha"
                    required
                  />
                  <Button
                    type="button"
                    variant="ghost"
                    size="sm"
                    className="absolute right-0 top-0 h-full px-3 py-2 hover:bg-transparent"
                    onClick={() => setShowPassword(!showPassword)}
                  >
                    {showPassword ? (
                      <EyeOff className="h-4 w-4 text-gray-400" />
                    ) : (
                      <Eye className="h-4 w-4 text-gray-400" />
                    )}
                  </Button>
                </div>
              </div>

              <Button
                type="submit"
                className="w-full bg-yellow-400 hover:bg-yellow-500 text-gray-900 font-medium"
              >
                <Lock className="w-4 h-4 mr-2" />
                Entrar
              </Button>
            </form>

            <div className="mt-6 p-4 bg-gray-50 rounded-lg">
              <p className="text-sm text-gray-600 text-center">
                <strong>Credenciais de acesso:</strong><br />
                Usuário: admin<br />
                Senha: admin
              </p>
            </div>
          </CardContent>
        </Card>
      </div>
    );
  }

  // Interface principal após login
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
              </div>
            </div>

            <div className="flex items-center space-x-4">
              <div className="flex items-center space-x-2">
                <User className="w-4 h-4 text-gray-500" />
                <span className="text-sm text-gray-700">{currentUser?.name}</span>
                <span className="text-xs bg-gray-100 px-2 py-1 rounded-full text-gray-600">
                  {userType}
                </span>
              </div>

              {userType === 'admin' && (
                <>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => setShowCreateUserForm(true)}
                    className="flex items-center space-x-1"
                  >
                    <UserPlus className="w-4 h-4" />
                    <span>Novo Usuário</span>
                  </Button>

                  <Select value={currentUser?.email} onValueChange={(email) => {
                    const user = users.find(u => u.email === email);
                    if (user) switchUser(user);
                  }}>
                    <SelectTrigger className="w-48">
                      <SelectValue placeholder="Trocar usuário" />
                    </SelectTrigger>
                    <SelectContent>
                      {users.map((user) => (
                        <SelectItem key={user.id} value={user.email}>
                          {user.name} ({user.user_type})
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </>
              )}

              <Button
                variant="outline"
                size="sm"
                onClick={handleLogout}
                className="flex items-center space-x-1 text-red-600 hover:text-red-700"
              >
                <LogOut className="w-4 h-4" />
                <span>Sair</span>
              </Button>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {userType === 'embaixadora' ? renderAmbassadorDashboard() : renderAdminDashboard()}
      </main>

      {/* Modal Nova Indicação */}
      {showNewIndicationForm && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <Card className="w-full max-w-md">
            <CardHeader>
              <CardTitle>Nova Indicação</CardTitle>
              <CardDescription>Preencha os dados do cliente indicado</CardDescription>
            </CardHeader>
            <CardContent>
              <form onSubmit={handleSubmitIndication} className="space-y-4">
                <div className="space-y-2">
                  <Label htmlFor="client_name">Nome do Cliente</Label>
                  <Input
                    id="client_name"
                    value={formData.client_name}
                    onChange={(e) => setFormData({ ...formData, client_name: e.target.value })}
                    placeholder="Digite o nome completo do cliente"
                    required
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="company_name">Nome da Empresa</Label>
                  <Input
                    id="company_name"
                    value={formData.company_name || ''}
                    onChange={(e) => setFormData({ ...formData, company_name: e.target.value })}
                    placeholder="Digite o nome da empresa"
                    required
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="client_email">Email</Label>
                  <Input
                    id="client_email"
                    type="email"
                    value={formData.client_email || ''}
                    onChange={(e) => setFormData({ ...formData, client_email: e.target.value })}
                    placeholder="exemplo@email.com"
                    required
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="client_contact">Telefone</Label>
                  <Input
                    id="client_contact"
                    value={formData.client_contact}
                    onChange={(e) => setFormData({ ...formData, client_contact: e.target.value })}
                    placeholder="(11) 99999-9999"
                    required
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="origin">Origem</Label>
                  <Select value={formData.origin || 'website'} onValueChange={(value) => setFormData({ ...formData, origin: value })}>
                    <SelectTrigger>
                      <SelectValue placeholder="Selecione a origem" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="website">Website</SelectItem>
                      <SelectItem value="whatsapp">WhatsApp</SelectItem>
                      <SelectItem value="social_media">Redes Sociais</SelectItem>
                      <SelectItem value="referral">Indicação</SelectItem>
                      <SelectItem value="event">Evento</SelectItem>
                      <SelectItem value="other">Outro</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="niche">Segmento</Label>
                  <Select value={formData.niche} onValueChange={(value) => setFormData({ ...formData, niche: value })}>
                    <SelectTrigger>
                      <SelectValue placeholder="Selecione o segmento" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="saude">🏥 Saúde</SelectItem>
                      <SelectItem value="educacao_pesquisa">🧠 Educação e Pesquisa</SelectItem>
                      <SelectItem value="juridico">🏛️ Jurídico</SelectItem>
                      <SelectItem value="administracao_negocios">💼 Administração e Negócios</SelectItem>
                      <SelectItem value="engenharias">🏢 Engenharias</SelectItem>
                      <SelectItem value="tecnologia_informacao">💻 Tecnologia da Informação</SelectItem>
                      <SelectItem value="financeiro_bancario">🏦 Financeiro e Bancário</SelectItem>
                      <SelectItem value="marketing_vendas_comunicacao">📣 Marketing, Vendas e Comunicação</SelectItem>
                      <SelectItem value="industria_producao">🏭 Indústria e Produção</SelectItem>
                      <SelectItem value="construcao_civil">🧱 Construção Civil</SelectItem>
                      <SelectItem value="transportes_logistica">🚛 Transportes e Logística</SelectItem>
                      <SelectItem value="comercio_varejo">🛒 Comércio e Varejo</SelectItem>
                      <SelectItem value="turismo_hotelaria_eventos">🏨 Turismo, Hotelaria e Eventos</SelectItem>
                      <SelectItem value="gastronomia_alimentacao">🍳 Gastronomia e Alimentação</SelectItem>
                      <SelectItem value="agronegocio_meio_ambiente">🌱 Agronegócio e Meio Ambiente</SelectItem>
                      <SelectItem value="artes_cultura_design">🎭 Artes, Cultura e Design</SelectItem>
                      <SelectItem value="midias_digitais_criativas">📱 Mídias Digitais e Criativas</SelectItem>
                      <SelectItem value="seguranca_defesa">👮 Segurança e Defesa</SelectItem>
                      <SelectItem value="servicos_gerais">🧹 Serviços Gerais</SelectItem>
                      <SelectItem value="outro">Outro</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                {formData.niche === 'outro' && (
                  <div className="space-y-2">
                    <Label htmlFor="custom_segment">Especifique o Segmento</Label>
                    <Input
                      id="custom_segment"
                      value={formData.custom_segment || ''}
                      onChange={(e) => setFormData({ ...formData, custom_segment: e.target.value })}
                      placeholder="Digite o segmento específico"
                      required
                    />
                  </div>
                )}

                <div className="space-y-2">
                  <Label htmlFor="observations">Observações</Label>
                  <Textarea
                    id="observations"
                    value={formData.observations}
                    onChange={(e) => setFormData({ ...formData, observations: e.target.value })}
                    placeholder="Informações adicionais sobre o cliente"
                  />
                </div>

                <div className="flex space-x-2">
                  <Button
                    type="button"
                    variant="outline"
                    onClick={() => setShowNewIndicationForm(false)}
                    className="flex-1"
                  >
                    Cancelar
                  </Button>
                  <Button
                    type="submit"
                    className="flex-1 bg-yellow-400 hover:bg-yellow-500 text-gray-900"
                  >
                    Criar Indicação
                  </Button>
                </div>
              </form>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Modal Criar Usuário */}
      {showCreateUserForm && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <Card className="w-full max-w-md">
            <CardHeader>
              <CardTitle>Criar Novo Usuário</CardTitle>
              <CardDescription>Cadastre uma nova embaixadora no sistema</CardDescription>
            </CardHeader>
            <CardContent>
              <form onSubmit={handleCreateUser} className="space-y-4">
                <div className="space-y-2">
                  <Label htmlFor="new_name">Nome Completo</Label>
                  <Input
                    id="new_name"
                    value={newUserData.name}
                    onChange={(e) => setNewUserData({ ...newUserData, name: e.target.value })}
                    placeholder="Nome completo da embaixadora"
                    required
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="new_email">Email</Label>
                  <Input
                    id="new_email"
                    type="email"
                    value={newUserData.email}
                    onChange={(e) => setNewUserData({ ...newUserData, email: e.target.value })}
                    placeholder="email@exemplo.com"
                    required
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="new_user_type">Tipo de Usuário</Label>
                  <Select
                    value={newUserData.user_type}
                    onValueChange={(value) => setNewUserData({ ...newUserData, user_type: value })}
                  >
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="embaixadora">Embaixadora</SelectItem>
                      <SelectItem value="admin">Administrador</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="new_password">Senha</Label>
                  <Input
                    id="new_password"
                    type="password"
                    value={newUserData.password}
                    onChange={(e) => setNewUserData({ ...newUserData, password: e.target.value })}
                    placeholder="Senha para acesso"
                    required
                  />
                </div>

                <div className="flex space-x-2">
                  <Button
                    type="button"
                    variant="outline"
                    onClick={() => setShowCreateUserForm(false)}
                    className="flex-1"
                  >
                    Cancelar
                  </Button>
                  <Button
                    type="submit"
                    className="flex-1 bg-green-600 hover:bg-green-700 text-white"
                  >
                    <UserPlus className="w-4 h-4 mr-2" />
                    Criar Usuário
                  </Button>
                </div>
              </form>
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  );

  // Função para renderizar dashboard da embaixadora
  function renderAmbassadorDashboard() {
    return (
      <div className="space-y-6">
        {/* Header */}
        <div className="flex justify-between items-center">
          <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
          <Button
            onClick={() => setShowNewIndicationForm(true)}
            className="bg-yellow-400 hover:bg-yellow-500 text-gray-900"
          >
            <Plus className="w-4 h-4 mr-2" />
            Nova Indicação
          </Button>
        </div>

        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Total de Indicações</CardTitle>
              <Users className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{ambassadorData.stats.total_indications}</div>
              <p className="text-xs text-muted-foreground">
                +{ambassadorData.stats.conversion_rate}% de conversão
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Total de Vendas</CardTitle>
              <TrendingUp className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{ambassadorData.stats.approved_sales}</div>
              <p className="text-xs text-muted-foreground">
                +13% acima da média
              </p>
            </CardContent>
          </Card>

          <Card className="bg-yellow-400">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-black">Comissão do Mês</CardTitle>
              <DollarSign className="h-4 w-4 text-black" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-black">
                R$ {ambassadorData.stats.current_month_commission.toFixed(2)}
              </div>
              <p className="text-xs text-black">
                Total a receber em julho/2025
              </p>
            </CardContent>
          </Card>
        </div>

        {/* Charts */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Comissões por mês */}
          <Card>
            <CardHeader>
              <CardTitle>Suas comissões mês a mês</CardTitle>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={300}>
                <LineChart data={ambassadorData.monthly_commissions}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="month" />
                  <YAxis />
                  <Tooltip formatter={(value) => [`R$ ${value}`, 'Comissão']} />
                  <Line type="monotone" dataKey="total" stroke="#f59e0b" strokeWidth={2} />
                </LineChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>

          {/* Indicações por segmento */}
          <Card>
            <CardHeader>
              <CardTitle>Indicações por segmento do cliente</CardTitle>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={300}>
                <PieChart>
                  <Pie
                    data={ambassadorData.niche_stats}
                    cx="50%"
                    cy="50%"
                    labelLine={false}
                    label={({ niche, percent }) => `${niche} ${(percent * 100).toFixed(0)}%`}
                    outerRadius={80}
                    fill="#8884d8"
                    dataKey="count"
                  >
                    {ambassadorData.niche_stats.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </div>

        {/* Histórico de Indicações */}
        <Card>
          <CardHeader>
            <CardTitle>Histórico de indicação</CardTitle>
            <CardDescription>Suas indicações mais recentes</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {indications.map((indication) => (
                <div key={indication.id} className="flex items-center justify-between p-4 border rounded-lg">
                  <div className="flex-1">
                    <h3 className="font-medium">{indication.client_name}</h3>
                    <p className="text-sm text-gray-500">{indication.client_contact}</p>
                    <p className="text-xs text-gray-400">
                      {new Date(indication.created_at).toLocaleDateString('pt-BR')}
                    </p>
                  </div>
                  <div className="text-right">
                    <Badge className={getStatusColor(indication.status)}>
                      {indication.status}
                    </Badge>
                    <p className="text-sm text-gray-500 mt-1">{indication.niche}</p>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>
    );
  }

  // Função para renderizar dashboard do admin
  function renderAdminDashboard() {
    return (
      <div className="space-y-6">
        {/* Header */}
        <div className="flex justify-between items-center">
          <h1 className="text-3xl font-bold text-gray-900">Dashboard - Visão da Agência</h1>
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
                R$ {adminData.stats.commissions_to_pay.toFixed(2)}
              </div>
            </CardContent>
          </Card>

          <Card className="bg-yellow-400">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-gray-900">Taxa de Conversão das Indicações</CardTitle>
              <TrendingUp className="h-4 w-4 text-gray-900" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-gray-900">
                {adminData.stats.conversion_rate}%
              </div>
            </CardContent>
          </Card>

          <Card className="bg-red-400">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-white">Total de Indicações</CardTitle>
              <TrendingUp className="h-4 w-4 text-white" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-white">{adminData.stats.total_indications}</div>
            </CardContent>
          </Card>

          <Card className="bg-purple-400">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-white">Embaixadoras Ativas</CardTitle>
              <Users className="h-4 w-4 text-white" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-white">{adminData.stats.total_ambassadors}</div>
            </CardContent>
          </Card>
        </div>

        {/* Gestão de Usuários */}
        <Card>
          <CardHeader>
            <CardTitle>Usuários do Sistema</CardTitle>
            <CardDescription>Lista de todos os usuários cadastrados</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {users.map((user) => (
                <div key={user.id} className="flex items-center justify-between p-4 border rounded-lg">
                  <div className="flex-1">
                    <h3 className="font-medium">{user.name}</h3>
                    <p className="text-sm text-gray-500">{user.email}</p>
                  </div>
                  <div className="flex items-center space-x-2">
                    <Badge className={user.user_type === 'admin' ? 'bg-blue-100 text-blue-800' : 'bg-green-100 text-green-800'}>
                      {user.user_type}
                    </Badge>
                    {user.user_type !== 'admin' && (
                      <Select value={user.status} onValueChange={(value) => handleUpdateUserStatus(user.id, value)}>
                        <SelectTrigger className="w-32">
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="ativo">Ativo</SelectItem>
                          <SelectItem value="inativo">Inativo</SelectItem>
                        </SelectContent>
                      </Select>
                    )}
                    {user.user_type !== 'admin' && (
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => switchUser(user)}
                      >
                        Visualizar como
                      </Button>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Charts */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Indicações mês a mês */}
          <Card>
            <CardHeader>
              <CardTitle>Indicações mês a mês</CardTitle>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={adminData.monthly_indications}>
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
                <LineChart data={adminData.monthly_sales}>
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
                    data={adminData.niche_conversion}
                    cx="50%"
                    cy="50%"
                    labelLine={false}
                    label={({ niche, conversion_rate }) => `${niche} ${conversion_rate}%`}
                    outerRadius={80}
                    fill="#8884d8"
                    dataKey="total"
                  >
                    {adminData.niche_conversion.map((entry, index) => (
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
                <BarChart data={adminData.top_ambassadors} layout="horizontal">
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
              {indications.map((indication) => (
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
                    <Select value={indication.status} onValueChange={(value) => handleUpdateIndicationStatus(indication.id, value)}>
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
              {commissions.map((commission) => (
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
                        className="bg-green-600 hover:bg-green-700"
                      >
                        Marcar como Pago
                      </Button>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>
    );
  }
};

export default AuthenticatedApp;



