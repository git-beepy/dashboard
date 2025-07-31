/**
 * Utilitários para validação de dados
 */

/**
 * Validar email
 */
export const validateEmail = (email) => {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return emailRegex.test(email);
};

/**
 * Validar telefone brasileiro
 */
export const validatePhone = (phone) => {
  const phoneRegex = /^\(?[1-9]{2}\)?\s?[9]?[0-9]{4}-?[0-9]{4}$/;
  const numbers = phone.replace(/\D/g, '');
  return numbers.length >= 10 && numbers.length <= 11;
};

/**
 * Validar CPF
 */
export const validateCPF = (cpf) => {
  const numbers = cpf.replace(/\D/g, '');
  
  if (numbers.length !== 11) return false;
  
  // Verificar se todos os dígitos são iguais
  if (/^(\d)\1{10}$/.test(numbers)) return false;
  
  // Validar dígitos verificadores
  let sum = 0;
  for (let i = 0; i < 9; i++) {
    sum += parseInt(numbers.charAt(i)) * (10 - i);
  }
  let remainder = 11 - (sum % 11);
  if (remainder === 10 || remainder === 11) remainder = 0;
  if (remainder !== parseInt(numbers.charAt(9))) return false;
  
  sum = 0;
  for (let i = 0; i < 10; i++) {
    sum += parseInt(numbers.charAt(i)) * (11 - i);
  }
  remainder = 11 - (sum % 11);
  if (remainder === 10 || remainder === 11) remainder = 0;
  if (remainder !== parseInt(numbers.charAt(10))) return false;
  
  return true;
};

/**
 * Validar senha
 */
export const validatePassword = (password) => {
  return {
    isValid: password.length >= 6,
    errors: password.length < 6 ? ['Senha deve ter pelo menos 6 caracteres'] : []
  };
};

/**
 * Validar campos obrigatórios
 */
export const validateRequired = (value, fieldName) => {
  if (!value || (typeof value === 'string' && value.trim() === '')) {
    return `${fieldName} é obrigatório`;
  }
  return null;
};

/**
 * Validar formulário de indicação
 */
export const validateIndicationForm = (data) => {
  const errors = {};
  
  // Nome do cliente
  const nameError = validateRequired(data.client_name, 'Nome do cliente');
  if (nameError) errors.client_name = nameError;
  
  // Email
  const emailError = validateRequired(data.email, 'Email');
  if (emailError) {
    errors.email = emailError;
  } else if (!validateEmail(data.email)) {
    errors.email = 'Email inválido';
  }
  
  // Telefone
  const phoneError = validateRequired(data.phone, 'Telefone');
  if (phoneError) {
    errors.phone = phoneError;
  } else if (!validatePhone(data.phone)) {
    errors.phone = 'Telefone inválido';
  }
  
  return {
    isValid: Object.keys(errors).length === 0,
    errors
  };
};

/**
 * Validar formulário de usuário
 */
export const validateUserForm = (data, isEdit = false) => {
  const errors = {};
  
  // Nome
  const nameError = validateRequired(data.name, 'Nome');
  if (nameError) errors.name = nameError;
  
  // Email
  const emailError = validateRequired(data.email, 'Email');
  if (emailError) {
    errors.email = emailError;
  } else if (!validateEmail(data.email)) {
    errors.email = 'Email inválido';
  }
  
  // Senha (obrigatória apenas na criação)
  if (!isEdit) {
    const passwordError = validateRequired(data.password, 'Senha');
    if (passwordError) {
      errors.password = passwordError;
    } else {
      const passwordValidation = validatePassword(data.password);
      if (!passwordValidation.isValid) {
        errors.password = passwordValidation.errors[0];
      }
    }
  }
  
  // Role
  const roleError = validateRequired(data.role, 'Tipo de usuário');
  if (roleError) errors.role = roleError;
  
  return {
    isValid: Object.keys(errors).length === 0,
    errors
  };
};

