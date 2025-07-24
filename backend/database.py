import os
import json
import tempfile
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple
from google.cloud import firestore
from google.cloud.firestore_v1.base_query import FieldFilter
from models import UserModel, IndicationModel, CommissionModel, validate_model_data

class DatabaseManager:
    """Gerenciador centralizado do banco de dados Firestore"""
    
    def __init__(self):
        self.db = None
        self._initialize_firestore()
    
    def _initialize_firestore(self):
        """Inicializa a conexão com o Firestore"""
        try:
            # Tentar usar credenciais do ambiente primeiro
            if os.environ.get("GOOGLE_APPLICATION_CREDENTIALS"):
                creds = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
                if isinstance(creds, str) and creds.startswith("{"):
                    # Se for string JSON, criar arquivo temporário
                    try:
                        json.loads(creds)
                        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
                            f.write(creds)
                            temp_file = f.name
                        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = temp_file
                        print("Credenciais Firebase configuradas via variável de ambiente")
                    except json.JSONDecodeError:
                        print("Erro: GOOGLE_APPLICATION_CREDENTIALS não é um JSON válido")

            self.db = firestore.Client()
            print("Firebase conectado com sucesso!")
            
        except Exception as e:
            print(f"Erro ao conectar Firebase: {e}")
            # Tentar usar arquivo local como fallback
            try:
                local_creds_path = "projeto-beepy-firebase-adminsdk-fbsvc-45c41daaaf.json"
                if os.path.exists(local_creds_path):
                    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = local_creds_path
                    self.db = firestore.Client()
                    print("Firebase conectado com arquivo local!")
                else:
                    print("Arquivo de credenciais local não encontrado")
            except Exception as e:
                print(f"Erro no fallback Firebase: {e}")
                self.db = None
    
    def is_connected(self) -> bool:
        """Verifica se a conexão com o banco está ativa"""
        return self.db is not None
    
    # Operações genéricas CRUD
    def create_document(self, collection: str, data: Dict[str, Any], model_class=None) -> Tuple[bool, str, Optional[str]]:
        """
        Cria um novo documento na coleção especificada
        Retorna: (sucesso, mensagem, document_id)
        """
        if not self.is_connected():
            return False, "Erro de conexão com banco de dados", None
        
        try:
            # Validar dados se modelo fornecido
            if model_class:
                is_valid, errors = validate_model_data(model_class, data)
                if not is_valid:
                    return False, f"Dados inválidos: {'; '.join(errors)}", None
            
            # Adicionar timestamps
            data['createdAt'] = datetime.now()
            data['updatedAt'] = datetime.now()
            
            # Criar documento
            doc_ref = self.db.collection(collection).add(data)
            document_id = doc_ref[1].id
            
            print(f"Documento criado na coleção '{collection}' com ID: {document_id}")
            return True, "Documento criado com sucesso", document_id
            
        except Exception as e:
            error_msg = f"Erro ao criar documento: {str(e)}"
            print(error_msg)
            return False, error_msg, None
    
    def get_document(self, collection: str, document_id: str) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
        """
        Busca um documento específico
        Retorna: (sucesso, mensagem, dados)
        """
        if not self.is_connected():
            return False, "Erro de conexão com banco de dados", None
        
        try:
            doc_ref = self.db.collection(collection).document(document_id)
            doc = doc_ref.get()
            
            if doc.exists:
                data = doc.to_dict()
                data['id'] = doc.id
                return True, "Documento encontrado", data
            else:
                return False, "Documento não encontrado", None
                
        except Exception as e:
            error_msg = f"Erro ao buscar documento: {str(e)}"
            print(error_msg)
            return False, error_msg, None
    
    def get_collection(self, collection: str, filters: List[Tuple[str, str, Any]] = None, 
                      order_by: str = None, limit: int = None) -> Tuple[bool, str, List[Dict[str, Any]]]:
        """
        Busca documentos de uma coleção com filtros opcionais
        Retorna: (sucesso, mensagem, lista_de_dados)
        """
        if not self.is_connected():
            return False, "Erro de conexão com banco de dados", []
        
        try:
            query = self.db.collection(collection)
            
            # Aplicar filtros
            if filters:
                for field, operator, value in filters:
                    query = query.where(field_path=field, op_string=operator, value=value)
            
            # Aplicar ordenação
            if order_by:
                query = query.order_by(order_by)
            
            # Aplicar limite
            if limit:
                query = query.limit(limit)
            
            # Executar query
            docs = query.stream()
            results = []
            
            for doc in docs:
                data = doc.to_dict()
                data['id'] = doc.id
                results.append(data)
            
            return True, f"Encontrados {len(results)} documentos", results
            
        except Exception as e:
            error_msg = f"Erro ao buscar coleção: {str(e)}"
            print(error_msg)
            return False, error_msg, []
    
    def update_document(self, collection: str, document_id: str, 
                       update_data: Dict[str, Any], model_class=None) -> Tuple[bool, str]:
        """
        Atualiza um documento existente
        Retorna: (sucesso, mensagem)
        """
        if not self.is_connected():
            return False, "Erro de conexão com banco de dados"
        
        try:
            # Buscar documento atual para validação completa se necessário
            if model_class:
                success, msg, current_data = self.get_document(collection, document_id)
                if not success:
                    return False, f"Documento não encontrado: {msg}"
                
                # Mesclar dados atuais com atualizações
                merged_data = {**current_data, **update_data}
                is_valid, errors = validate_model_data(model_class, merged_data)
                if not is_valid:
                    return False, f"Dados inválidos: {'; '.join(errors)}"
            
            # Adicionar timestamp de atualização
            update_data['updatedAt'] = datetime.now()
            
            # Atualizar documento
            doc_ref = self.db.collection(collection).document(document_id)
            doc_ref.update(update_data)
            
            print(f"Documento {document_id} atualizado na coleção '{collection}'")
            return True, "Documento atualizado com sucesso"
            
        except Exception as e:
            error_msg = f"Erro ao atualizar documento: {str(e)}"
            print(error_msg)
            return False, error_msg
    
    def delete_document(self, collection: str, document_id: str) -> Tuple[bool, str]:
        """
        Exclui um documento
        Retorna: (sucesso, mensagem)
        """
        if not self.is_connected():
            return False, "Erro de conexão com banco de dados"
        
        try:
            doc_ref = self.db.collection(collection).document(document_id)
            doc_ref.delete()
            
            print(f"Documento {document_id} excluído da coleção '{collection}'")
            return True, "Documento excluído com sucesso"
            
        except Exception as e:
            error_msg = f"Erro ao excluir documento: {str(e)}"
            print(error_msg)
            return False, error_msg
    
    # Operações específicas para usuários
    def create_user(self, user_data: Dict[str, Any]) -> Tuple[bool, str, Optional[str]]:
        """Cria um novo usuário"""
        return self.create_document('users', user_data, UserModel)
    
    def get_user_by_email(self, email: str) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
        """Busca usuário por email"""
        success, msg, users = self.get_collection('users', [('email', '==', email)], limit=1)
        if success and users:
            return True, "Usuário encontrado", users[0]
        return False, "Usuário não encontrado", None
    
    def get_users_by_role(self, role: str) -> Tuple[bool, str, List[Dict[str, Any]]]:
        """Busca usuários por role"""
        return self.get_collection('users', [('role', '==', role)])
    
    def update_user_last_active(self, user_id: str) -> Tuple[bool, str]:
        """Atualiza último acesso do usuário"""
        return self.update_document('users', user_id, {'lastActiveAt': datetime.now()})
    
    # Operações específicas para indicações
    def create_indication(self, indication_data: Dict[str, Any]) -> Tuple[bool, str, Optional[str]]:
        """Cria uma nova indicação"""
        return self.create_document('indications', indication_data, IndicationModel)
    
    def get_indications_by_ambassador(self, ambassador_id: str) -> Tuple[bool, str, List[Dict[str, Any]]]:
        """Busca indicações de uma embaixadora específica"""
        return self.get_collection('indications', [('ambassadorId', '==', ambassador_id)], 
                                 order_by='createdAt')
    
    def get_indications_by_status(self, status: str) -> Tuple[bool, str, List[Dict[str, Any]]]:
        """Busca indicações por status"""
        return self.get_collection('indications', [('status', '==', status)])
    
    def update_indication_status(self, indication_id: str, new_status: str) -> Tuple[bool, str]:
        """Atualiza status de uma indicação"""
        if new_status not in IndicationModel.VALID_STATUSES:
            return False, f"Status inválido. Use: {', '.join(IndicationModel.VALID_STATUSES)}"
        
        return self.update_document('indications', indication_id, {'status': new_status})
    
    # Operações específicas para comissões
    def create_commission(self, commission_data: Dict[str, Any]) -> Tuple[bool, str, Optional[str]]:
        """Cria uma nova comissão"""
        return self.create_document('commissions', commission_data, CommissionModel)
    
    def get_commissions_by_ambassador(self, ambassador_id: str) -> Tuple[bool, str, List[Dict[str, Any]]]:
        """Busca comissões de uma embaixadora específica"""
        return self.get_collection('commissions', [('ambassadorId', '==', ambassador_id)], 
                                 order_by='createdAt')
    
    def get_commissions_by_indication(self, indication_id: str) -> Tuple[bool, str, List[Dict[str, Any]]]:
        """Busca comissões relacionadas a uma indicação"""
        return self.get_collection('commissions', [('indicationId', '==', indication_id)])
    
    def update_commission_status(self, commission_id: str, new_status: str) -> Tuple[bool, str]:
        """Atualiza status de uma comissão"""
        if new_status not in CommissionModel.VALID_STATUSES:
            return False, f"Status inválido. Use: {', '.join(CommissionModel.VALID_STATUSES)}"
        
        update_data = {'status': new_status}
        if new_status == 'pago':
            update_data['paymentDate'] = datetime.now()
        
        return self.update_document('commissions', commission_id, update_data)
    
    # Operações de sincronização
    def sync_indication_commission_status(self, indication_id: str, indication_status: str) -> Tuple[bool, str]:
        """Sincroniza status entre indicação e comissões relacionadas"""
        try:
            # Buscar comissões relacionadas
            success, msg, commissions = self.get_commissions_by_indication(indication_id)
            if not success:
                return False, f"Erro ao buscar comissões: {msg}"
            
            # Determinar novo status da comissão baseado no status da indicação
            if indication_status == "aprovado":
                new_commission_status = "pendente"
            elif indication_status == "não aprovado":
                new_commission_status = "cancelado"
            else:
                new_commission_status = "em_analise"
            
            # Atualizar todas as comissões relacionadas
            updated_count = 0
            for commission in commissions:
                success, msg = self.update_commission_status(commission['id'], new_commission_status)
                if success:
                    updated_count += 1
                else:
                    print(f"Erro ao atualizar comissão {commission['id']}: {msg}")
            
            return True, f"{updated_count} comissões sincronizadas"
            
        except Exception as e:
            error_msg = f"Erro na sincronização: {str(e)}"
            print(error_msg)
            return False, error_msg
    
    # Operações de estatísticas
    def get_dashboard_stats(self, user_id: str = None, is_admin: bool = False) -> Tuple[bool, str, Dict[str, Any]]:
        """Gera estatísticas para o dashboard"""
        try:
            stats = {}
            
            if is_admin:
                # Estatísticas para admin (todos os dados)
                success, msg, all_indications = self.get_collection('indications')
                if success:
                    stats['totalIndications'] = len(all_indications)
                    stats['approvedIndications'] = len([i for i in all_indications if i.get('status') == 'aprovado'])
                    stats['pendingIndications'] = len([i for i in all_indications if i.get('status') == 'agendado'])
                    stats['rejectedIndications'] = len([i for i in all_indications if i.get('status') == 'não aprovado'])
                    stats['approvalRate'] = (stats['approvedIndications'] / stats['totalIndications'] * 100) if stats['totalIndications'] > 0 else 0
                
                success, msg, all_commissions = self.get_collection('commissions')
                if success:
                    stats['totalCommissions'] = sum(c.get('value', 0) for c in all_commissions)
                    stats['paidCommissions'] = len([c for c in all_commissions if c.get('status') == 'pago'])
                    stats['pendingCommissions'] = len([c for c in all_commissions if c.get('status') == 'pendente'])
                    
                    # Comissões do mês atual
                    current_month = datetime.now().month
                    current_year = datetime.now().year
                    monthly_commissions = 0
                    for commission in all_commissions:
                        created_at = commission.get('createdAt')
                        if created_at and created_at.month == current_month and created_at.year == current_year:
                            monthly_commissions += commission.get('value', 0)
                    stats['monthlyCommissions'] = monthly_commissions
                
                success, msg, ambassadors = self.get_users_by_role('embaixadora')
                if success:
                    stats['totalAmbassadors'] = len(ambassadors)
                    # Calcular embaixadoras ativas (com indicações nos últimos 60 dias)
                    # Implementação simplificada
                    stats['activeAmbassadors'] = len(ambassadors)  # Placeholder
                    stats['activePercentage'] = 100  # Placeholder
            
            else:
                # Estatísticas para embaixadora (apenas seus dados)
                success, msg, user_indications = self.get_indications_by_ambassador(user_id)
                if success:
                    stats['totalIndications'] = len(user_indications)
                    stats['approvedIndications'] = len([i for i in user_indications if i.get('status') == 'aprovado'])
                    stats['pendingIndications'] = len([i for i in user_indications if i.get('status') == 'agendado'])
                    stats['rejectedIndications'] = len([i for i in user_indications if i.get('status') == 'não aprovado'])
                    stats['conversionRate'] = (stats['approvedIndications'] / stats['totalIndications'] * 100) if stats['totalIndications'] > 0 else 0
                    stats['convertedIndications'] = len([i for i in user_indications if i.get('converted', False)])
                
                success, msg, user_commissions = self.get_commissions_by_ambassador(user_id)
                if success:
                    stats['totalCommissions'] = sum(c.get('value', 0) for c in user_commissions)
                    stats['paidCommissions'] = len([c for c in user_commissions if c.get('status') == 'pago'])
                    stats['pendingCommissions'] = len([c for c in user_commissions if c.get('status') == 'pendente'])
                    
                    # Comissões do mês atual
                    current_month = datetime.now().month
                    current_year = datetime.now().year
                    monthly_commission = 0
                    for commission in user_commissions:
                        created_at = commission.get('createdAt')
                        if created_at and created_at.month == current_month and created_at.year == current_year:
                            monthly_commission += commission.get('value', 0)
                    stats['monthlyCommission'] = monthly_commission
            
            return True, "Estatísticas geradas com sucesso", stats
            
        except Exception as e:
            error_msg = f"Erro ao gerar estatísticas: {str(e)}"
            print(error_msg)
            return False, error_msg, {}

# Instância global do gerenciador de banco
db_manager = DatabaseManager()

