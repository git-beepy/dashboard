"""
Configuração e inicialização do Firebase Firestore
"""
import os
import json
import tempfile
from google.cloud import firestore
from typing import Optional


class FirebaseConfig:
    """Classe para gerenciar a configuração e conexão com Firebase"""
    
    def __init__(self):
        self._db: Optional[firestore.Client] = None
        self._initialize_firebase()
    
    def _initialize_firebase(self) -> None:
        """Inicializa a conexão com Firebase Firestore"""
        try:
            # Verificar se as credenciais estão configuradas via variável de ambiente
            creds = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
            
            if creds:
                # Se for uma string JSON, criar arquivo temporário
                if isinstance(creds, str) and creds.startswith("{"):
                    try:
                        # Validar se é JSON válido
                        json.loads(creds)
                        
                        # Criar arquivo temporário
                        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
                            f.write(creds)
                            temp_file = f.name
                        
                        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = temp_file
                        print("✅ Credenciais Firebase configuradas via variável de ambiente JSON")
                    except json.JSONDecodeError:
                        raise ValueError("GOOGLE_APPLICATION_CREDENTIALS não é um JSON válido")
                else:
                    print("✅ Credenciais Firebase configuradas via arquivo")
            
            # Inicializar cliente Firestore
            self._db = firestore.Client()
            print("✅ Firebase Firestore conectado com sucesso!")
            
        except Exception as e:
            print(f"❌ Erro ao conectar Firebase: {e}")
            self._db = None
            raise
    
    @property
    def db(self) -> Optional[firestore.Client]:
        """Retorna o cliente Firestore"""
        return self._db
    
    def is_connected(self) -> bool:
        """Verifica se a conexão com Firebase está ativa"""
        return self._db is not None


# Instância global do Firebase
firebase_config = FirebaseConfig()

