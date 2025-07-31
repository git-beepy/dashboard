import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { TrendingUp, DollarSign, Target, CheckCircle, Clock, AlertTriangle } from 'lucide-react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, LineChart, Line } from 'recharts';
import { useAuth } from '../contexts/AuthContext';

const AmbassadorPage = () => {
  const { user, API_BASE_URL } = useAuth();
  const [dashboardData, setDashboardData] = useState(null);
  const [indications, setIndications] = useState([]);
  const [commissions, setCommissions] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchDashboardData();
    fetchIndications();
    fetchCommissions();
  }, []);

  const fetchDashboardData = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`${API_BASE_URL}/ambassador/dashboard`, {
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
      const response = await fetch(`${API_BASE_URL}/ambassador/indications`, {
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
      const response = await fetch(`${API_BASE_URL}/ambassador/commissions`, {
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

  const getStatusBadge = (status) => {
    const statusConfig = {
      'agendado': { color: 'bg-yellow-100 text-yellow-800', text: 'Agendado', icon: Clock },
      'aprovado': { color: 'bg-green-100 text-green-800', text: 'Aprovado', icon: CheckCircle },
      'não aprovado': { color: 'bg-red-100 text-red-800', text: 'Não Aprovado', icon: AlertTriangle },
      'pendente': { color: 'bg-blue-100 text-blue-800', text: 'Pendente', icon: Clock },
      'pago': { color: 'bg-green-100 text-green-800', text: 'Pago', icon: CheckCircle },
      'em atraso': { color: 'bg-red-100 text-red-800', text: 'Em Atraso', icon: AlertTriangle }
    };
    
    const config = statusConfig[status] || { color: 'bg-gray-100 text-gray-800', text: status, icon: Clock };
    const Icon = config.icon;
    
    return (
      <Badge className={`${config.color} flex items-center gap-1`}>
        <Icon className="h-3 w-3" />
        {config.text}
      </Badge>
    );
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
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Meu Dashboard</h1>
          <p className="text-gray-600">Olá, {user?.name}! Aqui estão suas indicações e comissões.</p>
        </div>
      </div>

      {/* Cards de Estatísticas */}
      {dashboardData && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Total de Indicações</CardTitle>
              <Target className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{dashboardData.indication_stats.total_indications}</div>
              <p className="text-xs text-muted-foreground">
                {dashboardData.indication_stats.approved_indications} aprovadas
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
                {dashboardData.commission_stats.total_commissions} parcelas
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Valor Já Recebido</CardTitle>
              <CheckCircle className="h-4 w-4 text-green-600" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-green-600">
                {formatCurrency(dashboardData.financial_stats.paid_amount)}
              </div>
              <p className="text-xs text-muted-foreground">
                {dashboardData.commission_stats.paid_commissions} parcelas pagas
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
                {dashboardData.commission_stats.pending_commissions + dashboardData.commission_stats.overdue_commissions} parcelas pendentes
              </p>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Gráfico de Pagamentos por Mês */}
      {dashboardData?.monthly_data && dashboardData.monthly_data.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>Meus Pagamentos por Mês</CardTitle>
            <CardDescription>Visualização dos seus valores por mês</CardDescription>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={dashboardData.monthly_data}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="month" />
                <YAxis />
                <Tooltip formatter={(value) => formatCurrency(value)} />
                <Bar dataKey="paid" fill="#10b981" name="Recebido" />
                <Bar dataKey="pending" fill="#f59e0b" name="Pendente" />
                <Bar dataKey="overdue" fill="#ef4444" name="Em Atraso" />
              </BarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      )}

      {/* Lista de Indicações com Parcelas */}
      <Card>
        <CardHeader>
          <CardTitle>Minhas Indicações</CardTitle>
          <CardDescription>Acompanhe o status das suas indicações e parcelas</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-6">
            {indications.map((indication) => (
              <div key={indication.id} className="border rounded-lg p-4">
                <div className="flex items-center justify-between mb-4">
                  <div className="flex-1">
                    <h3 className="font-semibold text-lg">{indication.client_name}</h3>
                    <p className="text-sm text-gray-600">{indication.email} | {indication.phone}</p>
                    <p className="text-sm text-gray-500">
                      Criado em: {formatDate(indication.created_at)}
                    </p>
                  </div>
                  <div className="flex items-center gap-4">
                    {getStatusBadge(indication.status)}
                  </div>
                </div>

                {/* Parcelas da Indicação */}
                {indication.commissions && indication.commissions.length > 0 && (
                  <div className="mt-4">
                    <h4 className="font-medium mb-3 text-gray-700">Parcelas (R$ 300,00 cada):</h4>
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                      {indication.commissions.map((commission) => (
                        <div key={commission.id} className="bg-gray-50 rounded-lg p-3">
                          <div className="flex items-center justify-between mb-2">
                            <span className="font-medium">
                              Parcela {commission.parcel_number}/3
                            </span>
                            {getStatusBadge(commission.payment_status)}
                          </div>
                          <div className="text-sm text-gray-600">
                            <p>Valor: {formatCurrency(commission.amount)}</p>
                            <p>Vencimento: {formatDate(commission.due_date)}</p>
                            {commission.payment_date && (
                              <p className="text-green-600">
                                Pago em: {formatDate(commission.payment_date)}
                              </p>
                            )}
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Indicação sem comissões ainda */}
                {(!indication.commissions || indication.commissions.length === 0) && (
                  <div className="mt-4 p-3 bg-yellow-50 rounded-lg">
                    <p className="text-sm text-yellow-700">
                      {indication.status === 'agendado' && 'Aguardando aprovação para gerar as parcelas.'}
                      {indication.status === 'não aprovado' && 'Indicação não aprovada - sem comissões.'}
                    </p>
                  </div>
                )}
              </div>
            ))}

            {indications.length === 0 && (
              <div className="text-center py-8 text-gray-500">
                <Target className="h-12 w-12 mx-auto mb-4 text-gray-300" />
                <p>Você ainda não possui indicações.</p>
              </div>
            )}
          </div>
        </CardContent>
      </Card>

      {/* Resumo das Parcelas */}
      {commissions.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>Resumo das Parcelas</CardTitle>
            <CardDescription>Todas as suas parcelas em ordem de vencimento</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {commissions.map((commission) => (
                <div key={commission.id} className="flex items-center justify-between p-3 border rounded-lg">
                  <div className="flex-1">
                    <h4 className="font-medium">
                      {commission.client_name} - Parcela {commission.parcel_number}/3
                    </h4>
                    <p className="text-sm text-gray-600">
                      Vencimento: {formatDate(commission.due_date)}
                    </p>
                  </div>
                  <div className="flex items-center gap-4">
                    <span className="font-semibold">{formatCurrency(commission.amount)}</span>
                    {getStatusBadge(commission.payment_status)}
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
};

export default AmbassadorPage;

