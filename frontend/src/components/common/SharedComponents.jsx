import React, { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from ../ui/card';
import { Button } from ../ui/button';
import { Input } from ../ui/input';
import { Label } from ../ui/label';
import { Select, SelectItem } from ../ui/select'; // Removido SelectContent, SelectTrigger, SelectValue
import { Badge } from ../ui/badge';
import { Plus, Edit, Trash2, Eye, DollarSign, TrendingUp, Users, Calendar } from 'lucide-react';
import { useFirestoreCRUD } from '../../hooks/useFirestoreRealtime';
import { useRealtime } from '../../contexts/RealtimeContext';
import { getSegmentDisplayName, getSegmentOptions } from '../../constants/segments';
import { getOriginDisplayName, getOriginOptions } from '../../constants/origins';

// Funções utilitárias para cores e status
const getStatusColor = (status) => {
  switch (status) {
    case 'aprovado':
      return 'bg-green-100 text-green-800';
    case 'não aprovado':
      return 'bg-red-100 text-red-800';
    case 'agendado':
      return 'bg-yellow-100 text-yellow-800';
    case 'pago':
      return 'bg-green-100 text-green-800';
    case 'pendente':
      return 'bg-yellow-100 text-yellow-800';
    case 'cancelado':
      return 'bg-red-100 text-red-800';
    default:
      return 'bg-gray-100 text-gray-800';
  }
};

const getOverallStatusColor = (overallStatus) => {
  switch (overallStatus) {
    case 'concluido':
      return 'bg-green-100 text-green-800';
    case 'aprovado_pendente_pagamento':
      return 'bg-blue-100 text-blue-800';
    case 'rejeitado':
      return 'bg-red-100 text-red-800';
    default:
      return 'bg-yellow-100 text-yellow-800';
  }
};

const getOverallStatusText = (overallStatus) => {
  switch (overallStatus) {
    case 'concluido':
      return 'Concluído';
    case 'aprovado_pendente_pagamento':
      return 'Aprovado - Pendente Pagamento';
    case 'rejeitado':
      return 'Rejeitado';
    default:
      return 'Em Análise';
  }
};

// Componente de Card de Estatística Reutilizável
export const StatsCard = ({ title, value, description, icon: Icon, color = "blue", trend = null }) => {
  const colorClasses = {
    blue: "text-blue-600 bg-blue-100",
    green: "text-green-600 bg-green-100",
    yellow: "text-yellow-600 bg-yellow-100",
    red: "text-red-600 bg-red-100",
    purple: "text-purple-600 bg-purple-100"
  };

  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
        <CardTitle className="text-sm font-medium">{title}</CardTitle>
        <div className={`h-8 w-8 rounded-full flex items-center justify-center ${colorClasses[color]}`}>
          <Icon className="h-4 w-4" />
        </div>
      </CardHeader>
      <CardContent>
        <div className="text-2xl font-bold">{value}</div>
        <p className="text-xs text-muted-foreground">
          {description}
          {trend && (
            <span className={`ml-1 ${trend > 0 ? 'text-green-600' : 'text-red-600'}`}>
              {trend > 0 ? '↗' : '↘'} {Math.abs(trend)}%
            </span>
          )}
        </p>
      </CardContent>
    </Card>
  );
};

// Componente de Tabela de Indicações Reutilizável
export const IndicationsTable = ({ isAdmin = false }) => {
  const { data: indications, loading, error, updateStatus } = useFirestoreCRUD('indications');
  const { notifyChange } = useRealtime();

  const handleStatusChange = async (indicationId, newStatus) => {
    const result = await updateStatus(indicationId, newStatus);
    if (result.success) {
      notifyChange('success', `Status da indicação atualizado para ${newStatus}`);
    } else {
      notifyChange('error', result.error || 'Erro ao atualizar status');
    }
  };

  if (loading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Indicações</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-center p-8">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
          </div>
        </CardContent>
      </Card>
    );
  }

  if (error) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Indicações</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-center p-8 text-red-600">
            Erro ao carregar indicações: {error}
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Gestão de Indicações</CardTitle>
        <CardDescription>
          {isAdmin ? 'Gerencie todas as indicações do sistema' : 'Suas indicações mais recentes'}
        </CardDescription>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {indications.length === 0 ? (
            <div className="text-center p-8 text-gray-500">
              Nenhuma indicação encontrada
            </div>
          ) : (
            indications.map((indication) => (
              <div key={indication.id} className="flex items-center justify-between p-4 border rounded-lg">
                <div className="flex-1">
                  <h3 className="font-medium">{indication.client_name}</h3>
                  <p className="text-sm text-gray-500">{indication.email}</p>
                  <p className="text-sm text-gray-500">{indication.phone}</p>
                  {isAdmin && indication.ambassadorName && (
                    <p className="text-xs text-gray-400">
                      Por: {indication.ambassadorName}
                    </p>
                  )}
                  <p className="text-xs text-gray-400">
                    {new Date(indication.createdAt).toLocaleDateString('pt-BR')}
                  </p>
                </div>
                <div className="flex flex-col items-end space-y-2">
                  <div className="flex space-x-2">
                    <Badge className={getStatusColor(indication.status)}>
                      {indication.status}
                    </Badge>
                    {indication.overall_status && (
                      <Badge className={getOverallStatusColor(indication.overall_status)}>
                        {getOverallStatusText(indication.overall_status)}
                      </Badge>
                    )}
                  </div>
                  {isAdmin && (
                    <Select 
                      value={indication.status} 
                      onValueChange={(value) => handleStatusChange(indication.id, value)}
                      className="w-32" // Adicionado className diretamente ao Select
                    >
                      <SelectItem value="agendado">Agendado</SelectItem>
                      <SelectItem value="aprovado">Aprovado</SelectItem>
                      <SelectItem value="não aprovado">Não Aprovado</SelectItem>
                    </Select>
                  )}
                  <p className="text-sm text-gray-500">{getOriginDisplayName(indication.origin)}</p>
                  <p className="text-sm text-gray-500">{getSegmentDisplayName(indication.segment)}</p>
                </div>
              </div>
            ))
          )}
        </div>
      </CardContent>
    </Card>
  );
};

// Componente de Tabela de Comissões Reutilizável
export const CommissionsTable = ({ isAdmin = false }) => {
  const { data: commissions, loading, error, updateStatus } = useFirestoreCRUD('commissions');
  const { notifyChange } = useRealtime();

  const handleStatusChange = async (commissionId, newStatus) => {
    const result = await updateStatus(commissionId, newStatus);
    if (result.success) {
      notifyChange('success', `Status da comissão atualizado para ${newStatus}`);
    } else {
      notifyChange('error', result.error || 'Erro ao atualizar status');
    }
  };

  const handlePaymentClick = async (commissionId) => {
    await handleStatusChange(commissionId, 'pago');
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'pago':
        return 'bg-green-100 text-green-800';
      case 'pendente':
        return 'bg-yellow-100 text-yellow-800';
      case 'cancelado':
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  if (loading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Comissões</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-center p-8">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
          </div>
        </CardContent>
      </Card>
    );
  }

  if (error) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Comissões</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-center p-8 text-red-600">
            Erro ao carregar comissões: {error}
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Gestão de Comissões</CardTitle>
        <CardDescription>
          {isAdmin ? 'Gerencie todas as comissões do sistema' : 'Suas comissões'}
        </CardDescription>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {commissions.length === 0 ? (
            <div className="text-center p-8 text-gray-500">
              Nenhuma comissão encontrada
            </div>
          ) : (
            commissions.map((commission) => (
              <div key={commission.id} className="flex items-center justify-between p-4 border rounded-lg">
                <div className="flex-1">
                  <h3 className="font-medium">{commission.clientName}</h3>
                  {isAdmin && (
                    <p className="text-sm text-gray-500">
                      Embaixadora: {commission.ambassadorName}
                    </p>
                  )}
                  <p className="text-xs text-gray-400">
                    {new Date(commission.createdAt).toLocaleDateString('pt-BR')}
                  </p>
                  {commission.overall_status && (
                    <Badge className={getOverallStatusColor(commission.overall_status)} size="sm">
                      {getOverallStatusText(commission.overall_status)}
                    </Badge>
                  )}
                </div>
                <div className="flex flex-col items-end space-y-2">
                  <div className="text-right">
                    <p className="font-medium">R$ {commission.value?.toFixed(2) || '0.00'}</p>
                    <Badge className={getStatusColor(commission.status)}>
                      {commission.status}
                    </Badge>
                  </div>
                  {isAdmin && (
                    <div className="flex space-x-2">
                      {commission.status === 'pendente' && (
                        <Button
                          size="sm"
                          className="bg-green-600 hover:bg-green-700"
                          onClick={() => handlePaymentClick(commission.id)}
                        >
                          Marcar como Pago
                        </Button>
                      )}
                      <Select 
                        value={commission.status} 
                        onValueChange={(value) => handleStatusChange(commission.id, value)}
                        className="w-32" // Adicionado className diretamente ao Select
                      >
                        <SelectItem value="pendente">Pendente</SelectItem>
                        <SelectItem value="pago">Pago</SelectItem>
                        <SelectItem value="cancelado">Cancelado</SelectItem>
                        <SelectItem value="em_analise">Em Análise</SelectItem>
                      </Select>
                    </div>
                  )}
                </div>
              </div>
            ))
          )}
        </div>
      </CardContent>
    </Card>
  );
};

// Formulário de Nova Indicação Reutilizável
export const NewIndicationForm = ({ onClose, onSuccess }) => {
  const [formData, setFormData] = useState({
    client_name: '',
    email: '',
    phone: '',
    origin: 'website',
    segment: 'outros'
  });

  const { create } = useFirestoreCRUD('indications');
  const { notifyChange } = useRealtime();
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);

    const result = await create(formData);
    
    if (result.success) {
      notifyChange('success', 'Indicação criada com sucesso!');
        setFormData({
          client_name: '',
          email: '',
          phone: '',
          origin: 'website',
          segment: 'outros'
        });
      onSuccess && onSuccess(result.data);
      onClose && onClose();
    } else {
      notifyChange('error', result.error || 'Erro ao criar indicação');
    }

    setLoading(false);
  };

  const handleChange = (field, value) => {
    setFormData(prev => ({ ...prev, [field]: value }));
  };

  return (
    <Card className="w-full max-w-md">
      <CardHeader>
        <CardTitle>Nova Indicação</CardTitle>
        <CardDescription>Cadastre uma nova indicação de cliente</CardDescription>
      </CardHeader>
      <CardContent>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="client_name">Nome do Cliente</Label>
            <Input
              id="client_name"
              value={formData.client_name}
              onChange={(e) => handleChange('client_name', e.target.value)}
              placeholder="Digite o nome do cliente"
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
              placeholder="Digite o email do cliente"
              required
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="phone">Telefone</Label>
            <Input
              id="phone"
              value={formData.phone}
              onChange={(e) => handleChange('phone', e.target.value)}
              placeholder="Digite o telefone do cliente"
              required
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="origin">Origem</Label>
            <Select value={formData.origin} onValueChange={(value) => handleChange('origin', value)}>
              {getOriginOptions().map((option) => (
                <SelectItem key={option.value} value={option.value}>
                  {option.label}
                </SelectItem>
              ))}
            </Select>
          </div>

          <div className="space-y-2">
            <Label htmlFor="segment">Segmento</Label>
            <Select value={formData.segment} onValueChange={(value) => handleChange('segment', value)}>
              {getSegmentOptions().map((option) => (
                <SelectItem key={option.value} value={option.value}>
                  {option.label}
                </SelectItem>
              ))}
            </Select>
          </div>

          <div className="flex space-x-2">
            <Button type="submit" disabled={loading} className="flex-1">
              {loading ? 'Criando...' : 'Criar Indicação'}
            </Button>
            {onClose && (
              <Button type="button" variant="outline" onClick={onClose}>
                Cancelar
              </Button>
            )}
          </div>
        </form>
      </CardContent>
    </Card>
  );
};



