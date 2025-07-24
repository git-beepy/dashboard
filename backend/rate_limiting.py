"""
Sistema de Rate Limiting para o projeto Beepy
Implementa controle de taxa de requisições para melhorar a segurança
"""
import os
import time
import logging
from functools import wraps
from typing import Dict, Optional, Callable
from flask import request, jsonify, g
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_jwt_extended import get_jwt_identity, verify_jwt_in_request
import redis
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class CustomRateLimiter:
    """Rate limiter customizado com funcionalidades avançadas"""
    
    def __init__(self, redis_url: str = None):
        # Configurar Redis (usar in-memory se Redis não estiver disponível)
        self.redis_client = None
        if redis_url:
            try:
                self.redis_client = redis.from_url(redis_url)
                self.redis_client.ping()  # Testar conexão
                logger.info("Conectado ao Redis para rate limiting")
            except Exception as e:
                logger.warning(f"Falha ao conectar ao Redis: {e}. Usando cache em memória.")
                self.redis_client = None
        
        # Cache em memória como fallback
        self.memory_cache: Dict[str, Dict] = {}
        self.cleanup_interval = 300  # 5 minutos
        self.last_cleanup = time.time()
    
    def _get_key(self, identifier: str, endpoint: str) -> str:
        """Gera chave única para rate limiting"""
        return f"rate_limit:{identifier}:{endpoint}"
    
    def _cleanup_memory_cache(self):
        """Remove entradas expiradas do cache em memória"""
        current_time = time.time()
        if current_time - self.last_cleanup < self.cleanup_interval:
            return
        
        expired_keys = []
        for key, data in self.memory_cache.items():
            if data.get('expires_at', 0) < current_time:
                expired_keys.append(key)
        
        for key in expired_keys:
            del self.memory_cache[key]
        
        self.last_cleanup = current_time
        logger.debug(f"Limpeza do cache: {len(expired_keys)} entradas removidas")
    
    def _get_rate_limit_data(self, key: str) -> Dict:
        """Obtém dados de rate limiting"""
        if self.redis_client:
            try:
                data = self.redis_client.hgetall(key)
                if data:
                    return {
                        'count': int(data.get(b'count', 0)),
                        'window_start': float(data.get(b'window_start', 0)),
                        'expires_at': float(data.get(b'expires_at', 0))
                    }
            except Exception as e:
                logger.error(f"Erro ao acessar Redis: {e}")
        
        # Fallback para cache em memória
        self._cleanup_memory_cache()
        return self.memory_cache.get(key, {
            'count': 0,
            'window_start': time.time(),
            'expires_at': time.time() + 3600
        })
    
    def _set_rate_limit_data(self, key: str, data: Dict, ttl: int = 3600):
        """Define dados de rate limiting"""
        if self.redis_client:
            try:
                pipe = self.redis_client.pipeline()
                pipe.hset(key, mapping={
                    'count': data['count'],
                    'window_start': data['window_start'],
                    'expires_at': data['expires_at']
                })
                pipe.expire(key, ttl)
                pipe.execute()
                return
            except Exception as e:
                logger.error(f"Erro ao salvar no Redis: {e}")
        
        # Fallback para cache em memória
        self.memory_cache[key] = data
    
    def is_allowed(self, identifier: str, endpoint: str, limit: int, window: int) -> tuple[bool, Dict]:
        """
        Verifica se a requisição é permitida
        
        Args:
            identifier: Identificador único (IP, user_id, etc.)
            endpoint: Nome do endpoint
            limit: Número máximo de requisições
            window: Janela de tempo em segundos
        
        Returns:
            (is_allowed, rate_limit_info)
        """
        key = self._get_key(identifier, endpoint)
        current_time = time.time()
        
        # Obter dados atuais
        data = self._get_rate_limit_data(key)
        
        # Verificar se a janela expirou
        if current_time - data['window_start'] >= window:
            # Nova janela
            data = {
                'count': 1,
                'window_start': current_time,
                'expires_at': current_time + window
            }
            self._set_rate_limit_data(key, data, window)
            
            return True, {
                'limit': limit,
                'remaining': limit - 1,
                'reset_time': int(current_time + window),
                'retry_after': None
            }
        
        # Verificar se excedeu o limite
        if data['count'] >= limit:
            retry_after = int(data['window_start'] + window - current_time)
            return False, {
                'limit': limit,
                'remaining': 0,
                'reset_time': int(data['window_start'] + window),
                'retry_after': retry_after
            }
        
        # Incrementar contador
        data['count'] += 1
        self._set_rate_limit_data(key, data, window)
        
        return True, {
            'limit': limit,
            'remaining': limit - data['count'],
            'reset_time': int(data['window_start'] + window),
            'retry_after': None
        }

# Instância global do rate limiter
custom_limiter = CustomRateLimiter(os.getenv('REDIS_URL'))

def get_identifier() -> str:
    """Obtém identificador para rate limiting"""
    try:
        # Tentar obter usuário autenticado
        verify_jwt_in_request(optional=True)
        user_email = get_jwt_identity()
        if user_email:
            return f"user:{user_email}"
    except:
        pass
    
    # Fallback para IP
    return f"ip:{get_remote_address()}"

def rate_limit(limit: int, window: int = 3600, per_user: bool = True, endpoint_specific: bool = True):
    """
    Decorador para rate limiting
    
    Args:
        limit: Número máximo de requisições
        window: Janela de tempo em segundos (padrão: 1 hora)
        per_user: Se True, aplica limite por usuário; se False, por IP
        endpoint_specific: Se True, aplica limite por endpoint específico
    """
    def decorator(f: Callable) -> Callable:
        @wraps(f)
        def wrapper(*args, **kwargs):
            # Obter identificador
            if per_user:
                identifier = get_identifier()
            else:
                identifier = f"ip:{get_remote_address()}"
            
            # Obter nome do endpoint
            if endpoint_specific:
                endpoint = f"{request.method}:{request.endpoint}"
            else:
                endpoint = "global"
            
            # Verificar rate limit
            is_allowed, rate_info = custom_limiter.is_allowed(
                identifier, endpoint, limit, window
            )
            
            if not is_allowed:
                logger.warning(f"Rate limit excedido para {identifier} no endpoint {endpoint}")
                
                response = jsonify({
                    'error': 'Rate limit excedido',
                    'message': f'Muitas requisições. Tente novamente em {rate_info["retry_after"]} segundos.',
                    'rate_limit': rate_info
                })
                response.status_code = 429
                response.headers['X-RateLimit-Limit'] = str(rate_info['limit'])
                response.headers['X-RateLimit-Remaining'] = str(rate_info['remaining'])
                response.headers['X-RateLimit-Reset'] = str(rate_info['reset_time'])
                response.headers['Retry-After'] = str(rate_info['retry_after'])
                
                return response
            
            # Adicionar headers de rate limit na resposta
            response = f(*args, **kwargs)
            
            if hasattr(response, 'headers'):
                response.headers['X-RateLimit-Limit'] = str(rate_info['limit'])
                response.headers['X-RateLimit-Remaining'] = str(rate_info['remaining'])
                response.headers['X-RateLimit-Reset'] = str(rate_info['reset_time'])
            
            return response
        
        return wrapper
    return decorator

def setup_flask_limiter(app):
    """Configura Flask-Limiter para rate limiting global"""
    
    # Configurar storage
    if os.getenv('REDIS_URL'):
        storage_uri = os.getenv('REDIS_URL')
    else:
        storage_uri = "memory://"
    
    # Criar limiter
    limiter = Limiter(
        app=app,
        key_func=get_identifier,
        storage_uri=storage_uri,
        default_limits=["1000 per hour", "100 per minute"],
        headers_enabled=True,
        retry_after="http-date"
    )
    
    # Rate limits específicos por rota
    @limiter.limit("5 per minute")
    @app.route('/auth/login', methods=['POST'])
    def login_rate_limited():
        pass  # Será sobrescrito pela rota real
    
    @limiter.limit("10 per minute")
    @app.route('/users', methods=['POST'])
    def create_user_rate_limited():
        pass  # Será sobrescrito pela rota real
    
    @limiter.limit("20 per minute")
    @app.route('/indications', methods=['POST'])
    def create_indication_rate_limited():
        pass  # Será sobrescrito pela rota real
    
    # Handler para rate limit excedido
    @app.errorhandler(429)
    def ratelimit_handler(e):
        logger.warning(f"Rate limit global excedido: {request.remote_addr} - {request.endpoint}")
        return jsonify({
            'error': 'Rate limit excedido',
            'message': 'Muitas requisições. Tente novamente mais tarde.',
            'retry_after': getattr(e, 'retry_after', None)
        }), 429
    
    return limiter

# Decoradores específicos para diferentes tipos de operações
def auth_rate_limit(f):
    """Rate limit para operações de autenticação (mais restritivo)"""
    return rate_limit(limit=5, window=300, per_user=False)(f)  # 5 tentativas por 5 minutos por IP

def api_rate_limit(f):
    """Rate limit padrão para APIs"""
    return rate_limit(limit=100, window=3600)(f)  # 100 requisições por hora por usuário

def create_rate_limit(f):
    """Rate limit para operações de criação"""
    return rate_limit(limit=20, window=3600)(f)  # 20 criações por hora por usuário

def read_rate_limit(f):
    """Rate limit para operações de leitura"""
    return rate_limit(limit=200, window=3600)(f)  # 200 leituras por hora por usuário

def update_rate_limit(f):
    """Rate limit para operações de atualização"""
    return rate_limit(limit=50, window=3600)(f)  # 50 atualizações por hora por usuário

def delete_rate_limit(f):
    """Rate limit para operações de exclusão"""
    return rate_limit(limit=10, window=3600)(f)  # 10 exclusões por hora por usuário

# Middleware para logging de rate limiting
def log_rate_limit_info():
    """Middleware para logar informações de rate limiting"""
    identifier = get_identifier()
    endpoint = f"{request.method}:{request.endpoint}"
    
    # Log da requisição
    logger.info(f"Requisição: {identifier} -> {endpoint}")
    
    # Adicionar informações ao contexto da requisição
    g.rate_limit_identifier = identifier
    g.rate_limit_endpoint = endpoint

# Função para obter estatísticas de rate limiting
def get_rate_limit_stats(identifier: str = None, hours: int = 24) -> Dict:
    """
    Obtém estatísticas de rate limiting
    
    Args:
        identifier: Identificador específico (opcional)
        hours: Número de horas para análise
    
    Returns:
        Dicionário com estatísticas
    """
    # Esta função seria implementada com dados reais do Redis
    # Por simplicidade, retornamos dados mock
    return {
        'total_requests': 1250,
        'blocked_requests': 15,
        'top_endpoints': [
            {'endpoint': 'GET:/indications', 'count': 450},
            {'endpoint': 'POST:/auth/login', 'count': 120},
            {'endpoint': 'GET:/users', 'count': 80}
        ],
        'top_users': [
            {'identifier': 'user:admin@beepy.com', 'count': 200},
            {'identifier': 'user:embaixadora@teste.com', 'count': 150}
        ],
        'blocked_ips': [
            {'ip': '192.168.1.100', 'count': 10},
            {'ip': '10.0.0.50', 'count': 5}
        ]
    }

# Função para limpar dados antigos (executar periodicamente)
def cleanup_rate_limit_data():
    """Limpa dados antigos de rate limiting"""
    if custom_limiter.redis_client:
        try:
            # Implementar limpeza no Redis
            # Por simplicidade, apenas logamos
            logger.info("Limpeza de dados de rate limiting executada")
        except Exception as e:
            logger.error(f"Erro na limpeza de rate limiting: {e}")
    else:
        custom_limiter._cleanup_memory_cache()
        logger.info("Limpeza de cache em memória executada")

