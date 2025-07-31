"""
Serviço de abstração para operações com Firestore
"""
from typing import Dict, List, Optional, Any
from datetime import datetime
from google.cloud import firestore
from config.firebase import firebase_config
from utils.serializers import serialize_firestore_data


class FirestoreService:
    """Serviço base para operações com Firestore"""
    
    def __init__(self, collection_name: str):
        self.collection_name = collection_name
        self._db = firebase_config.db
        
        if not self._db:
            raise RuntimeError("Firebase não está conectado")
    
    @property
    def collection(self):
        """Retorna a referência da coleção"""
        return self._db.collection(self.collection_name)
    
    def create(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Cria um novo documento"""
        # Adicionar timestamps
        now = datetime.now()
        data.update({
            "created_at": now,
            "updated_at": now
        })
        
        doc_ref = self.collection.add(data)
        document_id = doc_ref[1].id
        
        # Retornar dados com ID
        result = data.copy()
        result["id"] = document_id
        return serialize_firestore_data(result)
    
    def get_by_id(self, document_id: str) -> Optional[Dict[str, Any]]:
        """Busca um documento por ID"""
        doc = self.collection.document(document_id).get()
        
        if not doc.exists:
            return None
        
        data = doc.to_dict()
        data["id"] = doc.id
        return serialize_firestore_data(data)
    
    def get_all(self) -> List[Dict[str, Any]]:
        """Busca todos os documentos da coleção"""
        docs = self.collection.stream()
        results = []
        
        for doc in docs:
            data = doc.to_dict()
            data["id"] = doc.id
            results.append(serialize_firestore_data(data))
        
        return results
    
    def get_by_field(self, field: str, value: Any) -> List[Dict[str, Any]]:
        """Busca documentos por um campo específico"""
        query = self.collection.where(field_path=field, op_string="==", value=value)
        docs = query.stream()
        results = []
        
        for doc in docs:
            data = doc.to_dict()
            data["id"] = doc.id
            results.append(serialize_firestore_data(data))
        
        return results
    
    def update(self, document_id: str, data: Dict[str, Any]) -> bool:
        """Atualiza um documento"""
        try:
            # Adicionar timestamp de atualização
            data["updated_at"] = datetime.now()
            
            self.collection.document(document_id).update(data)
            return True
        except Exception as e:
            print(f"Erro ao atualizar documento {document_id}: {e}")
            return False
    
    def delete(self, document_id: str) -> bool:
        """Deleta um documento"""
        try:
            self.collection.document(document_id).delete()
            return True
        except Exception as e:
            print(f"Erro ao deletar documento {document_id}: {e}")
            return False
    
    def query(self, filters: List[tuple]) -> List[Dict[str, Any]]:
        """Executa uma query com múltiplos filtros"""
        query = self.collection
        
        for field, operator, value in filters:
            query = query.where(field_path=field, op_string=operator, value=value)
        
        docs = query.stream()
        results = []
        
        for doc in docs:
            data = doc.to_dict()
            data["id"] = doc.id
            results.append(serialize_firestore_data(data))
        
        return results


class UserService(FirestoreService):
    """Serviço específico para usuários"""
    
    def __init__(self):
        super().__init__("users")
    
    def get_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Busca usuário por email"""
        results = self.get_by_field("email", email)
        return results[0] if results else None
    
    def get_ambassadors(self) -> List[Dict[str, Any]]:
        """Busca todos os embaixadores"""
        return self.get_by_field("role", "ambassador")


class IndicationService(FirestoreService):
    """Serviço específico para indicações"""
    
    def __init__(self):
        super().__init__("indications")
    
    def get_by_ambassador(self, ambassador_id: str) -> List[Dict[str, Any]]:
        """Busca indicações de um embaixador específico"""
        return self.get_by_field("ambassadorId", ambassador_id)
    
    def update_status(self, indication_id: str, status: str) -> bool:
        """Atualiza o status de uma indicação"""
        if status not in ["agendado", "aprovado", "não aprovado"]:
            raise ValueError("Status inválido")
        
        return self.update(indication_id, {"status": status})


class CommissionService(FirestoreService):
    """Serviço específico para comissões"""
    
    def __init__(self):
        super().__init__("commissions")
    
    def get_by_ambassador(self, ambassador_id: str) -> List[Dict[str, Any]]:
        """Busca comissões de um embaixador específico"""
        return self.get_by_field("ambassador_id", ambassador_id)


class CommissionInstallmentService(FirestoreService):
    """Serviço específico para parcelas de comissão"""
    
    def __init__(self):
        super().__init__("commission_installments")
    
    def get_by_indication(self, indication_id: str) -> List[Dict[str, Any]]:
        """Busca parcelas de uma indicação específica"""
        return self.get_by_field("indication_id", indication_id)
    
    def get_by_ambassador(self, ambassador_id: str) -> List[Dict[str, Any]]:
        """Busca parcelas de um embaixador específico"""
        return self.get_by_field("ambassador_id", ambassador_id)

