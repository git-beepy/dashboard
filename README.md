# Sistema Beepy - Indicações e Comissões

Sistema completo para gerenciamento de indicações e comissões de embaixadoras, desenvolvido com Flask (backend) e React (frontend).

## 🚀 Funcionalidades

- **Autenticação segura** com JWT
- **Dashboard administrativo** com métricas e relatórios
- **Dashboard de embaixadoras** com indicações pessoais
- **Gestão de usuários** (admin e embaixadoras)
- **Controle de indicações** com status de conversão
- **Sistema de comissões** com controle de pagamentos
- **Interface responsiva** e moderna

## 📋 Pré-requisitos

- Python 3.8+
- Node.js 16+
- npm ou yarn
- Conta no Firebase (para Firestore)

## 🛠️ Instalação

### Backend (Flask)

1. Navegue até a pasta do backend:
```bash
cd backend
```

2. Instale as dependências:
```bash
pip install -r requirements.txt
```

3. Configure o Firebase:
   - Coloque o arquivo de credenciais do Firebase (`projeto-beepy-firebase-adminsdk-fbsvc-45c41daaaf.json`) na pasta `backend/`
   - Certifique-se de que o Firestore está habilitado no seu projeto Firebase

4. Execute o servidor:
```bash
python main.py
```

O backend estará disponível em `http://localhost:10000`

### Frontend (React)

1. Navegue até a pasta do frontend:
```bash
cd frontend
```

2. Instale as dependências:
```bash
npm install
```

3. Configure as variáveis de ambiente:
   - Para desenvolvimento: arquivo `env` já está configurado
   - Para produção: edite o arquivo `env.production`

4. Execute o servidor de desenvolvimento:
```bash
npm run dev
```

O frontend estará disponível em `http://localhost:5173`

## 🔧 Configuração

### Variáveis de Ambiente

**Frontend (.env):**
```
VITE_API_BASE_URL=http://localhost:10000/api
```

**Frontend (env.production):**
```
VITE_API_BASE_URL=https://sua-api.com/api
```

### Credenciais Padrão

Para acessar o sistema pela primeira vez, use:
- **Email:** admin@beepy.com
- **Senha:** admin123

## 📚 Estrutura do Projeto

```
projeto-beepy/
├── backend/
│   ├── main.py                 # Aplicação Flask principal
│   ├── utils.py               # Utilitários e encoder JSON
│   ├── requirements.txt       # Dependências Python
│   └── projeto-beepy-firebase-adminsdk-*.json
├── frontend/
│   ├── src/
│   │   ├── components/        # Componentes React
│   │   ├── contexts/          # Context API (Auth)
│   │   └── main.jsx          # Ponto de entrada
│   ├── package.json          # Dependências Node.js
│   └── vite.config.js        # Configuração Vite
└── docs/                     # Documentação
```

## 🔄 API Endpoints

### Autenticação
- `POST /api/auth/login` - Login de usuário
- `POST /api/setup` - Criar usuário admin inicial

### Usuários
- `GET /api/users` - Listar usuários (admin)
- `POST /api/users` - Criar usuário (admin)
- `PUT /api/users/:id` - Atualizar usuário (admin)
- `DELETE /api/users/:id` - Deletar usuário (admin)

### Indicações
- `GET /api/indications` - Listar indicações
- `POST /api/indications` - Criar indicação
- `PUT /api/indications/:id` - Atualizar indicação
- `DELETE /api/indications/:id` - Deletar indicação

### Comissões
- `GET /api/commissions` - Listar comissões
- `POST /api/commissions` - Criar comissão
- `PUT /api/commissions/:id` - Atualizar comissão
- `DELETE /api/commissions/:id` - Deletar comissão

### Dashboard
- `GET /api/dashboard/admin` - Dashboard administrativo
- `GET /api/dashboard/embaixadora` - Dashboard da embaixadora

## 🚀 Deploy

### Backend (Render/Heroku)
1. Configure as variáveis de ambiente no serviço de deploy
2. Faça upload do arquivo de credenciais do Firebase
3. Use `gunicorn main:app` como comando de inicialização

### Frontend (Vercel/Netlify)
1. Configure a variável `VITE_API_BASE_URL` para a URL da API em produção
2. Execute `npm run build` para gerar os arquivos estáticos
3. Faça deploy da pasta `dist/`

## 🐛 Solução de Problemas

### Erro de Serialização JSON
- ✅ **Corrigido:** Implementado encoder JSON customizado para lidar com tipos datetime e Firestore

### Problemas de Login
- ✅ **Corrigido:** Melhorado tratamento de erros e interceptors do Axios
- Verifique se o backend está rodando na porta correta (10000)
- Verifique se as credenciais do Firebase estão corretas

### CORS
- ✅ **Corrigido:** CORS configurado para aceitar requisições do frontend

## 📝 Changelog

### v2.0 (Atual)
- ✅ Corrigido problema de serialização JSON com datetime
- ✅ Melhorado sistema de autenticação
- ✅ Adicionado tratamento robusto de erros
- ✅ Corrigida configuração de CORS
- ✅ Melhorada interface de login
- ✅ Adicionados interceptors para requisições HTTP

## 📄 Licença

Este projeto é propriedade privada. Todos os direitos reservados.

## 🤝 Suporte

Para suporte técnico, entre em contato através dos canais oficiais do projeto.

