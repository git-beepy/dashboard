"""
Sistema de validação robusta para o projeto Beepy
"""
import re
import phonenumbers
from phonenumbers import NumberParseException
from email_validator import validate_email, EmailNotValidError
from datetime import datetime
from typing import Dict, List, Any, Optional, Union
import logging

logger = logging.getLogger(__name__)

class ValidationError(Exception):
    """Exceção customizada para erros de validação"""
    def __init__(self, message: str, field: str = None, code: str = None):
        self.message = message
        self.field = field
        self.code = code
        super().__init__(self.message)

class BaseValidator:
    """Classe base para validadores"""
    
    def __init__(self):
        self.errors = []
    
    def add_error(self, field: str, message: str, code: str = None):
        """Adiciona um erro à lista de erros"""
        self.errors.append({
            'field': field,
            'message': message,
            'code': code or 'invalid'
        })
    
    def is_valid(self) -> bool:
        """Retorna True se não há erros"""
        return len(self.errors) == 0
    
    def get_errors(self) -> List[Dict]:
        """Retorna lista de erros"""
        return self.errors
    
    def clear_errors(self):
        """Limpa a lista de erros"""
        self.errors = []

class EmailValidator(BaseValidator):
    """Validador para emails"""
    
    def validate(self, email: str, field_name: str = 'email') -> bool:
        """Valida formato de email"""
        if not email:
            self.add_error(field_name, 'Email é obrigatório', 'required')
            return False
        
        try:
            # Validação básica de formato
            validated_email = validate_email(email)
            return True
        except EmailNotValidError as e:
            self.add_error(field_name, f'Email inválido: {str(e)}', 'invalid_format')
            return False

class PhoneValidator(BaseValidator):
    """Validador para telefones"""
    
    def validate(self, phone: str, field_name: str = 'phone', country_code: str = 'BR') -> bool:
        """Valida formato de telefone"""
        if not phone:
            self.add_error(field_name, 'Telefone é obrigatório', 'required')
            return False
        
        try:
            # Parse do número de telefone
            parsed_number = phonenumbers.parse(phone, country_code)
            
            # Verificar se é um número válido
            if not phonenumbers.is_valid_number(parsed_number):
                self.add_error(field_name, 'Número de telefone inválido', 'invalid_format')
                return False
            
            # Verificar se é um número possível
            if not phonenumbers.is_possible_number(parsed_number):
                self.add_error(field_name, 'Número de telefone não é possível', 'invalid_format')
                return False
            
            return True
            
        except NumberParseException as e:
            self.add_error(field_name, f'Erro ao validar telefone: {str(e)}', 'parse_error')
            return False

class PasswordValidator(BaseValidator):
    """Validador para senhas"""
    
    def __init__(self, min_length: int = 8, require_uppercase: bool = True, 
                 require_lowercase: bool = True, require_numbers: bool = True, 
                 require_special: bool = False):
        super().__init__()
        self.min_length = min_length
        self.require_uppercase = require_uppercase
        self.require_lowercase = require_lowercase
        self.require_numbers = require_numbers
        self.require_special = require_special
    
    def validate(self, password: str, field_name: str = 'password') -> bool:
        """Valida força da senha"""
        if not password:
            self.add_error(field_name, 'Senha é obrigatória', 'required')
            return False
        
        # Verificar comprimento mínimo
        if len(password) < self.min_length:
            self.add_error(field_name, f'Senha deve ter pelo menos {self.min_length} caracteres', 'too_short')
            return False
        
        # Verificar maiúsculas
        if self.require_uppercase and not re.search(r'[A-Z]', password):
            self.add_error(field_name, 'Senha deve conter pelo menos uma letra maiúscula', 'no_uppercase')
            return False
        
        # Verificar minúsculas
        if self.require_lowercase and not re.search(r'[a-z]', password):
            self.add_error(field_name, 'Senha deve conter pelo menos uma letra minúscula', 'no_lowercase')
            return False
        
        # Verificar números
        if self.require_numbers and not re.search(r'\d', password):
            self.add_error(field_name, 'Senha deve conter pelo menos um número', 'no_numbers')
            return False
        
        # Verificar caracteres especiais
        if self.require_special and not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            self.add_error(field_name, 'Senha deve conter pelo menos um caractere especial', 'no_special')
            return False
        
        return True

class UserValidator(BaseValidator):
    """Validador para dados de usuário"""
    
    def __init__(self):
        super().__init__()
        self.email_validator = EmailValidator()
        self.password_validator = PasswordValidator(min_length=6, require_special=False)
    
    def validate_create(self, data: Dict[str, Any]) -> bool:
        """Valida dados para criação de usuário"""
        self.clear_errors()
        
        # Validar nome
        if not data.get('name'):
            self.add_error('name', 'Nome é obrigatório', 'required')
        elif len(data['name'].strip()) < 2:
            self.add_error('name', 'Nome deve ter pelo menos 2 caracteres', 'too_short')
        
        # Validar email
        if not self.email_validator.validate(data.get('email', ''), 'email'):
            self.errors.extend(self.email_validator.get_errors())
        
        # Validar senha
        if not self.password_validator.validate(data.get('password', ''), 'password'):
            self.errors.extend(self.password_validator.get_errors())
        
        # Validar role
        valid_roles = ['admin', 'embaixadora']
        if not data.get('role') or data['role'] not in valid_roles:
            self.add_error('role', f'Role deve ser um dos seguintes: {", ".join(valid_roles)}', 'invalid_choice')
        
        return self.is_valid()
    
    def validate_update(self, data: Dict[str, Any]) -> bool:
        """Valida dados para atualização de usuário"""
        self.clear_errors()
        
        # Validar nome (se fornecido)
        if 'name' in data:
            if not data['name']:
                self.add_error('name', 'Nome não pode estar vazio', 'required')
            elif len(data['name'].strip()) < 2:
                self.add_error('name', 'Nome deve ter pelo menos 2 caracteres', 'too_short')
        
        # Validar email (se fornecido)
        if 'email' in data:
            if not self.email_validator.validate(data['email'], 'email'):
                self.errors.extend(self.email_validator.get_errors())
        
        # Validar senha (se fornecida)
        if 'password' in data and data['password']:
            if not self.password_validator.validate(data['password'], 'password'):
                self.errors.extend(self.password_validator.get_errors())
        
        # Validar role (se fornecido)
        if 'role' in data:
            valid_roles = ['admin', 'embaixadora']
            if data['role'] not in valid_roles:
                self.add_error('role', f'Role deve ser um dos seguintes: {", ".join(valid_roles)}', 'invalid_choice')
        
        return self.is_valid()

class IndicationValidator(BaseValidator):
    """Validador para dados de indicação"""
    
    def __init__(self):
        super().__init__()
        self.email_validator = EmailValidator()
        self.phone_validator = PhoneValidator()
    
    def validate_create(self, data: Dict[str, Any]) -> bool:
        """Valida dados para criação de indicação"""
        self.clear_errors()
        
        # Validar nome do cliente
        if not data.get('clientName'):
            self.add_error('clientName', 'Nome do cliente é obrigatório', 'required')
        elif len(data['clientName'].strip()) < 2:
            self.add_error('clientName', 'Nome do cliente deve ter pelo menos 2 caracteres', 'too_short')
        
        # Validar email do cliente
        if not self.email_validator.validate(data.get('clientEmail', ''), 'clientEmail'):
            self.errors.extend(self.email_validator.get_errors())
        
        # Validar telefone do cliente
        if not self.phone_validator.validate(data.get('clientPhone', ''), 'clientPhone'):
            self.errors.extend(self.phone_validator.get_errors())
        
        # Validar segmento
        valid_segments = [
            'geral', 'premium', 'corporativo', 'startup', 'varejo', 
            'servicos', 'saude', 'educacao', 'tecnologia'
        ]
        if not data.get('segment') or data['segment'] not in valid_segments:
            self.add_error('segment', f'Segmento deve ser um dos seguintes: {", ".join(valid_segments)}', 'invalid_choice')
        
        # Validar origem
        valid_origins = [
            'indicacao_pessoal', 'redes_sociais', 'evento', 'site', 
            'email_marketing', 'publicidade', 'parceria', 'outros'
        ]
        if data.get('origin') and data['origin'] not in valid_origins:
            self.add_error('origin', f'Origem deve ser um dos seguintes: {", ".join(valid_origins)}', 'invalid_choice')
        
        # Validar observações (opcional, mas se fornecido deve ter tamanho razoável)
        if data.get('observations') and len(data['observations']) > 1000:
            self.add_error('observations', 'Observações não podem exceder 1000 caracteres', 'too_long')
        
        return self.is_valid()
    
    def validate_update_status(self, status: str) -> bool:
        """Valida atualização de status de indicação"""
        self.clear_errors()
        
        valid_statuses = ['pendente', 'aprovada', 'rejeitada', 'em_analise']
        if status not in valid_statuses:
            self.add_error('status', f'Status deve ser um dos seguintes: {", ".join(valid_statuses)}', 'invalid_choice')
        
        return self.is_valid()

class CommissionValidator(BaseValidator):
    """Validador para dados de comissão"""
    
    def validate_create(self, data: Dict[str, Any]) -> bool:
        """Valida dados para criação de comissão"""
        self.clear_errors()
        
        # Validar valor
        if not data.get('amount'):
            self.add_error('amount', 'Valor da comissão é obrigatório', 'required')
        else:
            try:
                amount = float(data['amount'])
                if amount <= 0:
                    self.add_error('amount', 'Valor da comissão deve ser positivo', 'invalid_value')
                elif amount > 100000:  # Limite máximo razoável
                    self.add_error('amount', 'Valor da comissão muito alto', 'too_high')
            except (ValueError, TypeError):
                self.add_error('amount', 'Valor da comissão deve ser um número válido', 'invalid_format')
        
        # Validar status
        valid_statuses = ['pendente', 'paga', 'cancelada']
        if data.get('status') and data['status'] not in valid_statuses:
            self.add_error('status', f'Status deve ser um dos seguintes: {", ".join(valid_statuses)}', 'invalid_choice')
        
        return self.is_valid()

def validate_request_data(validator_class, data: Dict[str, Any], method: str = 'create') -> Dict[str, Any]:
    """
    Função utilitária para validar dados de requisição
    
    Args:
        validator_class: Classe do validador a ser usado
        data: Dados a serem validados
        method: Método de validação ('create', 'update', etc.)
    
    Returns:
        Dict com resultado da validação
    """
    try:
        validator = validator_class()
        
        # Chamar método de validação apropriado
        if method == 'create':
            is_valid = validator.validate_create(data)
        elif method == 'update':
            is_valid = validator.validate_update(data)
        elif method == 'update_status' and hasattr(validator, 'validate_update_status'):
            is_valid = validator.validate_update_status(data.get('status', ''))
        else:
            raise ValueError(f"Método de validação '{method}' não suportado")
        
        return {
            'valid': is_valid,
            'errors': validator.get_errors()
        }
        
    except Exception as e:
        logger.error(f"Erro durante validação: {str(e)}")
        return {
            'valid': False,
            'errors': [{'field': 'general', 'message': 'Erro interno de validação', 'code': 'internal_error'}]
        }

# Decorador para validação automática de rotas
def validate_json(validator_class, method: str = 'create'):
    """
    Decorador para validação automática de dados JSON em rotas Flask
    """
    def decorator(f):
        def wrapper(*args, **kwargs):
            from flask import request, jsonify
            
            # Obter dados JSON da requisição
            if not request.is_json:
                return jsonify({'error': 'Content-Type deve ser application/json'}), 400
            
            data = request.get_json()
            if not data:
                return jsonify({'error': 'Dados JSON são obrigatórios'}), 400
            
            # Validar dados
            validation_result = validate_request_data(validator_class, data, method)
            
            if not validation_result['valid']:
                return jsonify({
                    'error': 'Dados inválidos',
                    'validation_errors': validation_result['errors']
                }), 400
            
            # Se válido, continuar com a função original
            return f(*args, **kwargs)
        
        wrapper.__name__ = f.__name__
        return wrapper
    return decorator

