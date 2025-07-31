# Sistema Beepy - Indicações e Comissões de Embaixadoras

## Visão Geral

O Sistema Beepy é uma plataforma web completa para gerenciar indicações feitas por embaixadoras, acompanhar vendas geradas e controlar o pagamento de comissões. A plataforma oferece dois tipos de usuários distintos: Embaixadoras e Administradores (Agência).

## URLs de Acesso

- **Frontend (Sistema Web)**: https://agsiente.manus.space
- **Backend (API)**: https://ogh5izcv9dg9.manus.space

## Funcionalidades Principais

### 👩‍💼 Painel da Embaixadora

- **Dashboard Personalizado**: Visualização de métricas pessoais
  - Total de indicações realizadas
  - Total de vendas aprovadas
  - Comissão a receber no mês atual
  - Taxa de conversão pessoal

- **Nova Indicação**: Formulário para cadastrar novos clientes
  - Nome do cliente
  - Informações de contato
  - Nicho/segmento do cliente
  - Observações adicionais

- **Histórico de Indicações**: Lista completa com status
  - Agendado (indicação criada, aguardando contato)
  - Aprovado (venda fechada)
  - Não aprovado (venda não realizada)

- **Gráficos e Análises**:
  - Evolução de comissões mês a mês
  - Distribuição de indicações por segmento
  - Acompanhamento de performance

### 🧑‍💻 Painel da Agência (Admin)

- **Dashboard Executivo**: Visão geral do negócio
  - Total de indicações no sistema
  - Total de vendas fechadas
  - Taxa de conversão geral
  - Número de embaixadoras ativas
  - Comissões a pagar no mês

- **Gestão de Indicações**:
  - Visualização de todas as indicações
  - Atualização de status (agendado → aprovado/não aprovado)
  - Filtros por embaixadora, data e status

- **Gestão de Comissões**:
  - Controle de parcelas (1ª, 2ª, 3ª)
  - Marcação de parcelas como pagas
  - Relatórios de pagamentos

- **Análises Avançadas**:
  - Gráficos de evolução mensal
  - Taxa de conversão por segmento
  - Ranking de embaixadoras
  - Origem dos leads

## Sistema de Comissões

### Regras de Pagamento
- **Valor por venda**: R$ 900,00 (dividido em 3 parcelas de R$ 300,00)
- **1ª parcela**: Paga no mês da aprovação da venda
- **2ª parcela**: Paga 30 dias após a aprovação
- **3ª parcela**: Paga 60 dias após a aprovação

### Controle Automático
- Geração automática das datas de vencimento
- Cálculo automático de comissões por mês
- Status de pagamento por parcela

## Tecnologias Utilizadas

### Frontend
- **React 18** com Vite
- **Tailwind CSS** para estilização
- **Shadcn/UI** para componentes
- **Recharts** para gráficos e visualizações
- **Lucide React** para ícones

### Backend
- **Flask** (Python)
- **SQLAlchemy** para ORM
- **SQLite** como banco de dados
- **Flask-CORS** para integração frontend/backend

### Deploy
- **Frontend**: Hospedado na Manus Cloud
- **Backend**: API REST hospedada na Manus Cloud

## Estrutura do Projeto

```
beepy-system/
├── frontend/
│   └── beepy-frontend/          # Aplicação React
│       ├── src/
│       │   ├── components/      # Componentes React
│       │   │   ├── MockDashboard.jsx
│       │   │   ├── Login.jsx
│       │   │   ├── Layout.jsx
│       │   │   ├── AmbassadorDashboard.jsx
│       │   │   └── AdminDashboard.jsx
│       │   ├── contexts/        # Contextos React
│       │   └── App.jsx
│       └── dist/               # Build de produção
└── backend/
    └── beepy-backend/          # API Flask
        ├── src/
        │   ├── models/         # Modelos de dados
        │   │   ├── user.py
        │   │   ├── indication.py
        │   │   └── commission.py
        │   ├── routes/         # Rotas da API
        │   │   ├── auth.py
        │   │   ├── indications.py
        │   │   ├── commissions.py
        │   │   └── dashboard.py
        │   └── main.py         # Aplicação principal
        └── requirements.txt
```

## Modelos de Dados

### User (Usuário)
- `id`: Identificador único
- `email`: Email do usuário
- `name`: Nome completo
- `user_type`: Tipo ('embaixadora' ou 'admin')
- `created_at`: Data de criação

### Indication (Indicação)
- `id`: Identificador único
- `ambassador_id`: ID da embaixadora
- `client_name`: Nome do cliente
- `client_contact`: Contato do cliente
- `niche`: Nicho/segmento
- `observations`: Observações
- `status`: Status ('agendado', 'aprovado', 'não aprovado')
- `sale_approval_date`: Data de aprovação da venda
- `created_at`: Data de criação

### Commission (Comissão)
- `id`: Identificador único
- `indication_id`: ID da indicação
- `ambassador_id`: ID da embaixadora
- `parcel_number`: Número da parcela (1, 2 ou 3)
- `amount`: Valor da parcela (R$ 300,00)
- `due_date`: Data de vencimento
- `payment_status`: Status ('pendente' ou 'pago')
- `created_at`: Data de criação

## Como Usar

### Para Embaixadoras
1. Acesse o sistema através do link: https://agsiente.manus.space
2. O sistema já está configurado com dados de demonstração
3. Use o botão "Nova Indicação" para cadastrar clientes
4. Acompanhe suas métricas no dashboard
5. Visualize o histórico de indicações e comissões

### Para Administradores
1. Acesse o sistema e clique em "Trocar para Admin"
2. Visualize métricas gerais no dashboard
3. Gerencie indicações alterando status
4. Controle pagamentos de comissões
5. Analise relatórios e gráficos

## Dados de Demonstração

O sistema inclui dados de teste pré-configurados:

### Usuários
- **Embaixadora**: Mariana Lopes (mariana@teste.com)
- **Embaixadora**: Julia Santos (julia@teste.com)
- **Admin**: Admin Beepy (admin@beepy.com)

### Indicações de Exemplo
- Studio Shodwe (Agendado)
- Borcelle (Aprovado - R$ 900,50)
- Fauget (Não Aprovado)
- Larana, Inc. (Não Aprovado)
- Ótica Vision (Aprovado)

## Características Técnicas

### Responsividade
- Interface adaptável para desktop e mobile
- Design otimizado para diferentes tamanhos de tela
- Navegação touch-friendly

### Performance
- Carregamento rápido com build otimizado
- Gráficos interativos e responsivos
- Interface fluida e intuitiva

### Segurança
- Separação clara entre perfis de usuário
- Validação de dados no frontend e backend
- APIs RESTful bem estruturadas

## Próximos Passos

Para evolução do sistema, considere:

1. **Autenticação Real**: Implementar login com senha e JWT
2. **Notificações**: Sistema de emails automáticos
3. **Relatórios**: Exportação de dados em PDF/Excel
4. **Filtros Avançados**: Busca e filtros mais robustos
5. **Dashboard Mobile**: App nativo para smartphones
6. **Integração de Pagamento**: Conexão com gateways de pagamento
7. **Backup Automático**: Sistema de backup dos dados

## Suporte

Para dúvidas ou suporte técnico, entre em contato através dos canais oficiais da Beepy.

---

**Sistema desenvolvido com tecnologias modernas e foco na experiência do usuário.**

