import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { TrendingUp, Users, DollarSign, Target, CheckCircle, AlertTriangle, Clock } from 'lucide-react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, LineChart, Line } from 'recharts';
import { useAuth } from '../contexts/AuthContext';

const AdminPage = () => {
  const { user, API_BASE_URL } = useAuth();
  const [dashboardData, setDashboardData] = useState(null);
  const [indications, setIndications] = useState([]);
  const [commissions, setCommissions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedAmbassador, setSelectedAmbassador] = useState('all');
  const [selectedStatus, setSelectedStatus] = useState('all');

  useEffect(() => {
    fetchDashboardData();
    fetchIndications();
    fetchCommissions();
  }, [selectedAmbassador, selectedStatus]);

  const fetchDashboardData = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`${API_BASE_URL}/admin/dashboard`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });
      
      if (response.ok) {
        const data = await response.json();
        setDashboardData(data.dashboard);
      }
    } catch (error) {
      console.error('Erro ao buscar dados do dashboard:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchIndications = async () => {
    try {
      const token = localStorage.getItem('token');
      let url = `${API_BASE_URL}/admin/indications`;
      
      const params = new URLSearchParams();
      if (selectedAmbassador !== 'all') {
        params.append('ambassador_id', selectedAmbassador);
      }
      if (selectedStatus !== 'all') {
        params.append('status', selectedStatus);
      }
      
      if (params.toString()) {
        url += `?${params.toString()}`;
      }
      
      const response = await fetch(url, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });
      
      if (response.ok) {
        const data = await response.json();
        setIndications(data.indications);
      }
    } catch (error) {
      console.error('Erro ao buscar indicações:', error);
    }
  };

  const fetchCommissions = async () => {
    try {
      const token = localStorage.getItem('token');
      let url = `${API_BASE_URL}/admin/commissions`;
      
      const params = new URLSearchParams();
      if (selectedAmbassador !== 'all') {
        params.append('ambassador_id', selectedAmbassador);
      }
      
      if (params.toString()) {
        url += `?${params.toString()}`;
      }
      
      const response = await fetch(url, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
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
      const token = localStorage.getItem('token');
      const response = await fetch(`${API_BASE_URL}/indications/${indicationId}/status`, {
        method: 'PUT',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ status: newStatus })
      });
      
      if (response.ok) {
        fetchIndications();
        fetchCommissions();
        fetchDashboardData();
      }
    } catch (error) {
      console.error('Erro ao atualizar status da indicação:', error);
    }
  };

  const updateCommissionStatus = async (commissionId, newStatus) => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`${API_BASE_URL}/admin/commissions/${commissionId}/status`, {
        method: 'PUT',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ status: newStatus })
      });
      
      if (response.ok) {
        fetchCommissions();
        fetchDashboardData();
      }
    } catch (error) {
      console.error('Erro ao atualizar status da comissão:', error);
    }
  };

  const getStatusBadge = (status) => {
    const statusConfig = {
      'agendado': { color: 'bg-yellow-100 text-yellow-800', text: 'Agendado' },
      'aprovado': { color: 'bg-green-100 text-green-800', text: 'Aprovado' },
      'não aprovado': { color: 'bg-red-100 text-red-800', text: 'Não Aprovado' },
      'pendente': { color: 'bg-blue-100 text-blue-800', text: 'Pendente' },
      'pago': { color: 'bg-green-100 text-green-800', text: 'Pago' },
      'em atraso': { color: 'bg-red-100 text-red-800', text: 'Em Atraso' }
    };
    
    const config = statusConfig[status] || { color: 'bg-gray-100 text-gray-800', text: status };
    return <Badge className={config.color}>{config.text}</Badge>;
  };

  const formatCurrency = (value) => {
    return new Intl.NumberFormat('pt-BR', {
      style: 'currency',
      currency: 'BRL'
    }).format(value);
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('pt-BR');
  };

  if (loading) {
    return <div className="flex justify-center items-center h-64">Carregando...</div>;
  }

  return (
    <div className="p-6 space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold text-gray-900">Dashboard Admin</h1>
        <div className="flex gap-4">
          <Select value={selectedAmbassador} onValueChange={setSelectedAmbassador}>
            <SelectTrigger className="w-48">
              <SelectValue placeholder="Filtrar por embaixadora" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">Todas as embaixadoras</SelectItem>
              {dashboardData?.ambassadors_stats?.map((ambassador) => (
                <SelectItem key={ambassador.id} value={ambassador.id.toString()}>
                  {ambassador.name}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
          
          <Select value={selectedStatus} onValueChange={setSelectedStatus}>
            <SelectTrigger className="w-48">
              <SelectValue placeholder="Filtrar por status" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">Todos os status</SelectItem>
              <SelectItem value="agendado">Agendado</SelectItem>
              <SelectItem value="aprovado">Aprovado</SelectItem>
              <SelectItem value="não aprovado">Não Aprovado</SelectItem>
            </SelectContent>
          </Select>
        </div>
      </div>

      {/* Cards de Estatísticas Gerais */}
      {dashboardData && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Total de Indicações</CardTitle>
              <Target className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{dashboardData.general_stats.total_indications}</div>
              <p className="text-xs text-muted-foreground">
                {dashboardData.general_stats.approved_indications} aprovadas
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Valor Total a Receber</CardTitle>
              <DollarSign className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                {formatCurrency(dashboardData.financial_stats.total_amount)}
              </div>
              <p className="text-xs text-muted-foreground">
                {dashboardData.general_stats.total_commissions} parcelas
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Valor Já Pago</CardTitle>
              <CheckCircle className="h-4 w-4 text-green-600" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-green-600">
                {formatCurrency(dashboardData.financial_stats.paid_amount)}
              </div>
              <p className="text-xs text-muted-foreground">
                {dashboardData.general_stats.paid_commissions} parcelas pagas
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Valor Pendente</CardTitle>
              <Clock className="h-4 w-4 text-yellow-600" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-yellow-600">
                {formatCurrency(dashboardData.financial_stats.pending_amount + dashboardData.financial_stats.overdue_amount)}
              </div>
              <p className="text-xs text-muted-foreground">
                {dashboardData.general_stats.pending_commissions + dashboardData.general_stats.overdue_commissions} parcelas pendentes
              </p>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Gráfico de Pagamentos por Mês */}
      {dashboardData?.monthly_data && (
        <Card>
          <CardHeader>
            <CardTitle>Pagamentos Programados por Mês</CardTitle>
            <CardDescription>Visualização dos valores por mês</CardDescription>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={dashboardData.monthly_data}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="month" />
                <YAxis />
                <Tooltip formatter={(value) => formatCurrency(value)} />
                <Bar dataKey="paid" fill="#10b981" name="Pago" />
                <Bar dataKey="pending" fill="#f59e0b" name="Pendente" />
                <Bar dataKey="overdue" fill="#ef4444" name="Em Atraso" />
              </BarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      )}

      {/* Lista de Indicações */}
      <Card>
        <CardHeader>
          <CardTitle>Indicações</CardTitle>
          <CardDescription>Gerencie o status das indicações</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {indications.map((indication) => (
              <div key={indication.id} className="flex items-center justify-between p-4 border rounded-lg">
                <div className="flex-1">
                  <h3 className="font-semibold">{indication.client_name}</h3>
                  <p className="text-sm text-gray-600">{indication.email}</p>
                  <p className="text-sm text-gray-500">
                    Embaixadora: {indication.ambassador_name} | 
                    Criado em: {formatDate(indication.created_at)}
                  </p>
                </div>
                <div className="flex items-center gap-4">
                  {getStatusBadge(indication.status)}
                  <div className="flex gap-2">
                    {indication.status !== 'aprovado' && (
                      <Button
                        size="sm"
                        onClick={() => updateIndicationStatus(indication.id, 'aprovado')}
                        className="bg-green-600 hover:bg-green-700"
                      >
                        Aprovar
                      </Button>
                    )}
                    {indication.status !== 'não aprovado' && (
                      <Button
                        size="sm"
                        variant="destructive"
                        onClick={() => updateIndicationStatus(indication.id, 'não aprovado')}
                      >
                        Reprovar
                      </Button>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Lista de Comissões */}
      <Card>
        <CardHeader>
          <CardTitle>Controle de Parcelas</CardTitle>
          <CardDescription>Gerencie o status dos pagamentos</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {commissions.map((commission) => (
              <div key={commission.id} className="flex items-center justify-between p-4 border rounded-lg">
                <div className="flex-1">
                  <h3 className="font-semibold">
                    {commission.client_name} - Parcela {commission.parcel_number}/3
                  </h3>
                  <p className="text-sm text-gray-600">
                    Embaixadora: {commission.ambassador_name}
                  </p>
                  <p className="text-sm text-gray-500">
                    Valor: {formatCurrency(commission.amount)} | 
                    Vencimento: {formatDate(commission.due_date)}
                  </p>
                </div>
                <div className="flex items-center gap-4">
                  {getStatusBadge(commission.payment_status)}
                  <div className="flex gap-2">
                    {commission.payment_status !== 'pago' && (
                      <Button
                        size="sm"
                        onClick={() => updateCommissionStatus(commission.id, 'pago')}
                        className="bg-green-600 hover:bg-green-700"
                      >
                        Marcar como Pago
                      </Button>
                    )}
                    {commission.payment_status === 'pago' && (
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => updateCommissionStatus(commission.id, 'pendente')}
                      >
                        Reverter Pagamento
                      </Button>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default AdminPage;

