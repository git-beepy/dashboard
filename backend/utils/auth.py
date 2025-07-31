"""
Utilitários para autenticação e autorização
"""
import bcrypt
from functools import wraps
from flask import request
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from services.firestore_service import UserService
from utils.responses import forbidden_response, unauthorized_response


def hash_password(password: str) -> str:
    """Gera hash da senha usando bcrypt"""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')


def verify_password(password: str, hashed_password: str) -> bool:
    """Verifica se a senha corresponde ao hash"""
    try:
        return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))
    except Exception:
        return False


def require_role(required_role: str):
    """Decorator para exigir uma role específica"""
    def decorator(f):
        @wraps(f)
        @jwt_required()
        def decorated_function(*args, **kwargs):
            try:
                current_user_id = get_jwt_identity()
                user_service = UserService()
                user = user_service.get_by_id(current_user_id)
                
                if not user:
                    return unauthorized_response("Usuário não encontrado")
                
                if user.get("role") != required_role:
                    return forbidden_response(f"Acesso restrito a {required_role}")
                
                return f(*args, **kwargs)
            except Exception as e:
                return unauthorized_response(f"Erro de autenticação: {str(e)}")
        
        return decorated_function
    return decorator


def require_admin():
    """Decorator para exigir role de admin"""
    return require_role("admin")


def require_ambassador():
    """Decorator para exigir role de ambassador"""
    return require_role("ambassador")


def get_current_user():
    """Retorna o usuário atual autenticado"""
    try:
        current_user_id = get_jwt_identity()
        user_service = UserService()
        return user_service.get_by_id(current_user_id)
    except Exception:
        return None


def is_admin(user: dict) -> bool:
    """Verifica se o usuário é admin"""
    return user and user.get("role") == "admin"


def is_ambassador(user: dict) -> bool:
    """Verifica se o usuário é embaixador"""
    return user and user.get("role") == "ambassador"

