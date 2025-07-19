
# Plano de Arquitetura do Sistema

## 1. Visão Geral
O sistema será uma plataforma web para gerenciar indicações e comissões de embaixadoras, com dois perfis de usuário: Embaixadora e Admin (Agência).

## 2. Escolha da Stack Tecnológica
- **Frontend**: React com Vite (para leveza e agilidade no desenvolvimento).
- **Backend**: Python com Flask (para flexibilidade e integração com Firebase).
- **Autenticação**: Firebase Authentication (para gerenciamento de usuários e segurança).
- **Banco de Dados**: Firebase Firestore (NoSQL, escalável e fácil integração com Firebase Auth e Cloud Functions).
- **Gráficos**: Chart.js (amplamente utilizado, flexível e bom para dashboards).
- **Hospedagem**: Vercel para o Frontend e Render para o Backend (alternativa ao Firebase Functions para o backend Flask).

## 3. Estrutura do Banco de Dados (Firebase Firestore)

### Coleção: `users`
- `uid`: ID do usuário (gerado pelo Firebase Auth)
- `email`: E-mail do usuário
- `user_type`: 'embaixadora' ou 'admin'
- `name`: Nome do usuário
- `created_at`: Timestamp da criação do usuário

### Coleção: `indications`
- `id`: ID da indicação (gerado automaticamente)
- `ambassador_uid`: UID da embaixadora que fez a indicação
- `client_name`: Nome do cliente indicado
- `client_contact`: Contato do cliente
- `niche`: Nicho do cliente
- `observations`: Observações adicionais
- `status`: 'agendado', 'aprovado', 'não aprovado'
- `sale_approval_date`: Data de aprovação da venda (se aprovado)
- `created_at`: Timestamp da criação da indicação

### Coleção: `commissions`
- `id`: ID da comissão (gerado automaticamente)
- `indication_id`: ID da indicação associada
- `ambassador_uid`: UID da embaixadora
- `parcel_number`: Número da parcela (1, 2, 3)
- `amount`: Valor da parcela (R$300)
- `due_date`: Data de vencimento da parcela
- `payment_status`: 'pendente', 'pago'
- `payment_date`: Data do pagamento (se pago)

## 4. APIs do Backend (Flask)

### Autenticação
- `POST /api/register`: Registro de novos usuários.
- `POST /api/login`: Login de usuários.

### Indicações
- `POST /api/indications`: Criar nova indicação.
- `GET /api/indications`: Listar indicações (filtrar por embaixadora, status).
- `PUT /api/indications/<id>`: Atualizar status da indicação.

### Comissões
- `GET /api/commissions`: Listar comissões (filtrar por embaixadora, status, mês).
- `PUT /api/commissions/<id>/pay`: Marcar parcela como paga.

## 5. Regras de Negócio (Implementação no Backend)
- **Cálculo de Comissões**: Ao aprovar uma indicação, o backend gerará 3 entradas na coleção `commissions` com as datas de vencimento calculadas (data de aprovação, +30 dias, +60 dias).
- **Status de Pagamento**: O admin poderá marcar manualmente as parcelas como pagas.

## 6. Interface do Usuário (Frontend React)

### Painel da Embaixadora
- Formulário de nova indicação.
- Tabela com histórico de indicações (status, detalhes).
- Resumo de indicações e vendas aprovadas.
- Gráfico de comissões mês a mês.
- Status de pagamento das comissões.

### Painel da Agência (Admin)
- Dashboard com KPIs (total de indicações, vendas, % conversão, embaixadoras ativas, comissões a pagar).
- Gráficos de evolução (indicações por mês, vendas por mês, origem dos leads, top embaixadoras).
- Tabela de gestão de indicações (atualização de status, marcação de parcelas).
- Visualização do histórico por embaixadora.
- Exportação de dados (opcional).

## 7. Próximos Passos
- Configurar o ambiente de desenvolvimento.
- Criar a estrutura dos projetos frontend e backend.

