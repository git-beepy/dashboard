// Segmentos com emojis conforme especificado
export const SEGMENTS = [
  {
    key: 'saude',
    emoji: '🏥',
    name: 'Saúde',
    description: 'Medicina, Enfermagem, Odontologia, Psicologia, etc.'
  },
  {
    key: 'educacao_pesquisa',
    emoji: '🧠',
    name: 'Educação e Pesquisa',
    description: 'Professores, Pedagogia, Pesquisa Científica, etc.'
  },
  {
    key: 'juridico',
    emoji: '🏛️',
    name: 'Jurídico',
    description: 'Direito Civil, Penal, Trabalhista, Advocacia, etc.'
  },
  {
    key: 'administracao_negocios',
    emoji: '💼',
    name: 'Administração e Negócios',
    description: 'Administração, RH, Contabilidade, Financeiro, etc.'
  },
  {
    key: 'engenharias',
    emoji: '🏢',
    name: 'Engenharias',
    description: 'Engenharia Civil, Mecânica, Elétrica, etc.'
  },
  {
    key: 'tecnologia_informacao',
    emoji: '💻',
    name: 'Tecnologia da Informação',
    description: 'Desenvolvimento, Suporte, Redes, Segurança, etc.'
  },
  {
    key: 'financeiro_bancario',
    emoji: '🏦',
    name: 'Financeiro e Bancário',
    description: 'Bancário, Investimentos, Seguros, etc.'
  },
  {
    key: 'marketing_vendas_comunicacao',
    emoji: '📣',
    name: 'Marketing, Vendas e Comunicação',
    description: 'Marketing Digital, Vendas, Publicidade, etc.'
  },
  {
    key: 'industria_producao',
    emoji: '🏭',
    name: 'Indústria e Produção',
    description: 'Produção Industrial, Controle de Qualidade, etc.'
  },
  {
    key: 'construcao_civil',
    emoji: '🧱',
    name: 'Construção Civil',
    description: 'Mestre de Obras, Arquitetura, Design de Interiores, etc.'
  },
  {
    key: 'transportes_logistica',
    emoji: '🚛',
    name: 'Transportes e Logística',
    description: 'Motorista, Logística, Estoque, etc.'
  },
  {
    key: 'comercio_varejo',
    emoji: '🛒',
    name: 'Comércio e Varejo',
    description: 'Atendente, Vendedor, E-commerce, etc.'
  },
  {
    key: 'turismo_hotelaria_eventos',
    emoji: '🏨',
    name: 'Turismo, Hotelaria e Eventos',
    description: 'Recepção, Guia de Turismo, Eventos, etc.'
  },
  {
    key: 'gastronomia_alimentacao',
    emoji: '🍳',
    name: 'Gastronomia e Alimentação',
    description: 'Cozinheiro, Chef, Confeiteiro, etc.'
  },
  {
    key: 'agronegocio_meio_ambiente',
    emoji: '🌱',
    name: 'Agronegócio e Meio Ambiente',
    description: 'Agronomia, Veterinária, Gestão Ambiental, etc.'
  },
  {
    key: 'artes_cultura_design',
    emoji: '🎭',
    name: 'Artes, Cultura e Design',
    description: 'Artes Visuais, Design Gráfico, Fotografia, etc.'
  },
  {
    key: 'midias_digitais_criativas',
    emoji: '📱',
    name: 'Mídias Digitais e Criativas',
    description: 'Influenciador, Edição de Vídeo, Streaming, etc.'
  },
  {
    key: 'seguranca_defesa',
    emoji: '👮',
    name: 'Segurança e Defesa',
    description: 'Polícia, Bombeiro, Segurança Privada, etc.'
  },
  {
    key: 'servicos_gerais',
    emoji: '🧹',
    name: 'Serviços Gerais',
    description: 'Limpeza, Portaria, Manutenção, etc.'
  },
  {
    key: 'outros',
    emoji: '📋',
    name: 'Outros',
    description: 'Outros segmentos não listados'
  }
];

// Função para buscar segmento por chave
export const getSegmentByKey = (key) => {
  return SEGMENTS.find(segment => segment.key === key) || SEGMENTS.find(segment => segment.key === 'outros');
};

// Função para obter nome de exibição com emoji
export const getSegmentDisplayName = (key) => {
  const segment = getSegmentByKey(key);
  return `${segment.emoji} ${segment.name}`;
};

// Função para obter apenas o emoji
export const getSegmentEmoji = (key) => {
  const segment = getSegmentByKey(key);
  return segment.emoji;
};

// Função para obter lista de opções para select
export const getSegmentOptions = () => {
  return SEGMENTS.map(segment => ({
    value: segment.key,
    label: `${segment.emoji} ${segment.name}`,
    description: segment.description
  }));
};

