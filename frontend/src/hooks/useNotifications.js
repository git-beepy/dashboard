/**
 * Hook para gerenciar notificações em tempo real
 */
import { useState, useEffect, useRef, useCallback } from 'react';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:10000';

export const useNotifications = () => {
  const [notifications, setNotifications] = useState([]);
  const [unreadCount, setUnreadCount] = useState(0);
  const [isConnected, setIsConnected] = useState(false);
  const [error, setError] = useState(null);
  
  const eventSourceRef = useRef(null);
  const reconnectTimeoutRef = useRef(null);
  const reconnectAttempts = useRef(0);
  const maxReconnectAttempts = 5;

  // Função para conectar ao SSE
  const connect = useCallback(() => {
    const token = localStorage.getItem('access_token');
    if (!token) {
      setError('Token de acesso não encontrado');
      return;
    }

    try {
      // Fechar conexão existente se houver
      if (eventSourceRef.current) {
        eventSourceRef.current.close();
      }

      const eventSource = new EventSource(`${API_BASE_URL}/notifications/stream?token=${token}`);
      eventSourceRef.current = eventSource;

      eventSource.onopen = () => {
        console.log('Conectado ao sistema de notificações');
        setIsConnected(true);
        setError(null);
        reconnectAttempts.current = 0;
      };

      eventSource.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          
          switch (data.type) {
            case 'connected':
              console.log('Conexão SSE estabelecida');
              break;
              
            case 'heartbeat':
              // Apenas manter conexão viva
              break;
              
            case 'new_indication':
            case 'indication_status_changed':
            case 'commission_paid':
            case 'indication_created':
            case 'new_user':
            case 'system_maintenance':
              // Adicionar nova notificação
              setNotifications(prev => [data, ...prev.slice(0, 49)]); // Manter apenas 50
              if (!data.read) {
                setUnreadCount(prev => prev + 1);
              }
              
              // Mostrar notificação do navegador se permitido
              showBrowserNotification(data);
              break;
              
            default:
              console.log('Tipo de notificação desconhecido:', data.type);
          }
        } catch (error) {
          console.error('Erro ao processar notificação:', error);
        }
      };

      eventSource.onerror = (error) => {
        console.error('Erro na conexão SSE:', error);
        setIsConnected(false);
        
        if (eventSource.readyState === EventSource.CLOSED) {
          // Tentar reconectar
          if (reconnectAttempts.current < maxReconnectAttempts) {
            const delay = Math.min(1000 * Math.pow(2, reconnectAttempts.current), 30000);
            console.log(`Tentando reconectar em ${delay}ms (tentativa ${reconnectAttempts.current + 1})`);
            
            reconnectTimeoutRef.current = setTimeout(() => {
              reconnectAttempts.current++;
              connect();
            }, delay);
          } else {
            setError('Falha ao conectar ao sistema de notificações após várias tentativas');
          }
        }
      };

    } catch (error) {
      console.error('Erro ao criar conexão SSE:', error);
      setError('Erro ao conectar ao sistema de notificações');
    }
  }, []);

  // Função para desconectar
  const disconnect = useCallback(() => {
    if (eventSourceRef.current) {
      eventSourceRef.current.close();
      eventSourceRef.current = null;
    }
    
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
      reconnectTimeoutRef.current = null;
    }
    
    setIsConnected(false);
    reconnectAttempts.current = 0;
  }, []);

  // Função para mostrar notificação do navegador
  const showBrowserNotification = (notification) => {
    if ('Notification' in window && Notification.permission === 'granted') {
      const options = {
        body: notification.message,
        icon: '/favicon.ico',
        badge: '/favicon.ico',
        tag: notification.id,
        requireInteraction: notification.priority === 'high',
        silent: notification.priority === 'low'
      };

      const browserNotification = new Notification(notification.title, options);
      
      // Auto-fechar após 5 segundos (exceto alta prioridade)
      if (notification.priority !== 'high') {
        setTimeout(() => {
          browserNotification.close();
        }, 5000);
      }
    }
  };

  // Função para solicitar permissão de notificação
  const requestNotificationPermission = useCallback(async () => {
    if ('Notification' in window) {
      const permission = await Notification.requestPermission();
      return permission === 'granted';
    }
    return false;
  }, []);

  // Função para marcar notificação como lida
  const markAsRead = useCallback(async (notificationId) => {
    const token = localStorage.getItem('access_token');
    if (!token) return;

    try {
      const response = await fetch(`${API_BASE_URL}/notifications/${notificationId}/read`, {
        method: 'PUT',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      if (response.ok) {
        setNotifications(prev => 
          prev.map(notif => 
            notif.id === notificationId 
              ? { ...notif, read: true }
              : notif
          )
        );
        
        setUnreadCount(prev => Math.max(0, prev - 1));
      }
    } catch (error) {
      console.error('Erro ao marcar notificação como lida:', error);
    }
  }, []);

  // Função para marcar todas como lidas
  const markAllAsRead = useCallback(async () => {
    const unreadNotifications = notifications.filter(n => !n.read);
    
    for (const notification of unreadNotifications) {
      await markAsRead(notification.id);
    }
  }, [notifications, markAsRead]);

  // Função para carregar histórico de notificações
  const loadHistory = useCallback(async (limit = 20) => {
    const token = localStorage.getItem('access_token');
    if (!token) return;

    try {
      const response = await fetch(`${API_BASE_URL}/notifications/history?limit=${limit}`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      if (response.ok) {
        const data = await response.json();
        setNotifications(data.notifications || []);
        setUnreadCount(data.unread_count || 0);
      }
    } catch (error) {
      console.error('Erro ao carregar histórico de notificações:', error);
    }
  }, []);

  // Função para obter contagem de não lidas
  const refreshUnreadCount = useCallback(async () => {
    const token = localStorage.getItem('access_token');
    if (!token) return;

    try {
      const response = await fetch(`${API_BASE_URL}/notifications/unread-count`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      if (response.ok) {
        const data = await response.json();
        setUnreadCount(data.unread_count || 0);
      }
    } catch (error) {
      console.error('Erro ao obter contagem de não lidas:', error);
    }
  }, []);

  // Efeito para conectar/desconectar
  useEffect(() => {
    const token = localStorage.getItem('access_token');
    
    if (token) {
      // Carregar histórico primeiro
      loadHistory();
      
      // Conectar ao SSE
      connect();
      
      // Solicitar permissão de notificação
      requestNotificationPermission();
    }

    // Cleanup na desmontagem
    return () => {
      disconnect();
    };
  }, [connect, disconnect, loadHistory, requestNotificationPermission]);

  // Efeito para reconectar quando o token muda
  useEffect(() => {
    const token = localStorage.getItem('access_token');
    
    if (token && !isConnected && !error) {
      connect();
    } else if (!token) {
      disconnect();
      setNotifications([]);
      setUnreadCount(0);
    }
  }, [connect, disconnect, isConnected, error]);

  // Efeito para lidar com visibilidade da página
  useEffect(() => {
    const handleVisibilityChange = () => {
      if (document.visibilityState === 'visible' && !isConnected) {
        // Reconectar quando a página fica visível
        const token = localStorage.getItem('access_token');
        if (token) {
          connect();
        }
      }
    };

    document.addEventListener('visibilitychange', handleVisibilityChange);
    
    return () => {
      document.removeEventListener('visibilitychange', handleVisibilityChange);
    };
  }, [connect, isConnected]);

  return {
    notifications,
    unreadCount,
    isConnected,
    error,
    markAsRead,
    markAllAsRead,
    loadHistory,
    refreshUnreadCount,
    requestNotificationPermission,
    connect,
    disconnect
  };
};

export default useNotifications;

