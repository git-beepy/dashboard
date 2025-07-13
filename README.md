# Projeto Beepy - Sistema de Gestão de Indicações

## Visão Geral

O Beepy é um sistema completo de gestão de indicações e comissões para embaixadoras de marca. O projeto foi desenvolvido com React no frontend e integração completa com Firebase para autenticação e banco de dados em tempo real.

## Tecnologias Utilizadas

### Frontend
- **React 18.2.0** - Biblioteca principal para interface
- **Vite 5.4.19** - Build tool e servidor de desenvolvimento
- **React Router DOM 6.8.1** - Roteamento da aplicação
- **Recharts 2.5.0** - Biblioteca para gráficos e visualizações
- **Lucide React 0.263.1** - Ícones modernos
- **Axios 1.4.0** - Cliente HTTP para requisições

### Backend/Database
- **Firebase 9.0.0** - Plataforma completa do Google
  - **Firebase Authentication** - Sistema de autenticação
  - **Cloud Firestore** - Banco de dados NoSQL em tempo real
  - **Firebase Hosting** - Hospedagem (opcional)

### Estilização
- **Tailwind CSS** - Framework CSS utilitário
- **CSS Modules** - Estilos componentizados

## Funcionalidades Principais

### 1. Sistema de Autenticação
- Login/logout com Firebase Authentication
- Controle de acesso baseado em roles (admin/ambassador)
- Persistência de sessão
- Criação automática de perfis de usuário

### 2. Dashboard Administrativo
- Métricas em tempo real
- Gráficos interativos com dados do Firebase
- Visão geral de indicações e conversões
- Estatísticas de comissões

### 3. Gestão de Indicações
- Cadastro de novas indicações
- Listagem com filtros e busca
- Controle de status (pendente, convertida, perdida)
- Histórico completo de indicações

### 4. Sistema de Comissões
- Cálculo automático de comissões
- Controle de pagamentos
- Relatórios financeiros
- Status de comissões (pendente, paga)

### 5. Perfis de Usuário
- Gestão de embaixadoras
- Controle de permissões
- Histórico de atividades

## Estrutura do Projeto

```
projeto-beepy/
├── frontend/
│   ├── src/
│   │   ├── components/          # Componentes React
│   │   │   ├── Dashboard.jsx    # Dashboard principal
│   │   │   ├── Login.jsx        # Tela de login
│   │   │   ├── Indications.jsx  # Gestão de indicações
│   │   │   ├── Commissions.jsx  # Gestão de comissões
│   │   │   ├── Sidebar.jsx      # Menu lateral
│   │   │   └── ui/              # Componentes de UI
│   │   ├── contexts/            # Contextos React
│   │   │   └── AuthContext.jsx  # Contexto de autenticação
│   │   ├── services/            # Serviços e APIs
│   │   │   ├── firebase.js      # Serviços do Firebase
│   │   │   └── auth.js          # Serviços de autenticação
│   │   ├── utils/               # Utilitários
│   │   │   ├── populateFirebase.js  # Popular dados de exemplo
│   │   │   └── createAdminUser.js   # Criar usuários admin
│   │   ├── data/                # Dados de exemplo
│   │   │   └── sampleData.js    # Dados para popular Firebase
│   │   ├── firebase-config.js   # Configuração do Firebase
│   │   ├── App.jsx              # Componente principal
│   │   └── main.jsx             # Ponto de entrada
│   ├── public/                  # Arquivos públicos
│   ├── package.json             # Dependências do projeto
│   └── vite.config.js           # Configuração do Vite
└── README.md                    # Documentação
```

## Configuração e Instalação

### Pré-requisitos
- Node.js 18+ 
- npm ou yarn
- Conta no Firebase

### 1. Configuração do Firebase

1. Acesse o [Console do Firebase](https://console.firebase.google.com/)
2. Crie um novo projeto ou use o existente `projeto-beepy`
3. Ative os seguintes serviços:
   - **Authentication** (Email/Password)
   - **Cloud Firestore**
4. Obtenha as credenciais de configuração

### 2. Instalação do Projeto

```bash
# Clone o repositório
git clone <url-do-repositorio>
cd projeto-beepy

# Instale as dependências
cd frontend
npm install

# Configure as variáveis do Firebase
# As credenciais já estão configuradas em src/firebase-config.js
```

### 3. Executar o Projeto

```bash
# Inicie o servidor de desenvolvimento
npm run dev

# A aplicação estará disponível em http://localhost:3000
```

## Configuração Inicial dos Dados

### 1. Criar Usuário Administrador

Após iniciar a aplicação, abra o console do navegador e execute:

```javascript
// Criar usuário administrador
window.createAdminUser()

// Popular com dados de exemplo
window.populateFirebaseData()

// Ou fazer tudo de uma vez
window.setupFirebase()
```

### 2. Credenciais de Acesso

**Administrador:**
- Email: `admin@beepy.com`
- Senha: `admin123`

**Embaixadoras de Exemplo:**
- Email: `maria@beepy.com` / Senha: `maria123`
- Email: `ana@beepy.com` / Senha: `ana123`
- Email: `carla@beepy.com` / Senha: `carla123`

## Estrutura do Banco de Dados (Firestore)

### Coleções Principais

#### `users`
```javascript
{
  id: "user_id",
  name: "Nome do Usuário",
  email: "email@exemplo.com",
  role: "admin" | "ambassador",
  active: true,
  createdAt: timestamp,
  updatedAt: timestamp
}
```

#### `indications`
```javascript
{
  id: "indication_id",
  userId: "user_id",
  clientName: "Nome do Cliente",
  clientEmail: "cliente@exemplo.com",
  clientPhone: "(11) 99999-9999",
  origin: "Instagram" | "WhatsApp" | "Indicação",
  segment: "Residencial" | "Comercial",
  status: "pending" | "converted" | "lost",
  notes: "Observações",
  createdAt: timestamp,
  updatedAt: timestamp
}
```

#### `commissions`
```javascript
{
  id: "commission_id",
  userId: "user_id",
  indicationId: "indication_id",
  amount: 150.00,
  status: "pending" | "paid",
  dueDate: timestamp,
  paidDate: timestamp,
  createdAt: timestamp,
  updatedAt: timestamp
}
```

#### `dashboard_stats`
```javascript
{
  id: "general",
  totalIndications: 120,
  totalSales: 36,
  conversionRate: 30.0,
  totalCommissions: 6300.00,
  // ... outras estatísticas
  updatedAt: timestamp
}
```

## Scripts Disponíveis

```bash
# Desenvolvimento
npm run dev          # Inicia servidor de desenvolvimento

# Build
npm run build        # Gera build de produção
npm run preview      # Preview do build de produção

# Linting
npm run lint         # Executa ESLint
```

## Deploy

### Opção 1: Firebase Hosting

```bash
# Instalar Firebase CLI
npm install -g firebase-tools

# Login no Firebase
firebase login

# Inicializar projeto
firebase init hosting

# Build e deploy
npm run build
firebase deploy
```

### Opção 2: Vercel/Netlify

1. Conecte o repositório à plataforma
2. Configure o comando de build: `npm run build`
3. Configure o diretório de output: `dist`
4. Deploy automático

## Funcionalidades Implementadas

### ✅ Autenticação
- [x] Login com Firebase Auth
- [x] Logout funcional
- [x] Controle de acesso por roles
- [x] Persistência de sessão

### ✅ Dashboard
- [x] Métricas em tempo real
- [x] Gráficos com dados do Firebase
- [x] Interface responsiva
- [x] Dados reais (não mock)

### ✅ Indicações
- [x] Listagem de indicações
- [x] Cadastro de novas indicações
- [x] Edição e exclusão
- [x] Controle de status
- [x] Integração com Firebase

### ✅ Comissões
- [x] Listagem de comissões
- [x] Cálculo automático
- [x] Controle de pagamentos
- [x] Integração com Firebase

### ✅ Infraestrutura
- [x] Configuração do Firebase
- [x] Resolução de conflitos de dependências
- [x] Otimização de consultas
- [x] Tratamento de erros

## Melhorias Futuras

### Funcionalidades
- [ ] Sistema de notificações
- [ ] Relatórios em PDF
- [ ] Dashboard para embaixadoras
- [ ] Sistema de metas
- [ ] Integração com WhatsApp Business

### Técnicas
- [ ] Testes unitários
- [ ] Testes de integração
- [ ] PWA (Progressive Web App)
- [ ] Otimização de performance
- [ ] Monitoramento de erros

## Suporte e Manutenção

### Logs e Debugging
- Console do navegador para erros frontend
- Firebase Console para logs do backend
- Network tab para debugging de requisições

### Backup
- Dados automaticamente replicados no Firebase
- Export/import via Firebase CLI
- Backup automático do Firestore

## Contato

Para dúvidas ou suporte técnico, consulte a documentação do Firebase ou entre em contato com a equipe de desenvolvimento.

---

**Versão:** 1.0.0  
**Última atualização:** Julho 2025  
**Status:** Produção Ready ✅

