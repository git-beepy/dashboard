// Origens com emojis conforme especificado
export const ORIGINS = [
  {
    key: 'website',
    emoji: '🌐',
    name: 'Website',
    description: 'Leads vindos do site oficial'
  },
  {
    key: 'facebook',
    emoji: '📘',
    name: 'Facebook',
    description: 'Leads vindos do Facebook'
  },
  {
    key: 'instagram',
    emoji: '📷',
    name: 'Instagram',
    description: 'Leads vindos do Instagram'
  },
  {
    key: 'indicacao',
    emoji: '👥',
    name: 'Indicação',
    description: 'Leads vindos de indicações de clientes'
  },
  {
    key: 'fixo',
    emoji: '📞',
    name: 'Fixo',
    description: 'Leads vindos de telefone fixo'
  },
  {
    key: 'whatsapp',
    emoji: '💬',
    name: 'WhatsApp',
    description: 'Leads vindos do WhatsApp'
  },
  {
    key: 'google',
    emoji: '🔍',
    name: 'Google',
    description: 'Leads vindos de pesquisas no Google'
  },
  {
    key: 'outros',
    emoji: '📋',
    name: 'Outros',
    description: 'Outras origens não listadas'
  }
];

// Função para buscar origem por chave
export const getOriginByKey = (key) => {
  return ORIGINS.find(origin => origin.key === key) || ORIGINS.find(origin => origin.key === 'outros');
};

// Função para obter nome de exibição com emoji
export const getOriginDisplayName = (key) => {
  const origin = getOriginByKey(key);
  return `${origin.emoji} ${origin.name}`;
};

// Função para obter apenas o emoji
export const getOriginEmoji = (key) => {
  const origin = getOriginByKey(key);
  return origin.emoji;
};

// Função para obter lista de opções para select
export const getOriginOptions = () => {
  return ORIGINS.map(origin => ({
    value: origin.key,
    label: `${origin.emoji} ${origin.name}`,
    description: origin.description
  }));
};

