"""
Utilitários para serialização de dados
"""
from datetime import datetime
from typing import Any, Dict


def serialize_firestore_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Serializa dados do Firestore para JSON
    Converte objetos datetime para strings ISO
    """
    if not isinstance(data, dict):
        return data
    
    serialized = {}
    
    for key, value in data.items():
        if isinstance(value, datetime):
            serialized[key] = value.isoformat()
        elif isinstance(value, dict):
            serialized[key] = serialize_firestore_data(value)
        elif isinstance(value, list):
            serialized[key] = [
                serialize_firestore_data(item) if isinstance(item, dict) else item
                for item in value
            ]
        else:
            serialized[key] = value
    
    return serialized

