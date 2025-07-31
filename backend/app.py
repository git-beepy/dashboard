"""
Aplicação Flask principal refatorada
"""
from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from config.settings import config
from config.firebase import firebase_config
from routes.auth import auth_bp
from routes.indications import indications_bp
from routes.users_firestore import users_bp
from utils.responses import error_response


def create_app():
    """Factory function para criar a aplicação Flask"""
    
    # Validar configurações
    try:
        config.validate()
    except ValueError as e:
        print(f"❌ Erro de configuração: {e}")
        raise
    
    # Verificar conexão Firebase
    if not firebase_config.is_connected():
        print("❌ Firebase não está conectado")
        raise RuntimeError("Firebase não está conectado")
    
    # Criar aplicação Flask
    app = Flask(__name__)
    
    # Configurações do Flask
    app.config["SECRET_KEY"] = config.SECRET_KEY
    app.config["JWT_SECRET_KEY"] = config.JWT_SECRET_KEY
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = config.JWT_ACCESS_TOKEN_EXPIRES
    
    # Inicializar JWT
    jwt = JWTManager(app)
    
    # Configurar CORS
    CORS(app, 
         supports_credentials=True, 
         origins=config.CORS_ORIGINS,
         resources={r"/*": {"origins": config.CORS_ORIGINS}})
    
    # Registrar blueprints
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(indications_bp, url_prefix='/indications')
    app.register_blueprint(users_bp, url_prefix='/users')
    
    # Handler de erro global
    @app.errorhandler(404)
    def not_found(error):
        return error_response("Endpoint não encontrado", 404)
    
    @app.errorhandler(405)
    def method_not_allowed(error):
        return error_response("Método não permitido", 405)
    
    @app.errorhandler(500)
    def internal_error(error):
        return error_response("Erro interno do servidor", 500)
    
    # Handler para erros JWT
    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return error_response("Token expirado", 401)
    
    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        return error_response("Token inválido", 401)
    
    @jwt.unauthorized_loader
    def missing_token_callback(error):
        return error_response("Token de acesso necessário", 401)
    
    # Rota de health check
    @app.route("/health", methods=["GET"])
    def health_check():
        return {
            "status": "healthy",
            "firebase_connected": firebase_config.is_connected()
        }
    
    print("✅ Aplicação Flask inicializada com sucesso")
    return app


# Criar aplicação
app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=config.DEBUG)

