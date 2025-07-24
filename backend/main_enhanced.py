"""
Aplicação principal do Beepy com todas as funcionalidades aprimoradas
"""
import os
import logging
from datetime import timedelta
from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from werkzeug.middleware.proxy_fix import ProxyFix

# Importar módulos customizados
from validators import validate_request_data
from rate_limiting import setup_flask_limiter, auth_rate_limit, api_rate_limit
from audit_logging import setup_audit_logging, audit_logger_instance, AuditEventType, AuditSeverity
from realtime_notifications import create_notification_routes, notification_manager

# Importar rotas existentes
from routes.auth import auth_bp
from routes.users_validated import users_validated_bp
from routes.indications import indications_bp
from routes.commissions import commissions_bp

def create_app(config=None):
    """Factory function para criar a aplicação Flask"""
    app = Flask(__name__)
    
    # Configurações
    app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'your-secret-key-change-in-production')
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=24)
    app.config['JWT_REFRESH_TOKEN_EXPIRES'] = timedelta(days=30)
    
    # Configurações customizadas para testes
    if config:
        app.config.update(config)
    
    # Configurar proxy fix para deployment
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)
    
    # Configurar CORS
    CORS(app, origins="*", allow_headers=["Content-Type", "Authorization"])
    
    # Configurar JWT
    jwt = JWTManager(app)
    
    # Configurar logging
    setup_logging()
    
    # Configurar auditoria
    setup_audit_logging()
    
    # Configurar rate limiting
    limiter = setup_flask_limiter(app)
    
    # Registrar blueprints
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(users_validated_bp, url_prefix='/')
    app.register_blueprint(indications_bp, url_prefix='/')
    app.register_blueprint(commissions_bp, url_prefix='/')
    
    # Configurar notificações em tempo real
    create_notification_routes(app)
    
    # Middleware para auditoria automática
    @app.before_request
    def before_request():
        """Middleware executado antes de cada requisição"""
        # Log de auditoria para operações importantes
        if request.method in ['POST', 'PUT', 'DELETE'] and request.endpoint:
            audit_logger_instance.log_event(
                event_type=AuditEventType.DATA_ACCESS,
                description=f"Requisição {request.method} para {request.endpoint}",
                severity=AuditSeverity.LOW
            )
    
    # Handler para erros JWT
    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        audit_logger_instance.log_security_event(
            event_type=AuditEventType.UNAUTHORIZED_ACCESS,
            description="Tentativa de acesso com token expirado",
            additional_data={'jwt_payload': jwt_payload}
        )
        return jsonify({'error': 'Token expirado'}), 401
    
    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        audit_logger_instance.log_security_event(
            event_type=AuditEventType.UNAUTHORIZED_ACCESS,
            description="Tentativa de acesso com token inválido",
            additional_data={'error': str(error)}
        )
        return jsonify({'error': 'Token inválido'}), 401
    
    @jwt.unauthorized_loader
    def missing_token_callback(error):
        return jsonify({'error': 'Token de acesso necessário'}), 401
    
    # Rotas de saúde e status
    @app.route('/health')
    def health_check():
        """Endpoint de verificação de saúde"""
        return jsonify({
            'status': 'healthy',
            'version': '2.0.0',
            'features': [
                'validation',
                'rate_limiting',
                'audit_logging',
                'real_time_notifications',
                'automated_tests'
            ]
        })
    
    @app.route('/status')
    @api_rate_limit
    def system_status():
        """Endpoint de status do sistema"""
        return jsonify({
            'system': 'Beepy API',
            'status': 'operational',
            'uptime': 'N/A',  # Implementar se necessário
            'active_connections': len(notification_manager.connections),
            'rate_limiting': 'enabled',
            'audit_logging': 'enabled'
        })
    
    # Handler para erros 404
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'error': 'Endpoint não encontrado'}), 404
    
    # Handler para erros 500
    @app.errorhandler(500)
    def internal_error(error):
        audit_logger_instance.log_event(
            event_type=AuditEventType.SYSTEM_CONFIG_CHANGED,
            description=f"Erro interno do servidor: {str(error)}",
            severity=AuditSeverity.CRITICAL,
            success=False
        )
        return jsonify({'error': 'Erro interno do servidor'}), 500
    
    # Handler para validação de dados
    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({'error': 'Dados inválidos na requisição'}), 400
    
    return app

def setup_logging():
    """Configura sistema de logging"""
    # Criar diretório de logs
    os.makedirs('logs', exist_ok=True)
    
    # Configurar logging básico
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('logs/app.log'),
            logging.StreamHandler()
        ]
    )
    
    # Configurar logger específico para auditoria
    audit_logger = logging.getLogger('audit')
    audit_handler = logging.FileHandler('logs/audit.log')
    audit_formatter = logging.Formatter(
        '%(asctime)s - AUDIT - %(levelname)s - %(message)s'
    )
    audit_handler.setFormatter(audit_formatter)
    audit_logger.addHandler(audit_handler)
    audit_logger.setLevel(logging.INFO)

# Criar instância da aplicação
app = create_app()

if __name__ == '__main__':
    # Log de inicialização
    audit_logger_instance.log_event(
        event_type=AuditEventType.SYSTEM_CONFIG_CHANGED,
        description="Sistema Beepy iniciado",
        severity=AuditSeverity.MEDIUM
    )
    
    # Executar aplicação
    port = int(os.getenv('PORT', 10000))
    debug = os.getenv('FLASK_ENV') == 'development'
    
    app.run(
        host='0.0.0.0',
        port=port,
        debug=debug
    )

