import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Badge } from '@/components/ui/badge';
import { Plus, TrendingUp, Users, DollarSign, Calendar } from 'lucide-react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';

const AmbassadorDashboard = () => {
  const [dashboardData, setDashboardData] = useState(null);
  const [indications, setIndications] = useState([]);
  const [showNewIndicationForm, setShowNewIndicationForm] = useState(false);
  const [loading, setLoading] = useState(true);
  const [formData, setFormData] = useState({
    client_name: '',
    client_contact: '',
    niche: '',
    observations: ''
  });

  useEffect(() => {
    fetchDashboardData();
    fetchIndications();
  }, []);

  const fetchDashboardData = async () => {
    try {
      const response = await fetch('/dashboard/ambassador', {
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
      const response = await fetch('/indications', {
        credentials: 'include'
      });
      if (response.ok) {
        const data = await response.json();
        setIndications(data.indications);
      }
    } catch (error) {
      console.error('Erro ao buscar indicações:', error);
    }
  };

  const handleSubmitIndication = async (e) => {
    e.preventDefault();
    try {
      const response = await fetch('/indications', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include',
        body: JSON.stringify(formData),
      });

      if (response.ok) {
        setFormData({
          client_name: '',
          client_contact: '',
          niche: '',
          observations: ''
        });
        setShowNewIndicationForm(false);
        fetchIndications();
        fetchDashboardData();
      }
    } catch (error) {
      console.error('Erro ao criar indicação:', error);
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

  const COLORS = ['#f59e0b', '#10b981', '#3b82f6', '#ef4444'];

  if (loading) {
    return <div className="flex justify-center items-center h-64">Carregando...</div>;
  }

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
            <div className="text-2xl font-bold">{dashboardData?.stats?.total_indications || 0}</div>
            <p className="text-xs text-muted-foreground">
              +{dashboardData?.stats?.conversion_rate?.toFixed(1) || 0}% de conversão
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total de Vendas</CardTitle>
            <TrendingUp className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{dashboardData?.stats?.approved_sales || 0}</div>
            <p className="text-xs text-muted-foreground">
              +13% acima da média
            </p>
          </CardContent>
        </Card>

        <Card className="bg-yellow-400">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-gray-900">Comissão do Mês</CardTitle>
            <DollarSign className="h-4 w-4 text-gray-900" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-gray-900">
              R$ {dashboardData?.stats?.current_month_commission?.toFixed(2) || '0,00'}
            </div>
            <p className="text-xs text-gray-700">
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
              <LineChart data={dashboardData?.monthly_commissions?.slice(0, 12).reverse() || []}>
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
                  data={dashboardData?.niche_stats || []}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ niche, percent }) => `${niche} ${(percent * 100).toFixed(0)}%`}
                  outerRadius={80}
                  fill="#8884d8"
                  dataKey="count"
                >
                  {(dashboardData?.niche_stats || []).map((entry, index) => (
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
                    required
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="client_contact">Contato</Label>
                  <Input
                    id="client_contact"
                    value={formData.client_contact}
                    onChange={(e) => setFormData({ ...formData, client_contact: e.target.value })}
                    placeholder="Telefone ou email"
                    required
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="niche">Nicho</Label>
                  <Select value={formData.niche} onValueChange={(value) => setFormData({ ...formData, niche: value })}>
                    <SelectTrigger>
                      <SelectValue placeholder="Selecione o nicho" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="roupa">Roupa</SelectItem>
                      <SelectItem value="clinicas">Clínicas</SelectItem>
                      <SelectItem value="loja de roupa">Loja de Roupa</SelectItem>
                      <SelectItem value="oticas">Óticas</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

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
    </div>
  );
};

export default AmbassadorDashboard;

