# Sistema Beepy - Indicações e Comissões

Sistema completo para gerenciamento de indicações e comissões de embaixadoras, desenvolvido com React (frontend) e Flask (backend), utilizando Firebase Firestore como banco de dados.

## 🚀 Funcionalidades

### Para Administradores
- Dashboard com estatísticas gerais
- Gerenciamento de usuários (embaixadoras)
- Visualização de todas as indicações
- Controle de comissões
- Relatórios e métricas

### Para Embaixadoras
- Dashboard personalizado
- Cadastro de indicações
- Acompanhamento de conversões
- Visualização de comissões
- Histórico de atividades

## 🛠️ Tecnologias Utilizadas

### Frontend
- React 18
- Vite
- Tailwind CSS
- Lucide React (ícones)
- Axios (requisições HTTP)
- React Router (navegação)

### Backend
- Flask 3.0.3
- Flask-CORS
- Flask-JWT-Extended
- Firebase Admin SDK
- bcrypt (criptografia de senhas)
- Gunicorn (servidor WSGI)

### Banco de Dados
- Firebase Firestore

## 📦 Estrutura do Projeto

```
projeto-beepy-unificado/
├── backend/
│   ├── main.py                 # Aplicação Flask principal
│   ├── utils.py               # Utilitários e helpers
│   ├── create_admin.py        # Script para criar admin
│   ├── requirements.txt       # Dependências Python
│   ├── render.yaml           # Configuração Render
│   └── projeto-beepy-firebase-adminsdk-*.json
├── frontend/
│   ├── src/
│   │   ├── components/       # Componentes React
│   │   ├── contexts/        # Contextos (Auth, etc.)
│   │   └── ...
│   ├── package.json
│   └── vite.config.js
├── vercel.json              # Configuração Vercel
└── README.md
```

## 🔧 Configuração Local

### Pré-requisitos
- Python 3.11+
- Node.js 18+
- Conta no Firebase
- Credenciais do Firebase

### Backend
1. Entre na pasta do backend:
   ```bash
   cd backend
   ```

2. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```

3. Configure as credenciais do Firebase:
   - Coloque o arquivo de credenciais na pasta backend
   - Ou configure a variável de ambiente `GOOGLE_APPLICATION_CREDENTIALS`

4. Execute o servidor:
   ```bash
   python main.py
   ```

### Frontend
1. Entre na pasta do frontend:
   ```bash
   cd frontend
   ```

2. Instale as dependências:
   ```bash
   npm install
   ```

3. Configure a variável de ambiente:
   ```bash
   # Crie um arquivo .env
   VITE_API_BASE_URL=http://localhost:10000/api
   ```

4. Execute o servidor de desenvolvimento:
   ```bash
   npm run dev
   ```

## 🚀 Deploy

### Backend no Render

1. **Conecte seu repositório** ao Render
2. **Configure as variáveis de ambiente**:
   - `GOOGLE_APPLICATION_CREDENTIALS`: JSON das credenciais Firebase
   - `SECRET_KEY`: Chave secreta para Flask
   - `JWT_SECRET_KEY`: Chave secreta para JWT
3. **Deploy automático** será feito seguindo o `render.yaml`

### Frontend no Vercel

1. **Conecte seu repositório** ao Vercel
2. **Configure as variáveis de ambiente**:
   - `VITE_API_BASE_URL`: URL do seu backend no Render
3. **Deploy automático** será feito seguindo o `vercel.json`

## 🔐 Credenciais Padrão

**Administrador:**
- Email: `admin@beepy.com`
- Senha: `admin123`

> ⚠️ **Importante**: Altere essas credenciais após o primeiro acesso!

## 📋 Configuração do Firebase

### 1. Criar Projeto Firebase
1. Acesse [Firebase Console](https://console.firebase.google.com/)
2. Crie um novo projeto
3. Ative o Firestore Database

### 2. Configurar Autenticação de Serviço
1. Vá em "Configurações do Projeto" > "Contas de Serviço"
2. Clique em "Gerar nova chave privada"
3. Baixe o arquivo JSON
4. Renomeie para `projeto-beepy-firebase-adminsdk-fbsvc-45c41daaaf.json`

### 3. Configurar Firestore
1. Crie as seguintes coleções:
   - `users` (usuários)
   - `indications` (indicações)
   - `commissions` (comissões)

## 🔧 Variáveis de Ambiente

### Backend (.env ou Render)
```env
SECRET_KEY=sua-chave-secreta-flask
JWT_SECRET_KEY=sua-chave-secreta-jwt
GOOGLE_APPLICATION_CREDENTIALS={"type":"service_account"...}
PORT=10000
```

### Frontend (.env ou Vercel)
```env
VITE_API_BASE_URL=https://seu-backend.onrender.com/api
```

## 🐛 Solução de Problemas

### Erro de CORS
- Verifique se o backend está configurado para aceitar requisições do frontend
- Confirme as URLs nos arquivos de configuração

### Erro de Firebase
- Verifique se as credenciais estão corretas
- Confirme se o Firestore está ativo no projeto

### Erro de Login
- Execute o endpoint `/api/setup` para criar o usuário admin
- Verifique se o Firebase está conectado

## 📞 Suporte

Para suporte técnico ou dúvidas sobre o sistema, entre em contato através dos canais oficiais.

## 📄 Licença

Este projeto é propriedade da equipe Beepy. Todos os direitos reservados.

---

**Versão:** 3.0  
**Última atualização:** Julho 2025

