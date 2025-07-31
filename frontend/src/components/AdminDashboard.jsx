import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Badge } from './ui/badge';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, LineChart, Line } from 'recharts';
import { DollarSign, Users, TrendingUp, AlertTriangle, CheckCircle, Clock, XCircle } from 'lucide-react';
import axios from 'axios';

const AdminDashboard = () => {
  const { user, token, API_BASE_URL } = useAuth();
  const [dashboardData, setDashboardData] = useState(null);
  const [indications, setIndications] = useState([]);
  const [installments, setInstallments] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (user?.role === 'admin') {
      fetchDashboardData();
      fetchIndications();
      fetchInstallments();
    }
  }, [user, token]);

  const fetchDashboardData = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/dashboard/admin`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        withCredentials: true
      });

      if (response.status === 200) {
        setDashboardData(response.data);
      }
    } catch (error) {
      console.error('Erro ao buscar dados do dashboard:', error);
    }
  };

  const fetchIndications = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/indications`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        withCredentials: true
      });

      if (response.status === 200) {
        setIndications(response.data);
      }
    } catch (error) {
      console.error('Erro ao buscar indicações:', error);
    }
  };

  const fetchInstallments = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/installments`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        withCredentials: true
      });

      if (response.status === 200) {
        setInstallments(response.data);
        setLoading(false);
      }
    } catch (error) {
      console.error('Erro ao buscar parcelas:', error);
      setLoading(false);
    }
  };

  const updateIndicationStatus = async (indicationId, newStatus) => {
    try {
      await axios.put(
        `${API_BASE_URL}/indications/${indicationId}/status`,
        { status: newStatus },
        {
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          },
          withCredentials: true
        }
      );

      // Recarregar dados
      fetchIndications();
      fetchInstallments();
      fetchDashboardData();
    } catch (error) {
      console.error('Erro ao atualizar status:', error);
    }
  };

  const markInstallmentAsPaid = async (installmentId) => {
    try {
      await axios.put(
        `${API_BASE_URL}/installments/${installmentId}/pay`,
        {},
        {
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          },
          withCredentials: true
        }
      );

      // Recarregar dados
      fetchInstallments();
      fetchDashboardData();
    } catch (error) {
      console.error('Erro ao marcar parcela como paga:', error);
    }
  };

  const getStatusBadge = (status) => {
    const statusConfig = {
      'agendado': { color: 'bg-yellow-100 text-yellow-800', icon: Clock },
      'aprovado': { color: 'bg-green-100 text-green-800', icon: CheckCircle },
      'não aprovado': { color: 'bg-red-100 text-red-800', icon: XCircle }
    };

    const config = statusConfig[status] || statusConfig['agendado'];
    const Icon = config.icon;

    return (
      <Badge className={`${config.color} flex items-center gap-1`}>
        <Icon size={12} />
        {status}
      </Badge>
    );
  };

  const getInstallmentStatusBadge = (status) => {
    const statusConfig = {
      'pendente': { color: 'bg-yellow-100 text-yellow-800', icon: Clock },
      'pago': { color: 'bg-green-100 text-green-800', icon: CheckCircle },
      'em_atraso': { color: 'bg-red-100 text-red-800', icon: AlertTriangle }
    };

    const config = statusConfig[status] || statusConfig['pendente'];
    const Icon = config.icon;

    return (
      <Badge className={`${config.color} flex items-center gap-1`}>
        <Icon size={12} />
        {status.replace('_', ' ')}
      </Badge>
    );
  };

  const formatCurrency = (value) => {
    return new Intl.NumberFormat('pt-BR', {
      style: 'currency',
      currency: 'BRL'
    }).format(value);
  };

  const formatDate = (date) => {
    if (!date) return '-';
    const dateObj = typeof date === 'string' ? new Date(date) : date;
    return dateObj.toLocaleDateString('pt-BR');
  };

  // Preparar dados para gráficos
  const prepareChartData = () => {
    const monthlyData = {};
    
    installments.forEach(installment => {
      const dueDate = new Date(installment.dueDate);
      const monthKey = `${dueDate.getFullYear()}-${String(dueDate.getMonth() + 1).padStart(2, '0')}`;
      
      if (!monthlyData[monthKey]) {
        monthlyData[monthKey] = {
          month: monthKey,
          total: 0,
          paid: 0,
          pending: 0,
          overdue: 0
        };
      }
      
      monthlyData[monthKey].total += installment.value;
      
      if (installment.status === 'pago') {
        monthlyData[monthKey].paid += installment.value;
      } else if (installment.status === 'em_atraso') {
        monthlyData[monthKey].overdue += installment.value;
      } else {
        monthlyData[monthKey].pending += installment.value;
      }
    });

    return Object.values(monthlyData).sort((a, b) => a.month.localeCompare(b.month));
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-lg">Carregando...</div>
      </div>
    );
  }

  if (user?.role !== 'admin') {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-lg text-red-600">Acesso negado. Apenas administradores podem acessar esta página.</div>
      </div>
    );
  }

  const chartData = prepareChartData();

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold">Dashboard Administrativo</h1>
      </div>

      {/* Cards de Resumo */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total de Indicações</CardTitle>
            <Users className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{dashboardData?.totalIndications || 0}</div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Valor Total</CardTitle>
            <DollarSign className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{formatCurrency(dashboardData?.totalValue || 0)}</div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Valor Pago</CardTitle>
            <CheckCircle className="h-4 w-4 text-green-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-green-600">{formatCurrency(dashboardData?.paidValue || 0)}</div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Valor Pendente</CardTitle>
            <AlertTriangle className="h-4 w-4 text-yellow-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-yellow-600">{formatCurrency(dashboardData?.pendingValue || 0)}</div>
          </CardContent>
        </Card>
      </div>

      {/* Gráfico de Pagamentos por Mês */}
      <Card>
        <CardHeader>
          <CardTitle>Pagamentos Programados por Mês</CardTitle>
        </CardHeader>
        <CardContent>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={chartData}>
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

      {/* Lista de Indicações */}
      <Card>
        <CardHeader>
          <CardTitle>Todas as Indicações</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {indications.map((indication) => (
              <div key={indication.id} className="border rounded-lg p-4">
                <div className="flex items-center justify-between mb-2">
                  <div>
                    <h3 className="font-semibold">{indication.client_name}</h3>
                    <p className="text-sm text-gray-600">{indication.email}</p>
                  </div>
                  <div className="flex items-center gap-2">
                    {getStatusBadge(indication.status)}
                    {indication.status === 'agendado' && (
                      <div className="flex gap-2">
                        <Button
                          size="sm"
                          onClick={() => updateIndicationStatus(indication.id, 'aprovado')}
                          className="bg-green-600 hover:bg-green-700"
                        >
                          Aprovar
                        </Button>
                        <Button
                          size="sm"
                          variant="destructive"
                          onClick={() => updateIndicationStatus(indication.id, 'não aprovado')}
                        >
                          Reprovar
                        </Button>
                      </div>
                    )}
                  </div>
                </div>

                {/* Parcelas da Indicação */}
                {indication.installments && indication.installments.length > 0 && (
                  <div className="mt-4">
                    <h4 className="font-medium mb-2">Parcelas:</h4>
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-2">
                      {indication.installments.map((installment) => (
                        <div key={installment.id} className="border rounded p-2 text-sm">
                          <div className="flex justify-between items-center mb-1">
                            <span>Parcela {installment.installmentNumber}</span>
                            {getInstallmentStatusBadge(installment.status)}
                          </div>
                          <div className="text-xs text-gray-600">
                            <div>Valor: {formatCurrency(installment.value)}</div>
                            <div>Vencimento: {formatDate(installment.dueDate)}</div>
                            {installment.paidDate && (
                              <div>Pago em: {formatDate(installment.paidDate)}</div>
                            )}
                          </div>
                          {installment.status !== 'pago' && (
                            <Button
                              size="sm"
                              className="mt-2 w-full"
                              onClick={() => markInstallmentAsPaid(installment.id)}
                            >
                              Marcar como Pago
                            </Button>
                          )}
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default AdminDashboard;

