import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, LineChart, Line, PieChart, Pie, Cell, Area, AreaChart } from 'recharts';
import { TrendingUp, DollarSign, Calendar, Download, Filter } from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';

const CommissionReports = () => {
  const { API_BASE_URL } = useAuth();
  const [reportData, setReportData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [filters, setFilters] = useState({
    period: '12months',
    ambassador: '',
    status: ''
  });

  useEffect(() => {
    fetchReportData();
  }, [filters]);

  const fetchReportData = async () => {
    try {
      const params = new URLSearchParams();
      if (filters.period) params.append('period', filters.period);
      if (filters.ambassador) params.append('ambassador', filters.ambassador);
      if (filters.status) params.append('status', filters.status);

      const response = await fetch(`${API_BASE_URL}/commissions/reports?${params}`, {
        credentials: 'include'
      });
      
      if (response.ok) {
        const data = await response.json();
        setReportData(data);
      }
    } catch (error) {
      console.error('Erro ao buscar dados do relatório:', error);
    } finally {
      setLoading(false);
    }
  };

  const formatCurrency = (value) => {
    return new Intl.NumberFormat('pt-BR', {
      style: 'currency',
      currency: 'BRL'
    }).format(value);
  };

  const COLORS = ['#10b981', '#f59e0b', '#ef4444', '#3b82f6'];

  // Dados mockados para demonstração
  const mockData = {
    summary: {
      totalCommissions: 45600,
      paidCommissions: 32400,
      pendingCommissions: 10800,
      overdueCommissions: 2400,
      totalParcels: 152,
      paidParcels: 108,
      pendingParcels: 36,
      overdueParcels: 8
    },
    monthlyTrend: [
      { month: 'Jan', total: 2700, paid: 2700, pending: 0, overdue: 0 },
      { month: 'Fev', total: 5400, paid: 3600, pending: 1800, overdue: 0 },
      { month: 'Mar', total: 8100, paid: 5400, pending: 2700, overdue: 0 },
      { month: 'Abr', total: 10800, paid: 7200, pending: 3600, overdue: 0 },
      { month: 'Mai', total: 13500, paid: 9000, pending: 4500, overdue: 0 },
      { month: 'Jun', total: 16200, paid: 10800, pending: 5400, overdue: 0 },
      { month: 'Jul', total: 18900, paid: 12600, pending: 6300, overdue: 0 },
      { month: 'Ago', total: 21600, paid: 14400, pending: 5400, overdue: 1800 },
      { month: 'Set', total: 24300, paid: 16200, pending: 5400, overdue: 2700 },
      { month: 'Out', total: 27000, paid: 18000, pending: 6300, overdue: 2700 },
      { month: 'Nov', total: 29700, paid: 19800, pending: 7200, overdue: 2700 },
      { month: 'Dez', total: 32400, paid: 21600, pending: 8100, overdue: 2700 }
    ],
    statusDistribution: [
      { name: 'Pagas', value: 108, amount: 32400, color: '#10b981' },
      { name: 'Pendentes', value: 36, amount: 10800, color: '#f59e0b' },
      { name: 'Em Atraso', value: 8, amount: 2400, color: '#ef4444' }
    ],
    ambassadorPerformance: [
      { name: 'Mariana Lopes', total: 15300, paid: 10800, pending: 3600, overdue: 900 },
      { name: 'Julia Santos', total: 12600, paid: 9000, pending: 2700, overdue: 900 },
      { name: 'Ana Costa', total: 10800, paid: 7200, pending: 2700, overdue: 900 },
      { name: 'Carla Silva', total: 9000, paid: 6300, pending: 1800, overdue: 900 },
      { name: 'Beatriz Lima', total: 7200, paid: 5400, pending: 1800, overdue: 0 }
    ],
    parcelDistribution: [
      { parcel: 'Parcela 1', count: 51, amount: 15300 },
      { parcel: 'Parcela 2', count: 50, amount: 15000 },
      { parcel: 'Parcela 3', count: 51, amount: 15300 }
    ]
  };

  if (loading) {
    return <div className="flex justify-center items-center h-64">Carregando relatórios...</div>;
  }

  const data = reportData || mockData;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold text-gray-900">Relatórios de Comissões</h1>
        <div className="flex space-x-2">
          <Button variant="outline" className="flex items-center space-x-2">
            <Download className="w-4 h-4" />
            <span>Exportar PDF</span>
          </Button>
          <Button variant="outline" className="flex items-center space-x-2">
            <Download className="w-4 h-4" />
            <span>Exportar Excel</span>
          </Button>
        </div>
      </div>

      {/* Filtros */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <Filter className="w-5 h-5" />
            <span>Filtros do Relatório</span>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label className="block text-sm font-medium mb-1">Período</label>
              <Select
                value={filters.period}
                onValueChange={(value) => setFilters({...filters, period: value})}
              >
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="3months">Últimos 3 meses</SelectItem>
                  <SelectItem value="6months">Últimos 6 meses</SelectItem>
                  <SelectItem value="12months">Últimos 12 meses</SelectItem>
                  <SelectItem value="all">Todos os períodos</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div>
              <label className="block text-sm font-medium mb-1">Embaixadora</label>
              <Select
                value={filters.ambassador}
                onValueChange={(value) => setFilters({...filters, ambassador: value})}
              >
                <SelectTrigger>
                  <SelectValue placeholder="Todas as embaixadoras" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="">Todas</SelectItem>
                  <SelectItem value="mariana">Mariana Lopes</SelectItem>
                  <SelectItem value="julia">Julia Santos</SelectItem>
                  <SelectItem value="ana">Ana Costa</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div>
              <label className="block text-sm font-medium mb-1">Status</label>
              <Select
                value={filters.status}
                onValueChange={(value) => setFilters({...filters, status: value})}
              >
                <SelectTrigger>
                  <SelectValue placeholder="Todos os status" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="">Todos</SelectItem>
                  <SelectItem value="pago">Pagas</SelectItem>
                  <SelectItem value="pendente">Pendentes</SelectItem>
                  <SelectItem value="atrasado">Em Atraso</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Resumo Executivo */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total de Comissões</CardTitle>
            <DollarSign className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{formatCurrency(data.summary.totalCommissions)}</div>
            <p className="text-xs text-muted-foreground">
              {data.summary.totalParcels} parcelas
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Comissões Pagas</CardTitle>
            <TrendingUp className="h-4 w-4 text-green-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-green-600">{formatCurrency(data.summary.paidCommissions)}</div>
            <p className="text-xs text-muted-foreground">
              {data.summary.paidParcels} parcelas ({((data.summary.paidParcels / data.summary.totalParcels) * 100).toFixed(1)}%)
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Pendentes</CardTitle>
            <Calendar className="h-4 w-4 text-yellow-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-yellow-600">{formatCurrency(data.summary.pendingCommissions)}</div>
            <p className="text-xs text-muted-foreground">
              {data.summary.pendingParcels} parcelas
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Em Atraso</CardTitle>
            <TrendingUp className="h-4 w-4 text-red-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-red-600">{formatCurrency(data.summary.overdueCommissions)}</div>
            <p className="text-xs text-muted-foreground">
              {data.summary.overdueParcels} parcelas
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Gráficos */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Evolução Mensal */}
        <Card>
          <CardHeader>
            <CardTitle>Evolução Mensal de Comissões</CardTitle>
            <CardDescription>Acompanhe o crescimento das comissões ao longo do tempo</CardDescription>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <AreaChart data={data.monthlyTrend}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="month" />
                <YAxis tickFormatter={(value) => formatCurrency(value)} />
                <Tooltip formatter={(value) => formatCurrency(value)} />
                <Area type="monotone" dataKey="total" stackId="1" stroke="#3b82f6" fill="#3b82f6" fillOpacity={0.6} />
                <Area type="monotone" dataKey="paid" stackId="2" stroke="#10b981" fill="#10b981" fillOpacity={0.8} />
              </AreaChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        {/* Distribuição por Status */}
        <Card>
          <CardHeader>
            <CardTitle>Distribuição por Status</CardTitle>
            <CardDescription>Proporção de comissões por status de pagamento</CardDescription>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={data.statusDistribution}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ name, value }) => `${name}: ${value}`}
                  outerRadius={80}
                  fill="#8884d8"
                  dataKey="value"
                >
                  {data.statusDistribution.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip formatter={(value, name) => [value, 'Parcelas']} />
              </PieChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        {/* Performance por Embaixadora */}
        <Card>
          <CardHeader>
            <CardTitle>Performance por Embaixadora</CardTitle>
            <CardDescription>Comissões totais por embaixadora</CardDescription>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={data.ambassadorPerformance} layout="horizontal">
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis type="number" tickFormatter={(value) => formatCurrency(value)} />
                <YAxis dataKey="name" type="category" width={100} />
                <Tooltip formatter={(value) => formatCurrency(value)} />
                <Bar dataKey="paid" fill="#10b981" name="Pagas" />
                <Bar dataKey="pending" fill="#f59e0b" name="Pendentes" />
                <Bar dataKey="overdue" fill="#ef4444" name="Atrasadas" />
              </BarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        {/* Distribuição por Parcela */}
        <Card>
          <CardHeader>
            <CardTitle>Distribuição por Parcela</CardTitle>
            <CardDescription>Quantidade e valor por número de parcela</CardDescription>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={data.parcelDistribution}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="parcel" />
                <YAxis yAxisId="left" orientation="left" />
                <YAxis yAxisId="right" orientation="right" tickFormatter={(value) => formatCurrency(value)} />
                <Tooltip />
                <Bar yAxisId="left" dataKey="count" fill="#3b82f6" name="Quantidade" />
                <Bar yAxisId="right" dataKey="amount" fill="#f59e0b" name="Valor Total" />
              </BarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default CommissionReports;

