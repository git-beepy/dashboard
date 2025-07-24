# Guia de Hospedagem do Sistema Beepy em Subdomínio Próprio na Plataforma Manus

Este guia detalha os passos necessários para configurar seu subdomínio e hospedar o sistema Beepy (frontend e backend) na plataforma Manus.

## 1. Entendendo a Estrutura do Deploy

O sistema Beepy é composto por duas partes principais:
- **Frontend (React)**: A interface do usuário que você acessa pelo navegador.
- **Backend (Flask)**: A API que processa os dados, gerencia a autenticação e interage com o banco de dados.

Ambas as partes serão hospedadas separadamente na plataforma Manus, e você poderá apontar seu subdomínio para o frontend.

## 2. Configuração do Subdomínio (DNS)

Para usar um subdomínio próprio (ex: `app.seusite.com.br`), você precisará configurar um registro DNS `CNAME` ou `A` no painel de controle do seu provedor de domínio (onde você comprou `seusite.com.br`).

**Passo a passo:**

1.  **Acesse o painel de controle do seu provedor de domínio** (ex: GoDaddy, HostGator, Registro.br, Cloudflare).
2.  **Localize a seção de gerenciamento de DNS** (pode ser chamada de 


`Zona DNS`, `Gerenciar DNS`, `Configurações de DNS`, etc.).
3.  **Crie um novo registro**:
    *   **Tipo**: `CNAME` (recomendado) ou `A`.
    *   **Nome/Host**: O nome do seu subdomínio (ex: `app`).
    *   **Valor/Aponta para**: Este valor será fornecido pela plataforma Manus após o deploy do seu frontend. Será um domínio gerado pela Manus (ex: `seusite-frontend.manus.space`).
    *   **TTL (Time To Live)**: Deixe o valor padrão ou defina um valor baixo (ex: 300 segundos) para que as alterações se propaguem mais rapidamente.

**Exemplo de configuração CNAME:**

| Tipo  | Nome/Host | Valor/Aponta para         | TTL   |
| :---- | :-------- | :------------------------ | :---- |
| CNAME | `app`     | `seusite-frontend.manus.space` | Auto  |

**Importante**: A propagação do DNS pode levar de alguns minutos a 48 horas. Você pode verificar o status da propagação usando ferramentas como `whatsmydns.net`.

## 3. Deploy do Frontend na Plataforma Manus

O frontend do sistema Beepy é uma aplicação React. Para hospedá-lo na Manus, você usará a ferramenta `service_deploy_frontend`.

**Passo a passo:**

1.  **Prepare seu projeto para produção**: Certifique-se de que seu projeto React esteja construído para produção. No caso do Beepy, isso é feito com `npm run build` ou `pnpm run build`.
    ```bash
    cd /home/ubuntu/beepy-system/frontend/beepy-frontend
    pnpm run build
    ```
    Isso criará uma pasta `dist` (ou `build`) com os arquivos estáticos otimizados.

2.  **Execute o comando de deploy**: Utilize a ferramenta `service_deploy_frontend` apontando para o diretório de build do seu frontend.
    ```python
    print(default_api.service_deploy_frontend(
        brief="Fazendo deploy do frontend do sistema Beepy.",
        framework="react",
        project_dir="/home/ubuntu/beepy-system/frontend/beepy-frontend/dist" # Ou 'build', dependendo da sua configuração
    ))
    ```
    A plataforma Manus retornará uma URL pública permanente para o seu frontend (ex: `https://seu-frontend-id.manus.space`). Guarde esta URL, pois você precisará dela para configurar o CNAME no Passo 2.

3.  **Configure o subdomínio na Manus (se aplicável)**: Algumas plataformas de deploy permitem que você adicione seu domínio personalizado diretamente no painel delas. Verifique a documentação da Manus para ver se há uma opção para adicionar seu subdomínio (`app.seusite.com.br`) diretamente ao deploy do frontend. Se houver, siga as instruções deles para vincular o subdomínio à URL gerada.

## 4. Deploy do Backend na Plataforma Manus

O backend do sistema Beepy é uma aplicação Flask. Para hospedá-lo, você usará a ferramenta `service_deploy_backend`.

**Passo a passo:**

1.  **Execute o comando de deploy**: Utilize a ferramenta `service_deploy_backend` apontando para o diretório raiz do seu backend Flask.
    ```python
    print(default_api.service_deploy_backend(
        brief="Fazendo deploy do backend do sistema Beepy.",
        framework="flask",
        project_dir="/home/ubuntu/beepy-system/backend/beepy-backend"
    ))
    ```
    A plataforma Manus retornará uma URL pública permanente para o seu backend (ex: `https://seu-backend-id.manus.space`). Guarde esta URL, pois você precisará atualizar o frontend para apontar para ela.

2.  **Atualize a URL do Backend no Frontend**: Após o deploy do backend, você precisará editar o código do seu frontend para que ele saiba onde encontrar a API do backend. Isso geralmente envolve a alteração de uma variável de ambiente ou de uma constante no código do frontend.
    *   Localize o arquivo onde as requisições para o backend são feitas (provavelmente em `src/components/AuthenticatedApp.jsx` ou em um arquivo de configuração de API).
    *   Substitua `http://localhost:5000` (ou a URL anterior) pela nova URL do backend gerada pela Manus (ex: `https://seu-backend-id.manus.space`).
    *   Após a alteração, você precisará **reconstruir o frontend** (`pnpm run build`) e **fazer o deploy novamente** (`service_deploy_frontend`) para que a mudança seja aplicada.

## 5. Testando o Sistema Deployado

Após configurar o DNS e realizar os deploys do frontend e backend, você poderá acessar seu sistema pelo seu subdomínio (`app.seusite.com.br`).

1.  Abra seu navegador e digite seu subdomínio.
2.  Verifique se a tela de login aparece.
3.  Tente fazer login com as credenciais `admin` / `admin`.
4.  Teste a criação de um novo usuário e as funcionalidades dos dashboards.

**Observações:**
-   Certifique-se de que o backend está configurado para aceitar requisições de todas as origens (CORS), o que já foi feito no código fornecido (`CORS(app, origins="*")`).
-   A URL do backend (`https://seu-backend-id.manus.space`) deve ser usada para todas as chamadas de API do frontend.

---

