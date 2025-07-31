/**
 * Utilitários para formatação de dados
 */

/**
 * Formatar valor monetário em Real brasileiro
 */
export const formatCurrency = (value) => {
  if (value === null || value === undefined || isNaN(value)) {
    return 'R$ 0,00';
  }
  
  return new Intl.NumberFormat('pt-BR', {
    style: 'currency',
    currency: 'BRL'
  }).format(value);
};

/**
 * Formatar data para exibição
 */
export const formatDate = (date) => {
  if (!date) return '-';
  
  const dateObj = typeof date === 'string' ? new Date(date) : date;
  
  if (isNaN(dateObj.getTime())) return '-';
  
  return new Intl.DateTimeFormat('pt-BR', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric'
  }).format(dateObj);
};

/**
 * Formatar data e hora para exibição
 */
export const formatDateTime = (date) => {
  if (!date) return '-';
  
  const dateObj = typeof date === 'string' ? new Date(date) : date;
  
  if (isNaN(dateObj.getTime())) return '-';
  
  return new Intl.DateTimeFormat('pt-BR', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  }).format(dateObj);
};

/**
 * Formatar telefone brasileiro
 */
export const formatPhone = (phone) => {
  if (!phone) return '';
  
  // Remove tudo que não é número
  const numbers = phone.replace(/\D/g, '');
  
  // Aplica máscara baseada no tamanho
  if (numbers.length === 11) {
    return numbers.replace(/(\d{2})(\d{5})(\d{4})/, '($1) $2-$3');
  } else if (numbers.length === 10) {
    return numbers.replace(/(\d{2})(\d{4})(\d{4})/, '($1) $2-$3');
  }
  
  return phone;
};

/**
 * Formatar CPF
 */
export const formatCPF = (cpf) => {
  if (!cpf) return '';
  
  const numbers = cpf.replace(/\D/g, '');
  
  if (numbers.length === 11) {
    return numbers.replace(/(\d{3})(\d{3})(\d{3})(\d{2})/, '$1.$2.$3-$4');
  }
  
  return cpf;
};

/**
 * Formatar status para exibição
 */
export const formatStatus = (status) => {
  const statusMap = {
    'agendado': 'Agendado',
    'aprovado': 'Aprovado',
    'não aprovado': 'Não Aprovado',
    'pendente': 'Pendente',
    'pago': 'Pago',
    'cancelado': 'Cancelado'
  };
  
  return statusMap[status] || status;
};

/**
 * Obter cor do status
 */
export const getStatusColor = (status) => {
  const colorMap = {
    'agendado': 'bg-yellow-100 text-yellow-800',
    'aprovado': 'bg-green-100 text-green-800',
    'não aprovado': 'bg-red-100 text-red-800',
    'pendente': 'bg-blue-100 text-blue-800',
    'pago': 'bg-green-100 text-green-800',
    'cancelado': 'bg-gray-100 text-gray-800'
  };
  
  return colorMap[status] || 'bg-gray-100 text-gray-800';
};

/**
 * Truncar texto
 */
export const truncateText = (text, maxLength = 50) => {
  if (!text) return '';
  
  if (text.length <= maxLength) return text;
  
  return text.substring(0, maxLength) + '...';
};

