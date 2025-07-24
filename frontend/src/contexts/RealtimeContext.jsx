import React, { createContext, useContext, useEffect, useState } from 'react';
import { useRealtimeNotifications } from '../hooks/useFirestoreRealtime';

const RealtimeContext = createContext();

export const useRealtime = () => {
  const context = useContext(RealtimeContext);
  if (!context) {
    throw new Error('useRealtime deve ser usado dentro de RealtimeProvider');
  }
  return context;
};

export const RealtimeProvider = ({ children }) => {
  const [isConnected, setIsConnected] = useState(true);
  const [lastUpdate, setLastUpdate] = useState(new Date());
  const { notifications, addNotification, removeNotification } = useRealtimeNotifications();

  // Simular conexão em tempo real
  useEffect(() => {
    const checkConnection = () => {
      // Simular verificação de conexão
      const connected = navigator.onLine;
      setIsConnected(connected);
      
      if (connected) {
        setLastUpdate(new Date());
      }
    };

    // Verificar conexão a cada 30 segundos
    const intervalId = setInterval(checkConnection, 30000);

    // Listeners para eventos de conexão
    window.addEventListener('online', checkConnection);
    window.addEventListener('offline', checkConnection);

    return () => {
      clearInterval(intervalId);
      window.removeEventListener('online', checkConnection);
      window.removeEventListener('offline', checkConnection);
    };
  }, []);

  // Função para notificar mudanças
  const notifyChange = (type, message) => {
    addNotification(message, type);
    setLastUpdate(new Date());
  };

  // Função para forçar sincronização
  const forceSync = () => {
    setLastUpdate(new Date());
    addNotification('Dados sincronizados', 'success');
  };

  const value = {
    isConnected,
    lastUpdate,
    notifications,
    addNotification,
    removeNotification,
    notifyChange,
    forceSync
  };

  return (
    <RealtimeContext.Provider value={value}>
      {children}
    </RealtimeContext.Provider>
  );
};

