# Guia de Deploy - Projeto Beepy

## Visão Geral

Este guia fornece instruções detalhadas para fazer o deploy do Projeto Beepy em diferentes plataformas de hospedagem.

## Pré-requisitos

### 1. Verificações Locais
Antes do deploy, certifique-se de que:

```bash
# 1. Aplicação funciona localmente
npm run dev

# 2. Build de produção funciona
npm run build
npm run preview

# 3. Não há erros no console
# 4. Firebase está configurado corretamente
# 5. Dados de exemplo foram populados
```

### 2. Configuração do Firebase
- Projeto Firebase criado e configurado
- Authentication habilitado (Email/Password)
- Firestore habilitado
- Regras de segurança configuradas

## Opções de Deploy

### 🔥 Opção 1: Firebase Hosting (Recomendado)

#### Vantagens
- Integração nativa com Firebase
- CDN global
- SSL automático
- Deploy simples

#### Passos

1. **Instalar Firebase CLI**
```bash
npm install -g firebase-tools
```

2. **Login no Firebase**
```bash
firebase login
```

3. **Inicializar projeto**
```bash
# Na raiz do projeto
firebase init hosting

# Configurações recomendadas:
# - Public directory: frontend/dist
# - Single-page app: Yes
# - Overwrite index.html: No
```

4. **Build e Deploy**
```bash
# Build da aplicação
cd frontend
npm run build

# Deploy
firebase deploy --only hosting
```

5. **Configurar domínio personalizado (opcional)**
```bash
firebase hosting:channel:deploy production --expires 30d
```

#### Configuração do firebase.json
```json
{
  "hosting": {
    "public": "frontend/dist",
    "ignore": [
      "firebase.json",
      "**/.*",
      "**/node_modules/**"
    ],
    "rewrites": [
      {
        "source": "**",
        "destination": "/index.html"
      }
    ],
    "headers": [
      {
        "source": "**/*.@(js|css)",
        "headers": [
          {
            "key": "Cache-Control",
            "value": "max-age=31536000"
          }
        ]
      }
    ]
  }
}
```

### 🚀 Opção 2: Vercel

#### Vantagens
- Deploy automático via Git
- Preview deployments
- Edge functions
- Analytics integrado

#### Passos

1. **Conectar repositório**
   - Acesse [vercel.com](https://vercel.com)
   - Conecte sua conta GitHub/GitLab
   - Importe o repositório

2. **Configurar projeto**
```bash
# Framework Preset: Vite
# Root Directory: frontend
# Build Command: npm run build
# Output Directory: dist
# Install Command: npm install
```

3. **Variáveis de ambiente (se necessário)**
```
VITE_FIREBASE_API_KEY=sua_api_key
VITE_FIREBASE_AUTH_DOMAIN=projeto-beepy.firebaseapp.com
# ... outras variáveis se necessário
```

4. **Deploy automático**
   - Push para branch main/master
   - Deploy automático será executado

#### vercel.json (opcional)
```json
{
  "buildCommand": "cd frontend && npm run build",
  "outputDirectory": "frontend/dist",
  "framework": "vite",
  "rewrites": [
    {
      "source": "/(.*)",
      "destination": "/index.html"
    }
  ]
}
```

### 🌐 Opção 3: Netlify

#### Vantagens
- Deploy via Git ou drag-and-drop
- Forms handling
- Edge functions
- Split testing

#### Passos

1. **Via Git (Recomendado)**
   - Acesse [netlify.com](https://netlify.com)
   - Conecte repositório
   - Configure build settings

2. **Configurações de build**
```bash
# Base directory: frontend
# Build command: npm run build
# Publish directory: frontend/dist
```

3. **Configurar redirects**
Criar `frontend/public/_redirects`:
```
/*    /index.html   200
```

#### netlify.toml (opcional)
```toml
[build]
  base = "frontend"
  command = "npm run build"
  publish = "dist"

[[redirects]]
  from = "/*"
  to = "/index.html"
  status = 200
```

### 🐳 Opção 4: Docker + Cloud Run

#### Dockerfile
```dockerfile
# Build stage
FROM node:18-alpine as build
WORKDIR /app
COPY frontend/package*.json ./
RUN npm ci --only=production
COPY frontend/ .
RUN npm run build

# Production stage
FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/nginx.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

#### nginx.conf
```nginx
events {
    worker_connections 1024;
}

http {
    include /etc/nginx/mime.types;
    default_type application/octet-stream;

    server {
        listen 80;
        server_name localhost;
        root /usr/share/nginx/html;
        index index.html;

        location / {
            try_files $uri $uri/ /index.html;
        }

        location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg)$ {
            expires 1y;
            add_header Cache-Control "public, immutable";
        }
    }
}
```

#### Deploy no Google Cloud Run
```bash
# Build da imagem
docker build -t beepy-app .

# Tag para Google Container Registry
docker tag beepy-app gcr.io/PROJECT_ID/beepy-app

# Push para registry
docker push gcr.io/PROJECT_ID/beepy-app

# Deploy no Cloud Run
gcloud run deploy beepy-app \
  --image gcr.io/PROJECT_ID/beepy-app \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

## Configurações Pós-Deploy

### 1. Verificações Essenciais

```bash
# Checklist pós-deploy:
# ✅ Aplicação carrega sem erros
# ✅ Login funciona
# ✅ Dashboard mostra dados
# ✅ Navegação entre páginas funciona
# ✅ Responsividade em mobile
# ✅ Performance adequada
```

### 2. Configurar Domínio Personalizado

#### Firebase Hosting
```bash
firebase hosting:channel:deploy production
# Seguir instruções no console
```

#### Vercel/Netlify
- Acessar configurações do projeto
- Adicionar domínio personalizado
- Configurar DNS conforme instruções

### 3. Configurar SSL
- Firebase: Automático
- Vercel/Netlify: Automático
- Cloud Run: Configurar Load Balancer

### 4. Monitoramento

#### Firebase Analytics
```javascript
// Adicionar ao firebase-config.js
import { getAnalytics } from "firebase/analytics";
const analytics = getAnalytics(app);
```

#### Google Analytics
```html
<!-- Adicionar ao index.html -->
<script async src="https://www.googletagmanager.com/gtag/js?id=GA_MEASUREMENT_ID"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());
  gtag('config', 'GA_MEASUREMENT_ID');
</script>
```

## Otimizações de Performance

### 1. Build Otimizado
```javascript
// vite.config.js
export default defineConfig({
  plugins: [react()],
  build: {
    rollupOptions: {
      output: {
        manualChunks: {
          vendor: ['react', 'react-dom'],
          firebase: ['firebase/app', 'firebase/auth', 'firebase/firestore'],
          charts: ['recharts']
        }
      }
    },
    chunkSizeWarningLimit: 1000
  }
})
```

### 2. Lazy Loading
```javascript
// Implementar lazy loading para rotas
const Dashboard = lazy(() => import('./components/Dashboard'));
const Indications = lazy(() => import('./components/Indications'));
```

### 3. Service Worker (PWA)
```javascript
// Adicionar service worker para cache
// Usar Workbox para implementação
```

## Troubleshooting

### Problemas Comuns

#### 1. Erro 404 em rotas
**Solução:** Configurar redirects para SPA
```
/*    /index.html   200
```

#### 2. Firebase não conecta
**Solução:** Verificar configurações e domínio autorizado

#### 3. Build falha
**Solução:** 
```bash
# Limpar cache
rm -rf node_modules package-lock.json
npm install
npm run build
```

#### 4. Performance lenta
**Solução:**
- Implementar code splitting
- Otimizar imagens
- Configurar cache headers

### Logs e Debugging

#### Firebase
- Console do Firebase para logs
- Performance monitoring
- Crashlytics para erros

#### Vercel/Netlify
- Function logs no dashboard
- Real-time logs durante deploy
- Analytics integrado

## Backup e Recuperação

### 1. Backup do Firestore
```bash
# Export via Firebase CLI
firebase firestore:export gs://bucket-name/backup-folder

# Import
firebase firestore:import gs://bucket-name/backup-folder
```

### 2. Backup do código
- Repositório Git como backup principal
- Tags para versões estáveis
- Branches para features

### 3. Configurações
- Documentar todas as configurações
- Manter arquivo de environment variables
- Backup das configurações de DNS

---

## Checklist Final

### Antes do Deploy
- [ ] Testes locais passando
- [ ] Build de produção funcional
- [ ] Firebase configurado
- [ ] Dados de exemplo populados
- [ ] Documentação atualizada

### Durante o Deploy
- [ ] Configurações corretas
- [ ] Variáveis de ambiente definidas
- [ ] Redirects configurados
- [ ] SSL habilitado

### Após o Deploy
- [ ] Aplicação acessível
- [ ] Todas as funcionalidades testadas
- [ ] Performance adequada
- [ ] Monitoramento configurado
- [ ] Backup configurado

---

**Recomendação:** Use Firebase Hosting para máxima compatibilidade e facilidade de manutenção.

**Suporte:** Para problemas específicos, consulte a documentação da plataforma escolhida ou entre em contato com a equipe de desenvolvimento.

