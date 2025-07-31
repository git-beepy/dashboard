from datetime import datetime
from typing import Dict, Any, Optional, List
import re

class BaseModel:
    """Classe base para todos os modelos"""
    
    def __init__(self, data: Dict[str, Any]):
        self.data = data
        self.created_at = data.get('createdAt', datetime.now())
        self.updated_at = data.get('updatedAt', datetime.now())
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte o modelo para dicionário"""
        return self.data
    
    def validate(self) -> List[str]:
        """Valida os dados do modelo. Retorna lista de erros."""
        return []

class UserModel(BaseModel):
    """Modelo para usuários (admin e embaixadoras)"""
    
    VALID_ROLES = ['admin', 'embaixadora']
    
    def __init__(self, data: Dict[str, Any]):
        super().__init__(data)
        self.email = data.get('email', '')
        self.name = data.get('name', '')
        self.role = data.get('role', 'embaixadora')
        self.phone = data.get('phone', '')
        self.active = data.get('active', True)
        self.password = data.get('password', '')
        self.last_active_at = data.get('lastActiveAt', datetime.now())
    
    def validate(self) -> List[str]:
        errors = []
        
        # Validar email
        if not self.email:
            errors.append("Email é obrigatório")
        elif not self._is_valid_email(self.email):
            errors.append("Email inválido")
        
        # Validar nome
        if not self.name or len(self.name.strip()) < 2:
            errors.append("Nome deve ter pelo menos 2 caracteres")
        
        # Validar role
        if self.role not in self.VALID_ROLES:
            errors.append(f"Role deve ser um dos seguintes: {', '.join(self.VALID_ROLES)}")
        
        # Validar senha (apenas para novos usuários)
        if self.password and len(self.password) < 6:
            errors.append("Senha deve ter pelo menos 6 caracteres")
        
        return errors
    
    def _is_valid_email(self, email: str) -> bool:
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'email': self.email,
            'name': self.name,
            'role': self.role,
            'phone': self.phone,
            'active': self.active,
            'createdAt': self.created_at,
            'updatedAt': self.updated_at,
            'lastActiveAt': self.last_active_at
        }

class IndicationModel(BaseModel):
    """Modelo para indicações"""
    
    VALID_STATUSES = ['agendado', 'aprovado', 'não aprovado']
    VALID_ORIGINS = ['website', 'facebook', 'instagram', 'indicacao', 'fixo', 'whatsapp', 'google', 'outros']
    VALID_SEGMENTS = [
        'saude', 'educacao_pesquisa', 'juridico', 'administracao_negocios',
        'engenharias', 'tecnologia_informacao', 'financeiro_bancario',
        'marketing_vendas_comunicacao', 'industria_producao', 'construcao_civil',
        'transportes_logistica', 'comercio_varejo', 'turismo_hotelaria_eventos',
        'gastronomia_alimentacao', 'agronegocio_meio_ambiente', 'artes_cultura_design',
        'midias_digitais_criativas', 'seguranca_defesa', 'servicos_gerais', 'outros'
    ]
    
    def __init__(self, data: Dict[str, Any]):
        super().__init__(data)
        self.client_name = data.get('client_name', '')
        self.email = data.get('email', '')
        self.phone = data.get('phone', '')
        self.origin = data.get('origin', 'website')
        self.segment = data.get('segment', 'outros')
        self.status = data.get('status', 'agendado')
        self.ambassador_id = data.get('ambassadorId', '')
        self.converted = data.get('converted', False)
        self.notes = data.get('notes', '')
    
    def validate(self) -> List[str]:
        errors = []
        
        # Validar nome do cliente
        if not self.client_name or len(self.client_name.strip()) < 2:
            errors.append("Nome do cliente deve ter pelo menos 2 caracteres")
        
        # Validar email
        if not self.email:
            errors.append("Email é obrigatório")
        elif not self._is_valid_email(self.email):
            errors.append("Email inválido")
        
        # Validar telefone
        if not self.phone:
            errors.append("Telefone é obrigatório")
        
        # Validar status
        if self.status not in self.VALID_STATUSES:
            errors.append(f"Status deve ser um dos seguintes: {', '.join(self.VALID_STATUSES)}")
        
        # Validar origem
        if self.origin not in self.VALID_ORIGINS:
            errors.append(f"Origem deve ser uma das seguintes: {', '.join(self.VALID_ORIGINS)}")
        
        # Validar segmento
        if self.segment not in self.VALID_SEGMENTS:
            errors.append(f"Segmento inválido")
        
        # Validar ambassador_id
        if not self.ambassador_id:
            errors.append("ID da embaixadora é obrigatório")
        
        return errors
    
    def _is_valid_email(self, email: str) -> bool:
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'client_name': self.client_name,
            'email': self.email,
            'phone': self.phone,
            'origin': self.origin,
            'segment': self.segment,
            'status': self.status,
            'ambassadorId': self.ambassador_id,
            'converted': self.converted,
            'notes': self.notes,
            'createdAt': self.created_at,
            'updatedAt': self.updated_at
        }

class CommissionModel(BaseModel):
    """Modelo para comissões"""
    
    VALID_STATUSES = ['pendente', 'pago', 'cancelado', 'em_analise']
    
    def __init__(self, data: Dict[str, Any]):
        super().__init__(data)
        self.ambassador_id = data.get('ambassadorId', '')
        self.ambassador_name = data.get('ambassadorName', '')
        self.indication_id = data.get('indicationId', '')
        self.client_name = data.get('clientName', '')
        self.value = data.get('value', 0.0)
        self.status = data.get('status', 'pendente')
        self.payment_date = data.get('paymentDate')
        self.notes = data.get('notes', '')
    
    def validate(self) -> List[str]:
        errors = []
        
        # Validar ambassador_id
        if not self.ambassador_id:
            errors.append("ID da embaixadora é obrigatório")
        
        # Validar indication_id
        if not self.indication_id:
            errors.append("ID da indicação é obrigatório")
        
        # Validar valor
        if not isinstance(self.value, (int, float)) or self.value < 0:
            errors.append("Valor deve ser um número positivo")
        
        # Validar status
        if self.status not in self.VALID_STATUSES:
            errors.append(f"Status deve ser um dos seguintes: {', '.join(self.VALID_STATUSES)}")
        
        # Validar nome do cliente
        if not self.client_name:
            errors.append("Nome do cliente é obrigatório")
        
        return errors
    
    def to_dict(self) -> Dict[str, Any]:
        result = {
            'ambassadorId': self.ambassador_id,
            'ambassadorName': self.ambassador_name,
            'indicationId': self.indication_id,
            'clientName': self.client_name,
            'value': self.value,
            'status': self.status,
            'notes': self.notes,
            'createdAt': self.created_at,
            'updatedAt': self.updated_at
        }
        
        if self.payment_date:
            result['paymentDate'] = self.payment_date
        
        return result

# Mapeamento de segmentos com emojis e nomes amigáveis
SEGMENTS_MAP = {
    'saude': {
        'emoji': '🏥',
        'name': 'Saúde',
        'description': 'Medicina, Enfermagem, Odontologia, Psicologia, etc.'
    },
    'educacao_pesquisa': {
        'emoji': '🧠',
        'name': 'Educação e Pesquisa',
        'description': 'Professores, Pedagogia, Pesquisa Científica, etc.'
    },
    'juridico': {
        'emoji': '🏛️',
        'name': 'Jurídico',
        'description': 'Direito Civil, Penal, Trabalhista, Advocacia, etc.'
    },
    'administracao_negocios': {
        'emoji': '💼',
        'name': 'Administração e Negócios',
        'description': 'Administração, RH, Contabilidade, Financeiro, etc.'
    },
    'engenharias': {
        'emoji': '🏢',
        'name': 'Engenharias',
        'description': 'Engenharia Civil, Mecânica, Elétrica, etc.'
    },
    'tecnologia_informacao': {
        'emoji': '💻',
        'name': 'Tecnologia da Informação',
        'description': 'Desenvolvimento, Suporte, Redes, Segurança, etc.'
    },
    'financeiro_bancario': {
        'emoji': '🏦',
        'name': 'Financeiro e Bancário',
        'description': 'Bancário, Investimentos, Seguros, etc.'
    },
    'marketing_vendas_comunicacao': {
        'emoji': '📣',
        'name': 'Marketing, Vendas e Comunicação',
        'description': 'Marketing Digital, Vendas, Publicidade, etc.'
    },
    'industria_producao': {
        'emoji': '🏭',
        'name': 'Indústria e Produção',
        'description': 'Produção Industrial, Controle de Qualidade, etc.'
    },
    'construcao_civil': {
        'emoji': '🧱',
        'name': 'Construção Civil',
        'description': 'Mestre de Obras, Arquitetura, Design de Interiores, etc.'
    },
    'transportes_logistica': {
        'emoji': '🚛',
        'name': 'Transportes e Logística',
        'description': 'Motorista, Logística, Estoque, etc.'
    },
    'comercio_varejo': {
        'emoji': '🛒',
        'name': 'Comércio e Varejo',
        'description': 'Atendente, Vendedor, E-commerce, etc.'
    },
    'turismo_hotelaria_eventos': {
        'emoji': '🏨',
        'name': 'Turismo, Hotelaria e Eventos',
        'description': 'Recepção, Guia de Turismo, Eventos, etc.'
    },
    'gastronomia_alimentacao': {
        'emoji': '🍳',
        'name': 'Gastronomia e Alimentação',
        'description': 'Cozinheiro, Chef, Confeiteiro, etc.'
    },
    'agronegocio_meio_ambiente': {
        'emoji': '🌱',
        'name': 'Agronegócio e Meio Ambiente',
        'description': 'Agronomia, Veterinária, Gestão Ambiental, etc.'
    },
    'artes_cultura_design': {
        'emoji': '🎭',
        'name': 'Artes, Cultura e Design',
        'description': 'Artes Visuais, Design Gráfico, Fotografia, etc.'
    },
    'midias_digitais_criativas': {
        'emoji': '📱',
        'name': 'Mídias Digitais e Criativas',
        'description': 'Influenciador, Edição de Vídeo, Streaming, etc.'
    },
    'seguranca_defesa': {
        'emoji': '👮',
        'name': 'Segurança e Defesa',
        'description': 'Polícia, Bombeiro, Segurança Privada, etc.'
    },
    'servicos_gerais': {
        'emoji': '🧹',
        'name': 'Serviços Gerais',
        'description': 'Limpeza, Portaria, Manutenção, etc.'
    },
    'outros': {
        'emoji': '📋',
        'name': 'Outros',
        'description': 'Outros segmentos não listados'
    }
}

# Mapeamento de origens com emojis
ORIGINS_MAP = {
    'website': {
        'emoji': '🌐',
        'name': 'Website'
    },
    'facebook': {
        'emoji': '📘',
        'name': 'Facebook'
    },
    'instagram': {
        'emoji': '📷',
        'name': 'Instagram'
    },
    'indicacao': {
        'emoji': '👥',
        'name': 'Indicação'
    },
    'fixo': {
        'emoji': '📞',
        'name': 'Fixo'
    },
    'whatsapp': {
        'emoji': '💬',
        'name': 'WhatsApp'
    },
    'google': {
        'emoji': '🔍',
        'name': 'Google'
    },
    'outros': {
        'emoji': '📋',
        'name': 'Outros'
    }
}

def get_segment_display_name(segment_key: str) -> str:
    """Retorna o nome de exibição do segmento com emoji"""
    segment_info = SEGMENTS_MAP.get(segment_key, SEGMENTS_MAP['outros'])
    return f"{segment_info['emoji']} {segment_info['name']}"

def get_origin_display_name(origin_key: str) -> str:
    """Retorna o nome de exibição da origem com emoji"""
    origin_info = ORIGINS_MAP.get(origin_key, ORIGINS_MAP['outros'])
    return f"{origin_info['emoji']} {origin_info['name']}"

def validate_model_data(model_class, data: Dict[str, Any]) -> tuple[bool, List[str]]:
    """Valida dados usando o modelo especificado"""
    try:
        model = model_class(data)
        errors = model.validate()
        return len(errors) == 0, errors
    except Exception as e:
        return False, [f"Erro na validação: {str(e)}"]

