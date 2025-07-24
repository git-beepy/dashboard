"""
Sistema de Logs de Auditoria para o projeto Beepy
Registra todas as ações importantes do sistema para compliance e segurança
"""
import json
import logging
import os
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List
from functools import wraps
from flask import request, g
from flask_jwt_extended import get_jwt_identity, verify_jwt_in_request
from enum import Enum
import hashlib
import uuid

# Configurar logger específico para auditoria
audit_logger = logging.getLogger('audit')
audit_logger.setLevel(logging.INFO)

# Handler para arquivo de auditoria
audit_handler = logging.FileHandler('logs/audit.log')
audit_handler.setLevel(logging.INFO)

# Formatter para logs de auditoria
audit_formatter = logging.Formatter(
    '%(asctime)s - AUDIT - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S UTC'
)
audit_handler.setFormatter(audit_formatter)
audit_logger.addHandler(audit_handler)

class AuditEventType(Enum):
    """Tipos de eventos de auditoria"""
    # Autenticação
    LOGIN_SUCCESS = "login_success"
    LOGIN_FAILURE = "login_failure"
    LOGOUT = "logout"
    TOKEN_REFRESH = "token_refresh"
    
    # Usuários
    USER_CREATED = "user_created"
    USER_UPDATED = "user_updated"
    USER_DELETED = "user_deleted"
    USER_STATUS_CHANGED = "user_status_changed"
    USER_PASSWORD_CHANGED = "user_password_changed"
    
    # Indicações
    INDICATION_CREATED = "indication_created"
    INDICATION_UPDATED = "indication_updated"
    INDICATION_STATUS_CHANGED = "indication_status_changed"
    INDICATION_DELETED = "indication_deleted"
    
    # Comissões
    COMMISSION_CREATED = "commission_created"
    COMMISSION_UPDATED = "commission_updated"
    COMMISSION_PAID = "commission_paid"
    COMMISSION_CANCELLED = "commission_cancelled"
    
    # Sistema
    SYSTEM_CONFIG_CHANGED = "system_config_changed"
    DATA_EXPORT = "data_export"
    DATA_IMPORT = "data_import"
    BACKUP_CREATED = "backup_created"
    
    # Segurança
    UNAUTHORIZED_ACCESS = "unauthorized_access"
    RATE_LIMIT_EXCEEDED = "rate_limit_exceeded"
    SUSPICIOUS_ACTIVITY = "suspicious_activity"
    
    # Acesso a dados
    DATA_ACCESS = "data_access"
    SENSITIVE_DATA_ACCESS = "sensitive_data_access"
    BULK_DATA_ACCESS = "bulk_data_access"

class AuditSeverity(Enum):
    """Níveis de severidade para auditoria"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class AuditLogger:
    """Classe principal para logging de auditoria"""
    
    def __init__(self):
        self.session_id = None
        self.user_context = {}
    
    def _get_user_context(self) -> Dict[str, Any]:
        """Obtém contexto do usuário atual"""
        try:
            verify_jwt_in_request(optional=True)
            user_email = get_jwt_identity()
            
            if user_email:
                return {
                    'user_email': user_email,
                    'user_id': getattr(g, 'current_user_id', None),
                    'user_role': getattr(g, 'current_user_role', None),
                    'authenticated': True
                }
        except:
            pass
        
        return {
            'user_email': None,
            'user_id': None,
            'user_role': None,
            'authenticated': False
        }
    
    def _get_request_context(self) -> Dict[str, Any]:
        """Obtém contexto da requisição"""
        return {
            'ip_address': request.remote_addr if request else None,
            'user_agent': request.headers.get('User-Agent') if request else None,
            'method': request.method if request else None,
            'endpoint': request.endpoint if request else None,
            'url': request.url if request else None,
            'referrer': request.referrer if request else None,
            'session_id': getattr(g, 'session_id', None)
        }
    
    def _generate_event_id(self) -> str:
        """Gera ID único para o evento"""
        return str(uuid.uuid4())
    
    def _calculate_checksum(self, data: Dict[str, Any]) -> str:
        """Calcula checksum dos dados para integridade"""
        data_str = json.dumps(data, sort_keys=True, default=str)
        return hashlib.sha256(data_str.encode()).hexdigest()[:16]
    
    def log_event(
        self,
        event_type: AuditEventType,
        description: str,
        severity: AuditSeverity = AuditSeverity.MEDIUM,
        resource_type: str = None,
        resource_id: str = None,
        old_values: Dict = None,
        new_values: Dict = None,
        additional_data: Dict = None,
        success: bool = True
    ):
        """
        Registra um evento de auditoria
        
        Args:
            event_type: Tipo do evento
            description: Descrição do evento
            severity: Nível de severidade
            resource_type: Tipo do recurso afetado
            resource_id: ID do recurso afetado
            old_values: Valores anteriores (para updates)
            new_values: Novos valores (para updates)
            additional_data: Dados adicionais
            success: Se a operação foi bem-sucedida
        """
        
        # Dados base do evento
        event_data = {
            'event_id': self._generate_event_id(),
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'event_type': event_type.value,
            'description': description,
            'severity': severity.value,
            'success': success,
            'user_context': self._get_user_context(),
            'request_context': self._get_request_context()
        }
        
        # Adicionar dados específicos do recurso
        if resource_type:
            event_data['resource'] = {
                'type': resource_type,
                'id': resource_id
            }
        
        # Adicionar mudanças (para operações de update)
        if old_values is not None or new_values is not None:
            event_data['changes'] = {
                'old_values': old_values,
                'new_values': new_values
            }
        
        # Adicionar dados extras
        if additional_data:
            event_data['additional_data'] = additional_data
        
        # Calcular checksum para integridade
        event_data['checksum'] = self._calculate_checksum(event_data)
        
        # Log do evento
        audit_logger.info(json.dumps(event_data, default=str, ensure_ascii=False))
        
        # Log adicional para eventos críticos
        if severity == AuditSeverity.CRITICAL:
            logging.getLogger().critical(f"AUDIT CRITICAL: {description}")
    
    def log_authentication(self, email: str, success: bool, reason: str = None):
        """Log de tentativas de autenticação"""
        event_type = AuditEventType.LOGIN_SUCCESS if success else AuditEventType.LOGIN_FAILURE
        severity = AuditSeverity.LOW if success else AuditSeverity.MEDIUM
        
        description = f"Tentativa de login para {email}"
        if not success and reason:
            description += f" - Falha: {reason}"
        
        additional_data = {'email': email}
        if reason:
            additional_data['failure_reason'] = reason
        
        self.log_event(
            event_type=event_type,
            description=description,
            severity=severity,
            additional_data=additional_data,
            success=success
        )
    
    def log_user_action(self, action: str, target_user_id: str, old_data: Dict = None, new_data: Dict = None):
        """Log de ações relacionadas a usuários"""
        event_type_map = {
            'create': AuditEventType.USER_CREATED,
            'update': AuditEventType.USER_UPDATED,
            'delete': AuditEventType.USER_DELETED,
            'status_change': AuditEventType.USER_STATUS_CHANGED
        }
        
        event_type = event_type_map.get(action, AuditEventType.USER_UPDATED)
        description = f"Usuário {action} - ID: {target_user_id}"
        
        self.log_event(
            event_type=event_type,
            description=description,
            severity=AuditSeverity.MEDIUM,
            resource_type='user',
            resource_id=target_user_id,
            old_values=old_data,
            new_values=new_data
        )
    
    def log_indication_action(self, action: str, indication_id: str, old_data: Dict = None, new_data: Dict = None):
        """Log de ações relacionadas a indicações"""
        event_type_map = {
            'create': AuditEventType.INDICATION_CREATED,
            'update': AuditEventType.INDICATION_UPDATED,
            'status_change': AuditEventType.INDICATION_STATUS_CHANGED,
            'delete': AuditEventType.INDICATION_DELETED
        }
        
        event_type = event_type_map.get(action, AuditEventType.INDICATION_UPDATED)
        description = f"Indicação {action} - ID: {indication_id}"
        
        severity = AuditSeverity.HIGH if action == 'delete' else AuditSeverity.MEDIUM
        
        self.log_event(
            event_type=event_type,
            description=description,
            severity=severity,
            resource_type='indication',
            resource_id=indication_id,
            old_values=old_data,
            new_values=new_data
        )
    
    def log_commission_action(self, action: str, commission_id: str, amount: float = None, old_data: Dict = None, new_data: Dict = None):
        """Log de ações relacionadas a comissões"""
        event_type_map = {
            'create': AuditEventType.COMMISSION_CREATED,
            'update': AuditEventType.COMMISSION_UPDATED,
            'paid': AuditEventType.COMMISSION_PAID,
            'cancelled': AuditEventType.COMMISSION_CANCELLED
        }
        
        event_type = event_type_map.get(action, AuditEventType.COMMISSION_UPDATED)
        description = f"Comissão {action} - ID: {commission_id}"
        
        if amount:
            description += f" - Valor: R$ {amount:.2f}"
        
        severity = AuditSeverity.HIGH if action in ['paid', 'cancelled'] else AuditSeverity.MEDIUM
        
        additional_data = {}
        if amount:
            additional_data['amount'] = amount
        
        self.log_event(
            event_type=event_type,
            description=description,
            severity=severity,
            resource_type='commission',
            resource_id=commission_id,
            old_values=old_data,
            new_values=new_data,
            additional_data=additional_data if additional_data else None
        )
    
    def log_security_event(self, event_type: AuditEventType, description: str, additional_data: Dict = None):
        """Log de eventos de segurança"""
        self.log_event(
            event_type=event_type,
            description=description,
            severity=AuditSeverity.HIGH,
            additional_data=additional_data
        )
    
    def log_data_access(self, resource_type: str, resource_ids: List[str] = None, sensitive: bool = False):
        """Log de acesso a dados"""
        if len(resource_ids or []) > 10:
            event_type = AuditEventType.BULK_DATA_ACCESS
            description = f"Acesso em massa a {resource_type} - {len(resource_ids)} registros"
        elif sensitive:
            event_type = AuditEventType.SENSITIVE_DATA_ACCESS
            description = f"Acesso a dados sensíveis - {resource_type}"
        else:
            event_type = AuditEventType.DATA_ACCESS
            description = f"Acesso a dados - {resource_type}"
        
        additional_data = {
            'resource_count': len(resource_ids) if resource_ids else 1,
            'sensitive': sensitive
        }
        
        if resource_ids and len(resource_ids) <= 10:
            additional_data['resource_ids'] = resource_ids
        
        severity = AuditSeverity.HIGH if sensitive else AuditSeverity.LOW
        
        self.log_event(
            event_type=event_type,
            description=description,
            severity=severity,
            additional_data=additional_data
        )

# Instância global do audit logger
audit_logger_instance = AuditLogger()

def audit_log(
    event_type: AuditEventType,
    description: str = None,
    severity: AuditSeverity = AuditSeverity.MEDIUM,
    resource_type: str = None,
    auto_description: bool = True
):
    """
    Decorador para logging automático de auditoria
    
    Args:
        event_type: Tipo do evento
        description: Descrição customizada (opcional)
        severity: Nível de severidade
        resource_type: Tipo do recurso
        auto_description: Se deve gerar descrição automaticamente
    """
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            # Capturar dados antes da execução
            user_context = audit_logger_instance._get_user_context()
            
            try:
                # Executar função
                result = f(*args, **kwargs)
                
                # Gerar descrição automática se necessário
                if auto_description and not description:
                    func_name = f.__name__
                    auto_desc = f"Execução de {func_name}"
                    if user_context['authenticated']:
                        auto_desc += f" por {user_context['user_email']}"
                else:
                    auto_desc = description or f"Execução de {f.__name__}"
                
                # Log de sucesso
                audit_logger_instance.log_event(
                    event_type=event_type,
                    description=auto_desc,
                    severity=severity,
                    resource_type=resource_type,
                    success=True
                )
                
                return result
                
            except Exception as e:
                # Log de falha
                error_desc = description or f"Falha na execução de {f.__name__}: {str(e)}"
                
                audit_logger_instance.log_event(
                    event_type=event_type,
                    description=error_desc,
                    severity=AuditSeverity.HIGH,
                    resource_type=resource_type,
                    success=False,
                    additional_data={'error': str(e)}
                )
                
                raise
        
        return wrapper
    return decorator

# Decoradores específicos para diferentes tipos de operações
def audit_auth(f):
    """Decorador para operações de autenticação"""
    return audit_log(
        event_type=AuditEventType.LOGIN_SUCCESS,
        severity=AuditSeverity.MEDIUM
    )(f)

def audit_user_management(f):
    """Decorador para gerenciamento de usuários"""
    return audit_log(
        event_type=AuditEventType.USER_UPDATED,
        severity=AuditSeverity.MEDIUM,
        resource_type='user'
    )(f)

def audit_indication_management(f):
    """Decorador para gerenciamento de indicações"""
    return audit_log(
        event_type=AuditEventType.INDICATION_UPDATED,
        severity=AuditSeverity.MEDIUM,
        resource_type='indication'
    )(f)

def audit_commission_management(f):
    """Decorador para gerenciamento de comissões"""
    return audit_log(
        event_type=AuditEventType.COMMISSION_UPDATED,
        severity=AuditSeverity.HIGH,
        resource_type='commission'
    )(f)

def audit_sensitive_data(f):
    """Decorador para acesso a dados sensíveis"""
    return audit_log(
        event_type=AuditEventType.SENSITIVE_DATA_ACCESS,
        severity=AuditSeverity.HIGH
    )(f)

# Funções utilitárias para análise de logs
def get_audit_summary(start_date: datetime = None, end_date: datetime = None) -> Dict[str, Any]:
    """
    Obtém resumo dos logs de auditoria
    
    Args:
        start_date: Data de início
        end_date: Data de fim
    
    Returns:
        Dicionário com resumo dos logs
    """
    # Esta função seria implementada para ler e analisar os logs reais
    # Por simplicidade, retornamos dados mock
    return {
        'total_events': 1500,
        'events_by_type': {
            'login_success': 450,
            'indication_created': 200,
            'user_updated': 150,
            'commission_paid': 80,
            'login_failure': 25
        },
        'events_by_severity': {
            'low': 800,
            'medium': 600,
            'high': 90,
            'critical': 10
        },
        'top_users': [
            {'email': 'admin@beepy.com', 'event_count': 300},
            {'email': 'embaixadora@teste.com', 'event_count': 250}
        ],
        'security_events': 35,
        'failed_operations': 45
    }

def search_audit_logs(
    event_type: str = None,
    user_email: str = None,
    start_date: datetime = None,
    end_date: datetime = None,
    severity: str = None,
    limit: int = 100
) -> List[Dict[str, Any]]:
    """
    Busca logs de auditoria com filtros
    
    Args:
        event_type: Tipo do evento
        user_email: Email do usuário
        start_date: Data de início
        end_date: Data de fim
        severity: Nível de severidade
        limit: Limite de resultados
    
    Returns:
        Lista de eventos de auditoria
    """
    # Esta função seria implementada para buscar nos logs reais
    # Por simplicidade, retornamos dados mock
    return [
        {
            'event_id': 'evt_123',
            'timestamp': '2024-01-15T10:30:00Z',
            'event_type': 'user_created',
            'description': 'Usuário criado - ID: user_456',
            'severity': 'medium',
            'user_email': 'admin@beepy.com',
            'success': True
        }
    ]

# Função para configurar diretório de logs
def setup_audit_logging():
    """Configura sistema de logging de auditoria"""
    # Criar diretório de logs se não existir
    os.makedirs('logs', exist_ok=True)
    
    # Configurar rotação de logs (implementar se necessário)
    logging.info("Sistema de auditoria configurado")

# Middleware para logging automático de requisições
def audit_request_middleware():
    """Middleware para logging automático de requisições importantes"""
    if request.endpoint and request.method in ['POST', 'PUT', 'DELETE']:
        # Log automático para operações de modificação
        audit_logger_instance.log_event(
            event_type=AuditEventType.DATA_ACCESS,
            description=f"Requisição {request.method} para {request.endpoint}",
            severity=AuditSeverity.LOW
        )

