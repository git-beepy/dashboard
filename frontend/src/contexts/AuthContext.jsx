import React, { createContext, useContext, useState, useEffect } from 'react';
import axios from 'axios';

const AuthContext = createContext();

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth deve ser usado dentro de AuthProvider');
  }
  return context;
};

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  // Configurar URL base da API
  const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:10000/api';

  // Configurar interceptor para requests
  useEffect(() => {
    const requestInterceptor = axios.interceptors.request.use(
      (config) => {
        const token = localStorage.getItem('token');
        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
      },
      (error) => {
        return Promise.reject(error);
      }
    );

    // Configurar interceptor para responses
    const responseInterceptor = axios.interceptors.response.use(
      (response) => response,
      (error) => {
        if (error.response?.status === 401) {
          // Token expirado ou inválido
          logout();
        }
        return Promise.reject(error);
      }
    );

    return () => {
      axios.interceptors.request.eject(requestInterceptor);
      axios.interceptors.response.eject(responseInterceptor);
    };
  }, []);

  useEffect(() => {
    const initializeAuth = () => {
      try {
        const token = localStorage.getItem('token');
        const userData = localStorage.getItem('user');
        
        if (token && userData) {
          const parsedUser = JSON.parse(userData);
          setUser(parsedUser);
          axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
        }
      } catch (error) {
        console.error('Erro ao inicializar autenticação:', error);
        // Limpar dados corrompidos
        localStorage.removeItem('token');
        localStorage.removeItem('user');
      } finally {
        setLoading(false);
      }
    };

    initializeAuth();
  }, []);

  const login = async (email, password) => {
    try {
      console.log('Tentando fazer login com:', { email, API_BASE_URL });
      
      const response = await axios.post(`${API_BASE_URL}/auth/login`, {
        email,
        password,
      }, {
        headers: {
          'Content-Type': 'application/json',
        },
        timeout: 10000, // 10 segundos de timeout
      });

      console.log('Resposta do login:', response.data);

      const { access_token, user: userData } = response.data;

      if (!access_token || !userData) {
        throw new Error('Resposta inválida do servidor');
      }

      // Salvar dados no localStorage
      localStorage.setItem('token', access_token);
      localStorage.setItem('user', JSON.stringify(userData));
      
      // Configurar header de autorização
      axios.defaults.headers.common['Authorization'] = `Bearer ${access_token}`;
      
      // Atualizar estado
      setUser(userData);

      return { success: true, user: userData };
    } catch (error) {
      console.error('Erro no login:', error);
      
      let errorMessage = 'Erro ao fazer login';
      
      if (error.response) {
        // Erro da API
        errorMessage = error.response.data?.error || `Erro ${error.response.status}: ${error.response.statusText}`;
      } else if (error.request) {
        // Erro de rede
        errorMessage = 'Erro de conexão. Verifique sua internet e tente novamente.';
      } else if (error.code === 'ECONNABORTED') {
        // Timeout
        errorMessage = 'Timeout na conexão. Tente novamente.';
      } else {
        // Outros erros
        errorMessage = error.message || 'Erro desconhecido';
      }

      return {
        success: false,
        error: errorMessage,
      };
    }
  };

  const logout = () => {
    try {
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      delete axios.defaults.headers.common['Authorization'];
      setUser(null);
    } catch (error) {
      console.error('Erro ao fazer logout:', error);
    }
  };

  const isAuthenticated = () => {
    return !!user && !!localStorage.getItem('token');
  };

  const value = {
    user,
    login,
    logout,
    loading,
    API_BASE_URL,
    isAuthenticated,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};

