#!/bin/bash

echo "🚀 Iniciando Sistema Beepy..."
echo ""

# Verificar se estamos no diretório correto
if [ ! -f "README.md" ]; then
    echo "❌ Erro: Execute este script a partir do diretório raiz do projeto"
    exit 1
fi

# Função para verificar se uma porta está em uso
check_port() {
    if lsof -Pi :$1 -sTCP:LISTEN -t >/dev/null ; then
        echo "⚠️  Porta $1 já está em uso"
        return 1
    else
        return 0
    fi
}

# Verificar dependências
echo "📋 Verificando dependências..."

# Verificar Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 não encontrado. Instale Python 3.8+ para continuar."
    exit 1
fi

# Verificar Node.js
if ! command -v node &> /dev/null; then
    echo "❌ Node.js não encontrado. Instale Node.js 16+ para continuar."
    exit 1
fi

# Verificar npm
if ! command -v npm &> /dev/null; then
    echo "❌ npm não encontrado. Instale npm para continuar."
    exit 1
fi

echo "✅ Dependências verificadas"
echo ""

# Verificar portas
echo "🔍 Verificando portas..."
if ! check_port 10000; then
    echo "   Use: lsof -ti:10000 | xargs kill -9 para liberar a porta"
    exit 1
fi

if ! check_port 5173; then
    echo "   Use: lsof -ti:5173 | xargs kill -9 para liberar a porta"
    exit 1
fi

echo "✅ Portas disponíveis"
echo ""

# Instalar dependências do backend se necessário
if [ ! -d "backend/__pycache__" ]; then
    echo "📦 Instalando dependências do backend..."
    cd backend
    pip install -r requirements.txt
    cd ..
    echo "✅ Dependências do backend instaladas"
    echo ""
fi

# Instalar dependências do frontend se necessário
if [ ! -d "frontend/node_modules" ]; then
    echo "📦 Instalando dependências do frontend..."
    cd frontend
    npm install
    cd ..
    echo "✅ Dependências do frontend instaladas"
    echo ""
fi

# Verificar arquivo de credenciais do Firebase
if [ ! -f "backend/projeto-beepy-firebase-adminsdk-fbsvc-72fd5c9b0e.json" ]; then
    echo "⚠️  Arquivo de credenciais do Firebase não encontrado!"
    echo "   Coloque o arquivo 'projeto-beepy-firebase-adminsdk-fbsvc-45c41daaaf.json' na pasta 'backend/'"
    echo "   O sistema pode não funcionar corretamente sem as credenciais."
    echo ""
fi

# Iniciar backend
echo "🔧 Iniciando backend (porta 10000)..."
cd backend
python main.py &
BACKEND_PID=$!
cd ..

# Aguardar backend inicializar
sleep 3

# Verificar se backend está rodando
if ! curl -s http://localhost:10000/health > /dev/null; then
    echo "❌ Erro ao iniciar backend"
    kill $BACKEND_PID 2>/dev/null
    exit 1
fi

echo "✅ Backend iniciado com sucesso"
echo ""

# Iniciar frontend
echo "🎨 Iniciando frontend (porta 5173)..."
cd frontend
npm run dev &
FRONTEND_PID=$!
cd ..

echo ""
echo "🎉 Sistema Beepy iniciado com sucesso!"
echo ""
echo "📍 URLs de acesso:"
echo "   Frontend: http://localhost:5173"
echo "   Backend:  http://localhost:10000"
echo "   API:      http://localhost:10000/api"
echo ""

echo ""
echo "⏹️  Para parar o sistema, pressione Ctrl+C"
echo ""

# Função para cleanup quando o script for interrompido
cleanup() {
    echo ""
    echo "🛑 Parando sistema..."
    kill $BACKEND_PID 2>/dev/null
    kill $FRONTEND_PID 2>/dev/null
    echo "✅ Sistema parado"
    exit 0
}

# Capturar sinais de interrupção
trap cleanup SIGINT SIGTERM

# Aguardar indefinidamente
wait

