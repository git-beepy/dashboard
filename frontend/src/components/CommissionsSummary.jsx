import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Calendar, DollarSign, Clock, CheckCircle, AlertTriangle } from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';

const CommissionsSummary = () => {
  const { user, API_BASE_URL } = useAuth();
  const [commissions, setCommissions] = useState([]);
  const [summary, setSummary] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchCommissions();
    fetchSummary();
  }, []);

  const fetchCommissions = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/commissions`, {
        credentials: 'include'
      });
      if (response.ok) {
        const data = await response.json();
        setCommissions(data.commissions || []);
      }
    } catch (error) {
      console.error('Erro ao buscar comissões:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchSummary = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/commissions/summary`, {
        credentials: 'include'
      });
      if (response.ok) {
        const data = await response.json();
        setSummary(data.summary);
      }
    } catch (error) {
      console.error('Erro ao buscar resumo:', error);
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'pago':
        return 'bg-green-100 text-green-800';
      case 'atrasado':
        return 'bg-red-100 text-red-800';
      case 'pendente':
        return 'bg-yellow-100 text-yellow-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'pago':
        return <CheckCircle className="w-4 h-4 text-green-600" />;
      case 'atrasado':
        return <AlertTriangle className="w-4 h-4 text-red-600" />;
      case 'pendente':
        return <Clock className="w-4 h-4 text-yellow-600" />;
      default:
        return <Clock className="w-4 h-4 text-gray-600" />;
    }
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

  const getNextPayments = () => {
    const today = new Date();
    const nextMonth = new Date(today.getFullYear(), today.getMonth() + 1, 1);
    const followingMonth = new Date(today.getFullYear(), today.getMonth() + 2, 1);
    
    return commissions
      .filter(c => c.status === 'pendente')
      .sort((a, b) => new Date(a.dueDate) - new Date(b.dueDate))
      .slice(0, 3);
  };

  if (loading) {
    return <div className="flex justify-center items-center h-32">Carregando...</div>;
  }

  return (
    <div className="space-y-6">
      {/* Resumo Financeiro */}
      {summary && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Total Esperado</CardTitle>
              <DollarSign className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{formatCurrency(summary.total_amount)}</div>
              <p className="text-xs text-muted-foreground">
                {summary.total_commissions} parcelas
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Já Recebido</CardTitle>
              <CheckCircle className="h-4 w-4 text-green-600" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-green-600">{formatCurrency(summary.paid_amount)}</div>
              <p className="text-xs text-muted-foreground">
                {summary.paid_commissions} parcelas pagas
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">A Receber</CardTitle>
              <Clock className="h-4 w-4 text-yellow-600" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-yellow-600">
                {formatCurrency(summary.pending_amount + summary.overdue_amount)}
              </div>
              <p className="text-xs text-muted-foreground">
                {summary.pending_commissions + summary.overdue_commissions} parcelas pendentes
              </p>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Próximos Pagamentos */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <Calendar className="w-5 h-5" />
            <span>Próximos Pagamentos</span>
          </CardTitle>
          <CardDescription>
            Suas próximas comissões a receber
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {getNextPayments().length > 0 ? (
              getNextPayments().map((commission) => (
                <div key={commission.id} className="flex items-center justify-between p-3 border rounded-lg">
                  <div className="flex items-center space-x-3">
                    {getStatusIcon(commission.status)}
                    <div>
                      <p className="font-medium">{commission.clientName}</p>
                      <p className="text-sm text-gray-500">
                        Parcela {commission.parcelNumber}/3
                      </p>
                    </div>
                  </div>
                  <div className="text-right">
                    <p className="font-medium">{formatCurrency(commission.value)}</p>
                    <p className="text-sm text-gray-500">
                      {formatDate(commission.dueDate)}
                    </p>
                  </div>
                </div>
              ))
            ) : (
              <div className="text-center py-6 text-gray-500">
                Nenhum pagamento pendente encontrado.
              </div>
            )}
          </div>
        </CardContent>
      </Card>

      {/* Histórico Completo */}
      <Card>
        <CardHeader>
          <CardTitle>Histórico de Comissões</CardTitle>
          <CardDescription>
            Todas as suas comissões e status de pagamento
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {commissions.length > 0 ? (
              commissions.map((commission) => (
                <div key={commission.id} className="flex items-center justify-between p-3 border rounded-lg hover:bg-gray-50">
                  <div className="flex items-center space-x-3">
                    {getStatusIcon(commission.status)}
                    <div>
                      <p className="font-medium">{commission.clientName}</p>
                      <p className="text-sm text-gray-500">
                        Parcela {commission.parcelNumber}/3 • Vencimento: {formatDate(commission.dueDate)}
                      </p>
                      {commission.paymentDate && (
                        <p className="text-xs text-green-600">
                          Pago em: {formatDate(commission.paymentDate)}
                        </p>
                      )}
                    </div>
                  </div>
                  <div className="text-right">
                    <p className="font-medium text-lg">{formatCurrency(commission.value)}</p>
                    <Badge className={getStatusColor(commission.status)}>
                      {commission.status}
                    </Badge>
                  </div>
                </div>
              ))
            ) : (
              <div className="text-center py-8 text-gray-500">
                <DollarSign className="w-12 h-12 mx-auto mb-4 text-gray-300" />
                <p>Você ainda não possui comissões geradas.</p>
                <p className="text-sm mt-1">
                  Comissões são geradas automaticamente quando suas indicações são aprovadas.
                </p>
              </div>
            )}
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default CommissionsSummary;

