import { useState, useEffect } from 'react';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;

// Hook personalizado para sincronização em tempo real com Firestore
export const useFirestoreRealtime = (collection, filters = [], dependencies = []) => {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    let intervalId;
    
    const fetchData = async () => {
      try {
        const token = localStorage.getItem('access_token');
        if (!token) {
          setError('Token de acesso não encontrado');
          setLoading(false);
          return;
        }

        const response = await fetch(`${API_BASE_URL}/${collection}`, {
          method: 'GET',
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          }
        });

        if (response.ok) {
          const result = await response.json();
          setData(result);
          setError(null);
        } else {
          const errorData = await response.json();
          setError(errorData.error || 'Erro ao buscar dados');
        }
      } catch (err) {
        setError('Erro de conexão');
        console.error('Erro ao buscar dados:', err);
      } finally {
        setLoading(false);
      }
    };

    // Buscar dados inicialmente
    fetchData();

    // Configurar polling para simular tempo real (a cada 5 segundos)
    intervalId = setInterval(fetchData, 5000);

    // Cleanup
    return () => {
      if (intervalId) {
        clearInterval(intervalId);
      }
    };
  }, [...dependencies]);

  const refetch = () => {
    setLoading(true);
    // Força uma nova busca imediatamente
    const fetchData = async () => {
      try {
        const token = localStorage.getItem('access_token');
        if (!token) {
          setError('Token de acesso não encontrado');
          setLoading(false);
          return;
        }

        const response = await fetch(`${API_BASE_URL}/${collection}`, {
          method: 'GET',
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          }
        });

        if (response.ok) {
          const result = await response.json();
          setData(result);
          setError(null);
        } else {
          const errorData = await response.json();
          setError(errorData.error || 'Erro ao buscar dados');
        }
      } catch (err) {
        setError('Erro de conexão');
        console.error('Erro ao buscar dados:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  };

  return { data, loading, error, refetch };
};

// Hook específico para indicações
export const useIndicationsRealtime = () => {
  return useFirestoreRealtime('indications');
};

// Hook específico para comissões
export const useCommissionsRealtime = () => {
  return useFirestoreRealtime('commissions');
};

// Hook específico para usuários (apenas admin)
export const useUsersRealtime = () => {
  return useFirestoreRealtime('users');
};

// Hook para dashboard em tempo real
export const useDashboardRealtime = (userRole) => {
  const endpoint = userRole === 'admin' ? 'dashboard/admin' : 'dashboard/ambassador';
  return useFirestoreRealtime(endpoint, [], [userRole]);
};

// Hook para operações CRUD com sincronização automática
export const useFirestoreCRUD = (collection) => {
  const { data, loading, error, refetch } = useFirestoreRealtime(collection);

  const create = async (itemData) => {
    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch(`${API_BASE_URL}/${collection}`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(itemData)
      });

      if (response.ok) {
        const result = await response.json();
        // Atualizar dados localmente para resposta imediata
        refetch();
        return { success: true, data: result };
      } else {
        const errorData = await response.json();
        return { success: false, error: errorData.error || 'Erro ao criar item' };
      }
    } catch (err) {
      return { success: false, error: 'Erro de conexão' };
    }
  };

  const update = async (itemId, updateData) => {
    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch(`${API_BASE_URL}/${collection}/${itemId}`, {
        method: 'PUT',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(updateData)
      });

      if (response.ok) {
        const result = await response.json();
        // Atualizar dados localmente para resposta imediata
        refetch();
        return { success: true, data: result };
      } else {
        const errorData = await response.json();
        return { success: false, error: errorData.error || 'Erro ao atualizar item' };
      }
    } catch (err) {
      return { success: false, error: 'Erro de conexão' };
    }
  };

  const remove = async (itemId) => {
    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch(`${API_BASE_URL}/${collection}/${itemId}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      if (response.ok) {
        // Atualizar dados localmente para resposta imediata
        refetch();
        return { success: true };
      } else {
        const errorData = await response.json();
        return { success: false, error: errorData.error || 'Erro ao excluir item' };
      }
    } catch (err) {
      return { success: false, error: 'Erro de conexão' };
    }
  };

  const updateStatus = async (itemId, status) => {
    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch(`${API_BASE_URL}/${collection}/${itemId}/status`, {
        method: 'PUT',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ status })
      });

      if (response.ok) {
        const result = await response.json();
        // Atualizar dados localmente para resposta imediata
        refetch();
        return { success: true, data: result };
      } else {
        const errorData = await response.json();
        return { success: false, error: errorData.error || 'Erro ao atualizar status' };
      }
    } catch (err) {
      return { success: false, error: 'Erro de conexão' };
    }
  };

  return {
    data,
    loading,
    error,
    refetch,
    create,
    update,
    remove,
    updateStatus
  };
};

// Context para notificações em tempo real
export const useRealtimeNotifications = () => {
  const [notifications, setNotifications] = useState([]);

  const addNotification = (message, type = 'info') => {
    const id = Date.now();
    const notification = { id, message, type, timestamp: new Date() };
    
    setNotifications(prev => [...prev, notification]);

    // Remover notificação após 5 segundos
    setTimeout(() => {
      setNotifications(prev => prev.filter(n => n.id !== id));
    }, 5000);
  };

  const removeNotification = (id) => {
    setNotifications(prev => prev.filter(n => n.id !== id));
  };

  return {
    notifications,
    addNotification,
    removeNotification
  };
};

