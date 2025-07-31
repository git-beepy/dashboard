"""
Configurações gerais da aplicação
"""
import os
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Configurações base da aplicação"""
    
    # Chaves secretas - OBRIGATÓRIAS em produção
    SECRET_KEY = os.environ.get("SECRET_KEY")
    JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY")
    
    # Configurações JWT
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=24)
    
    # Configurações CORS
    CORS_ORIGINS = os.environ.get("CORS_ORIGINS", "*").split(",")
    
    # Validações
    @classmethod
    def validate(cls):
        """Valida se as configurações obrigatórias estão definidas"""
        errors = []
        
        if not cls.SECRET_KEY:
            errors.append("SECRET_KEY não está definida")
        
        if not cls.JWT_SECRET_KEY:
            errors.append("JWT_SECRET_KEY não está definida")
        
        if errors:
            raise ValueError(f"Configurações obrigatórias não definidas: {', '.join(errors)}")
        
        return True


class DevelopmentConfig(Config):
    """Configurações para desenvolvimento"""
    DEBUG = True
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key-CHANGE-IN-PRODUCTION")
    JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "jwt-secret-key-CHANGE-IN-PRODUCTION")


class ProductionConfig(Config):
    """Configurações para produção"""
    DEBUG = False
    
    @classmethod
    def validate(cls):
        """Validação mais rigorosa para produção"""
        super().validate()
        
        # Em produção, não permitir chaves padrão
        if cls.SECRET_KEY and "CHANGE-IN-PRODUCTION" in cls.SECRET_KEY:
            raise ValueError("SECRET_KEY padrão não pode ser usada em produção")
        
        if cls.JWT_SECRET_KEY and "CHANGE-IN-PRODUCTION" in cls.JWT_SECRET_KEY:
            raise ValueError("JWT_SECRET_KEY padrão não pode ser usada em produção")


# Configuração baseada no ambiente
ENV = os.environ.get("FLASK_ENV", "development")

if ENV == "production":
    config = ProductionConfig
else:
    config = DevelopmentConfig

