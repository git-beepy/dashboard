"""
Sistema de notificações em tempo real para o projeto Beepy
Usando Server-Sent Events (SSE) para comunicação em tempo real
"""
import json
import time
import threading
from datetime import datetime
from typing import Dict, List, Any, Optional
from flask import Response, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
import logging
from collections import defaultdict
import queue

logger = logging.getLogger(__name__)

class NotificationManager:
    """Gerenciador de notificações em tempo real"""
    
    def __init__(self):
        # Dicionário para armazenar conexões ativas por usuário
        self.connections: Dict[str, List[queue.Queue]] = defaultdict(list)
        # Histórico de notificações por usuário
        self.notification_history: Dict[str, List[Dict]] = defaultdict(list)
        # Lock para thread safety
        self.lock = threading.Lock()
        # Contador de conexões
        self.connection_count = 0
    
    def add_connection(self, user_email: str) -> queue.Queue:
        """Adiciona uma nova conexão SSE para um usuário"""
        with self.lock:
            connection_queue = queue.Queue(maxsize=100)
            self.connections[user_email].append(connection_queue)
            self.connection_count += 1
            
            logger.info(f"Nova conexão SSE para {user_email}. Total: {self.connection_count}")
            
            # Enviar notificações pendentes
            self._send_pending_notifications(user_email, connection_queue)
            
            return connection_queue
    
    def remove_connection(self, user_email: str, connection_queue: queue.Queue):
        """Remove uma conexão SSE"""
        with self.lock:
            if user_email in self.connections:
                try:
                    self.connections[user_email].remove(connection_queue)
                    self.connection_count -= 1
                    
                    # Remove usuário se não há mais conexões
                    if not self.connections[user_email]:
                        del self.connections[user_email]
                    
                    logger.info(f"Conexão SSE removida para {user_email}. Total: {self.connection_count}")
                except ValueError:
                    pass  # Conexão já foi removida
    
    def send_notification(self, user_email: str, notification: Dict[str, Any]):
        """Envia notificação para um usuário específico"""
        with self.lock:
            # Adicionar timestamp e ID único
            notification.update({
                'id': f"{int(time.time() * 1000)}_{user_email}",
                'timestamp': datetime.now().isoformat(),
                'read': False
            })
            
            # Adicionar ao histórico
            self.notification_history[user_email].append(notification)
            
            # Manter apenas as últimas 50 notificações
            if len(self.notification_history[user_email]) > 50:
                self.notification_history[user_email] = self.notification_history[user_email][-50:]
            
            # Enviar para conexões ativas
            if user_email in self.connections:
                dead_connections = []
                
                for connection_queue in self.connections[user_email]:
                    try:
                        connection_queue.put_nowait(notification)
                    except queue.Full:
                        # Conexão com fila cheia, remover
                        dead_connections.append(connection_queue)
                        logger.warning(f"Fila cheia para {user_email}, removendo conexão")
                
                # Remover conexões mortas
                for dead_conn in dead_connections:
                    self.remove_connection(user_email, dead_conn)
            
            logger.info(f"Notificação enviada para {user_email}: {notification['type']}")
    
    def send_broadcast(self, notification: Dict[str, Any], exclude_user: str = None):
        """Envia notificação para todos os usuários conectados"""
        with self.lock:
            for user_email in list(self.connections.keys()):
                if exclude_user and user_email == exclude_user:
                    continue
                
                user_notification = notification.copy()
                self.send_notification(user_email, user_notification)
    
    def send_admin_notification(self, notification: Dict[str, Any]):
        """Envia notificação apenas para administradores"""
        # Em um sistema real, você consultaria o banco de dados para obter admins
        # Por simplicidade, assumimos que emails com 'admin' são administradores
        with self.lock:
            for user_email in list(self.connections.keys()):
                if 'admin' in user_email.lower():
                    self.send_notification(user_email, notification)
    
    def _send_pending_notifications(self, user_email: str, connection_queue: queue.Queue):
        """Envia notificações não lidas para uma nova conexão"""
        if user_email in self.notification_history:
            unread_notifications = [
                notif for notif in self.notification_history[user_email]
                if not notif.get('read', False)
            ]
            
            for notification in unread_notifications[-10:]:  # Últimas 10 não lidas
                try:
                    connection_queue.put_nowait(notification)
                except queue.Full:
                    break
    
    def mark_as_read(self, user_email: str, notification_id: str):
        """Marca uma notificação como lida"""
        with self.lock:
            if user_email in self.notification_history:
                for notification in self.notification_history[user_email]:
                    if notification.get('id') == notification_id:
                        notification['read'] = True
                        logger.info(f"Notificação {notification_id} marcada como lida para {user_email}")
                        break
    
    def get_notification_history(self, user_email: str, limit: int = 20) -> List[Dict]:
        """Obtém histórico de notificações de um usuário"""
        with self.lock:
            if user_email in self.notification_history:
                return self.notification_history[user_email][-limit:]
            return []
    
    def get_unread_count(self, user_email: str) -> int:
        """Obtém contagem de notificações não lidas"""
        with self.lock:
            if user_email in self.notification_history:
                return sum(1 for notif in self.notification_history[user_email] if not notif.get('read', False))
            return 0
    
    def clear_old_notifications(self, days: int = 7):
        """Remove notificações antigas (executar periodicamente)"""
        cutoff_time = datetime.now().timestamp() - (days * 24 * 60 * 60)
        
        with self.lock:
            for user_email in list(self.notification_history.keys()):
                self.notification_history[user_email] = [
                    notif for notif in self.notification_history[user_email]
                    if datetime.fromisoformat(notif['timestamp']).timestamp() > cutoff_time
                ]
                
                if not self.notification_history[user_email]:
                    del self.notification_history[user_email]

# Instância global do gerenciador
notification_manager = NotificationManager()

def create_notification_routes(app):
    """Cria rotas para notificações em tempo real"""
    
    @app.route('/notifications/stream')
    @jwt_required()
    def notification_stream():
        """Endpoint SSE para receber notificações em tempo real"""
        user_email = get_jwt_identity()
        
        def event_stream():
            connection_queue = notification_manager.add_connection(user_email)
            
            try:
                # Enviar evento de conexão
                yield f"data: {json.dumps({'type': 'connected', 'message': 'Conectado ao sistema de notificações'})}\n\n"
                
                while True:
                    try:
                        # Aguardar notificação com timeout
                        notification = connection_queue.get(timeout=30)
                        yield f"data: {json.dumps(notification)}\n\n"
                    except queue.Empty:
                        # Enviar heartbeat para manter conexão viva
                        yield f"data: {json.dumps({'type': 'heartbeat', 'timestamp': datetime.now().isoformat()})}\n\n"
                    except Exception as e:
                        logger.error(f"Erro no stream SSE para {user_email}: {str(e)}")
                        break
            
            finally:
                notification_manager.remove_connection(user_email, connection_queue)
        
        return Response(
            event_stream(),
            mimetype='text/event-stream',
            headers={
                'Cache-Control': 'no-cache',
                'Connection': 'keep-alive',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Cache-Control'
            }
        )
    
    @app.route('/notifications/history')
    @jwt_required()
    def get_notification_history():
        """Obtém histórico de notificações do usuário"""
        user_email = get_jwt_identity()
        limit = request.args.get('limit', 20, type=int)
        
        history = notification_manager.get_notification_history(user_email, limit)
        unread_count = notification_manager.get_unread_count(user_email)
        
        return jsonify({
            'notifications': history,
            'unread_count': unread_count
        })
    
    @app.route('/notifications/<notification_id>/read', methods=['PUT'])
    @jwt_required()
    def mark_notification_read(notification_id):
        """Marca notificação como lida"""
        user_email = get_jwt_identity()
        notification_manager.mark_as_read(user_email, notification_id)
        
        return jsonify({'message': 'Notificação marcada como lida'})
    
    @app.route('/notifications/unread-count')
    @jwt_required()
    def get_unread_count():
        """Obtém contagem de notificações não lidas"""
        user_email = get_jwt_identity()
        count = notification_manager.get_unread_count(user_email)
        
        return jsonify({'unread_count': count})

# Funções utilitárias para enviar notificações específicas
def notify_new_indication(indication_data: Dict, ambassador_email: str):
    """Notifica sobre nova indicação"""
    # Notificar administradores
    notification_manager.send_admin_notification({
        'type': 'new_indication',
        'title': 'Nova Indicação Recebida',
        'message': f'Nova indicação de {indication_data.get("clientName", "Cliente")} por {ambassador_email}',
        'data': {
            'indication_id': indication_data.get('id'),
            'client_name': indication_data.get('clientName'),
            'ambassador_email': ambassador_email
        },
        'priority': 'medium'
    })
    
    # Notificar a embaixadora
    notification_manager.send_notification(ambassador_email, {
        'type': 'indication_created',
        'title': 'Indicação Criada',
        'message': f'Sua indicação para {indication_data.get("clientName", "Cliente")} foi registrada com sucesso',
        'data': {
            'indication_id': indication_data.get('id'),
            'client_name': indication_data.get('clientName')
        },
        'priority': 'low'
    })

def notify_indication_status_change(indication_data: Dict, new_status: str, ambassador_email: str):
    """Notifica sobre mudança de status de indicação"""
    status_messages = {
        'aprovada': 'foi aprovada! 🎉',
        'rejeitada': 'foi rejeitada',
        'em_analise': 'está em análise'
    }
    
    message = f'Sua indicação para {indication_data.get("clientName", "Cliente")} {status_messages.get(new_status, "teve o status alterado")}'
    
    notification_manager.send_notification(ambassador_email, {
        'type': 'indication_status_changed',
        'title': 'Status da Indicação Atualizado',
        'message': message,
        'data': {
            'indication_id': indication_data.get('id'),
            'client_name': indication_data.get('clientName'),
            'new_status': new_status
        },
        'priority': 'high' if new_status in ['aprovada', 'rejeitada'] else 'medium'
    })

def notify_commission_paid(commission_data: Dict, ambassador_email: str):
    """Notifica sobre pagamento de comissão"""
    notification_manager.send_notification(ambassador_email, {
        'type': 'commission_paid',
        'title': 'Comissão Paga',
        'message': f'Sua comissão de R$ {commission_data.get("amount", "0.00")} foi paga! 💰',
        'data': {
            'commission_id': commission_data.get('id'),
            'amount': commission_data.get('amount'),
            'indication_id': commission_data.get('indication_id')
        },
        'priority': 'high'
    })

def notify_new_user(user_data: Dict, admin_email: str):
    """Notifica sobre novo usuário criado"""
    notification_manager.send_admin_notification({
        'type': 'new_user',
        'title': 'Novo Usuário Criado',
        'message': f'Novo usuário {user_data.get("name", "Usuário")} ({user_data.get("role", "role")}) criado por {admin_email}',
        'data': {
            'user_id': user_data.get('id'),
            'user_name': user_data.get('name'),
            'user_email': user_data.get('email'),
            'user_role': user_data.get('role'),
            'created_by': admin_email
        },
        'priority': 'low'
    })

def notify_system_maintenance(message: str, start_time: str = None):
    """Notifica sobre manutenção do sistema"""
    notification_manager.send_broadcast({
        'type': 'system_maintenance',
        'title': 'Manutenção do Sistema',
        'message': message,
        'data': {
            'start_time': start_time
        },
        'priority': 'high'
    })

# Função para limpeza periódica (executar em background)
def cleanup_old_notifications():
    """Limpa notificações antigas (executar periodicamente)"""
    notification_manager.clear_old_notifications(days=7)
    logger.info("Limpeza de notificações antigas executada")

