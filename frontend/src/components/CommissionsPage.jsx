import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { CheckCircle, XCircle, Clock, AlertTriangle, Download } from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';

const CommissionsPage = () => {
  const { API_BASE_URL } = useAuth();
  const [commissions, setCommissions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [summary, setSummary] = useState(null);

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

  const markCommissionAsPaid = async (commissionId) => {
    try {
      const response = await fetch(`${API_BASE_URL}/commissions/${commissionId}/pay`, {
        method: 'PUT',
        credentials: 'include',
      });

      if (response.ok) {
        fetchCommissions();
        fetchSummary();
      }
    } catch (error) {
      console.error('Erro ao marcar comissão como paga:', error);
    }
  };

  const markCommissionAsUnpaid = async (commissionId) => {
    try {
      const response = await fetch(`${API_BASE_URL}/commissions/${commissionId}/unpay`, {
        method: 'PUT',
        credentials: 'include',
      });

      if (response.ok) {
        fetchCommissions();
        fetchSummary();
      }
    } catch (error) {
      console.error('Erro ao reverter pagamento:', error);
    }
  };

  const updateOverdueCommissions = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/commissions/update-overdue`, {
        method: 'POST',
        credentials: 'include',
      });

      if (response.ok) {
        fetchCommissions();
        fetchSummary();
      }
    } catch (error) {
      console.error('Erro ao atualizar comissões em atraso:', error);
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
        return <XCircle className="w-4 h-4 text-gray-600" />;
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

  if (loading) {
    return <div className="flex justify-center items-center h-64">Carregando...</div>;
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold text-gray-900">Gestão de Comissões</h1>
        <div className="flex space-x-2">
          <Button
            onClick={updateOverdueCommissions}
            variant="outline"
            className="flex items-center space-x-2"
          >
            <AlertTriangle className="w-4 h-4" />
            <span>Atualizar Atrasos</span>
          </Button>
          <Button
            variant="outline"
            className="flex items-center space-x-2"
          >
            <Download className="w-4 h-4" />
            <span>Exportar</span>
          </Button>
        </div>
      </div>

      {/* Resumo */}
      {summary && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Total de Comissões</CardTitle>
              <CheckCircle className="h-4 w-4 text-muted-foreground" />
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
              <CardTitle className="text-sm font-medium">Pagas</CardTitle>
              <CheckCircle className="h-4 w-4 text-green-600" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-green-600">{formatCurrency(summary.paid_amount)}</div>
              <p className="text-xs text-muted-foreground">
                {summary.paid_commissions} parcelas
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Pendentes</CardTitle>
              <Clock className="h-4 w-4 text-yellow-600" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-yellow-600">{formatCurrency(summary.pending_amount)}</div>
              <p className="text-xs text-muted-foreground">
                {summary.pending_commissions} parcelas
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Em Atraso</CardTitle>
              <AlertTriangle className="h-4 w-4 text-red-600" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-red-600">{formatCurrency(summary.overdue_amount)}</div>
              <p className="text-xs text-muted-foreground">
                {summary.overdue_commissions} parcelas
              </p>
            </CardContent>
          </Card>
        </div>
      )}


    </div>
  );
};

export default CommissionsPage;

