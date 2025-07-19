# 📋 Instruções de Deploy - Sistema Beepy

## 🔥 Firebase - Configuração Inicial

### 1. Preparar Firebase
1. Acesse [Firebase Console](https://console.firebase.google.com/)
2. Crie um novo projeto ou use existente
3. Ative o **Firestore Database**
4. Vá em **Configurações** > **Contas de Serviço**
5. Clique em **"Gerar nova chave privada"**
6. Baixe o arquivo JSON das credenciais

### 2. Configurar Credenciais
Você tem duas opções:

**Opção A: Arquivo local (desenvolvimento)**
- Coloque o arquivo JSON na pasta `backend/`
- Renomeie para: `projeto-beepy-firebase-adminsdk-fbsvc-45c41daaaf.json`

**Opção B: Variável de ambiente (produção)**
- Copie todo o conteúdo do arquivo JSON
- Configure como variável `GOOGLE_APPLICATION_CREDENTIALS`

## 🚀 Deploy Backend (Render)

### 1. Preparar Repositório
```bash
# Faça commit de todas as alterações
git add .
git commit -m "Deploy: Sistema Beepy unificado"
git push origin main
```

### 2. Configurar no Render
1. Acesse [Render.com](https://render.com/)
2. Conecte sua conta GitHub
3. Clique em **"New Web Service"**
4. Selecione seu repositório
5. Configure:
   - **Name**: `beepy-backend`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn main:app --bind 0.0.0.0:$PORT`
   - **Root Directory**: `backend`

### 3. Variáveis de Ambiente no Render
Adicione estas variáveis em **Environment**:

```env
SECRET_KEY=gere-uma-chave-secreta-forte
JWT_SECRET_KEY=gere-outra-chave-secreta-forte
GOOGLE_APPLICATION_CREDENTIALS={"type":"service_account","project_id":"seu-projeto"...}
PYTHON_VERSION=3.11.0
```

> **⚠️ IMPORTANTE**: Cole o JSON completo das credenciais Firebase na variável `GOOGLE_APPLICATION_CREDENTIALS`

### 4. Deploy
- Clique em **"Create Web Service"**
- Aguarde o build completar
- Anote a URL gerada (ex: `https://beepy-backend-xyz.onrender.com`)

## 🌐 Deploy Frontend (Vercel)

### 1. Preparar Configuração
Edite o arquivo `vercel.json` na raiz do projeto:

```json
{
  "builds": [
    {
      "src": "frontend/package.json",
      "use": "@vercel/node"
    }
  ],
  "routes": [
    {
      "src": "/(.*)",
      "dest": "frontend/$1"
    }
  ],
  "env": {
    "VITE_API_BASE_URL": "https://SUA-URL-DO-RENDER.onrender.com/api"
  }
}
```

### 2. Configurar no Vercel
1. Acesse [Vercel.com](https://vercel.com/)
2. Conecte sua conta GitHub
3. Clique em **"New Project"**
4. Selecione seu repositório
5. Configure:
   - **Framework Preset**: `Vite`
   - **Root Directory**: `frontend`
   - **Build Command**: `npm run build`
   - **Output Directory**: `dist`

### 3. Variáveis de Ambiente no Vercel
Adicione em **Environment Variables**:

```env
VITE_API_BASE_URL=https://SUA-URL-DO-RENDER.onrender.com/api
```

### 4. Deploy
- Clique em **"Deploy"**
- Aguarde o build completar
- Teste a aplicação na URL gerada

## ✅ Pós-Deploy

### 1. Criar Usuário Admin
Acesse via browser ou curl:
```bash
curl -X POST https://SUA-URL-DO-RENDER.onrender.com/api/setup
```

### 2. Testar Login
1. Acesse sua aplicação no Vercel
2. Use as credenciais:
   - **Email**: `admin@beepy.com`
   - **Senha**: `admin123`

### 3. Configurar Domínio (Opcional)
- **Vercel**: Vá em Settings > Domains
- **Render**: Vá em Settings > Custom Domains

## 🔧 Troubleshooting

### Backend não inicia
- Verifique se todas as variáveis de ambiente estão configuradas
- Confirme se o JSON do Firebase está válido
- Veja os logs no painel do Render

### Frontend não conecta
- Verifique se `VITE_API_BASE_URL` aponta para a URL correta do backend
- Confirme se o backend está rodando
- Teste a API diretamente: `https://seu-backend.onrender.com/health`

### Erro de CORS
- Verifique se o backend aceita requisições do domínio do frontend
- Confirme a configuração de CORS no `main.py`

### Firebase não conecta
- Verifique se as credenciais estão corretas
- Confirme se o Firestore está ativo
- Teste localmente primeiro

## 📞 Checklist Final

- [ ] Firebase configurado e Firestore ativo
- [ ] Backend deployado no Render com todas as variáveis
- [ ] Frontend deployado no Vercel com URL do backend
- [ ] Usuário admin criado via `/api/setup`
- [ ] Login funcionando
- [ ] Todas as funcionalidades testadas

## 🔐 Segurança

### Após Deploy:
1. **Altere as credenciais padrão** do admin
2. **Configure HTTPS** (automático no Render/Vercel)
3. **Monitore os logs** regularmente
4. **Faça backup** das configurações

---

**🎉 Parabéns! Seu sistema Beepy está no ar!**

