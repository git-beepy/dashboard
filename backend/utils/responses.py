"""
Utilitários para respostas padronizadas da API
"""
from flask import jsonify
from typing import Any, Dict, Optional


def success_response(data: Any = None, message: str = "Sucesso", status_code: int = 200):
    """Resposta de sucesso padronizada"""
    response_data = {
        "success": True,
        "message": message,
        "data": data
    }
    return jsonify(response_data), status_code


def error_response(message: str, status_code: int = 400, errors: Optional[Dict] = None):
    """Resposta de erro padronizada"""
    response_data = {
        "success": False,
        "message": message,
        "errors": errors
    }
    return jsonify(response_data), status_code


def validation_error_response(errors: Dict, message: str = "Dados inválidos"):
    """Resposta de erro de validação"""
    return error_response(message, 422, errors)


def not_found_response(message: str = "Recurso não encontrado"):
    """Resposta de recurso não encontrado"""
    return error_response(message, 404)


def unauthorized_response(message: str = "Não autorizado"):
    """Resposta de não autorizado"""
    return error_response(message, 401)


def forbidden_response(message: str = "Acesso negado"):
    """Resposta de acesso negado"""
    return error_response(message, 403)


def internal_error_response(message: str = "Erro interno do servidor"):
    """Resposta de erro interno"""
    return error_response(message, 500)

