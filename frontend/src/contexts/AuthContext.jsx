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
  const [error, setError] = useState(null);

  // Configurar URL base da API
  const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:10000';

  // Configurar axios defaults
  useEffect(() => {
    axios.defaults.timeout = 15000; // 15 segundos
    axios.defaults.headers.common['Content-Type'] = 'application/json';
  }, []);

  // Configurar interceptors
  useEffect(() => {
    const requestInterceptor = axios.interceptors.request.use(
      (config) => {
        const token = localStorage.getItem('token');
        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
        }
        
        // Log da requisição para debug
        console.log(`[API Request] ${config.method?.toUpperCase()} ${config.url}`);
        
        return config;
      },
      (error) => {
        console.error('[API Request Error]', error);
        return Promise.reject(error);
      }
    );

    const responseInterceptor = axios.interceptors.response.use(
      (response) => {
        console.log(`[API Response] ${response.status} ${response.config.url}`);
        return response;
      },
      (error) => {
        console.error('[API Response Error]', error.response?.status, error.response?.data);
        
        if (error.response?.status === 401) {
          console.log('Token expirado ou inválido, fazendo logout...');
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

  // Inicializar autenticação
  useEffect(() => {
    const initializeAuth = async () => {
      try {
        setError(null);
        const token = localStorage.getItem('token');
        const userData = localStorage.getItem('user');
        
        if (token && userData) {
          const parsedUser = JSON.parse(userData);
          
          // Verificar se o token ainda é válido
          try {
            const response = await axios.get(`${API_BASE_URL}/auth/verify`, {
              headers: { Authorization: `Bearer ${token}` }
            });
            
            if (response.data.user) {
              setUser(response.data.user);
              console.log('Usuário autenticado:', response.data.user.email);
            } else {
              throw new Error('Resposta inválida do servidor');
            }
          } catch (verifyError) {
            console.log('Token inválido, removendo dados de autenticação');
            localStorage.removeItem('token');
            localStorage.removeItem('user');
            setUser(null);
          }
        }
      } catch (error) {
        console.error('Erro ao inicializar autenticação:', error);
        localStorage.removeItem('token');
        localStorage.removeItem('user');
        setUser(null);
        setError('Erro ao inicializar autenticação');
      } finally {
        setLoading(false);
      }
    };

    initializeAuth();
  }, [API_BASE_URL]);

  const login = async (email, password) => {
    try {
      setError(null);
      setLoading(true);
      
      console.log('Iniciando login para:', email);
      console.log('URL da API:', `${API_BASE_URL}/auth/login`);
      
      const response = await axios.post(`${API_BASE_URL}/auth/login`, {
        email: email.trim(),
        password: password,
      });

      console.log('Resposta do login:', response.data);

      const { access_token, user: userData } = response.data;

      if (!access_token || !userData) {
        throw new Error('Resposta inválida do servidor - token ou dados do usuário ausentes');
      }

      // Salvar dados no localStorage
      localStorage.setItem('token', access_token);
      localStorage.setItem('user', JSON.stringify(userData));
      
      // Atualizar estado
      setUser(userData);

      console.log('Login realizado com sucesso para:', userData.email);
      return { success: true, user: userData };
      
    } catch (error) {
      console.error('Erro no login:', error);
      
      let errorMessage = 'Erro ao fazer login';
      
      if (error.response) {
        // Erro da API
        const status = error.response.status;
        const data = error.response.data;
        
        if (status === 401) {
          errorMessage = data?.error || 'Email ou senha incorretos';
        } else if (status === 400) {
          errorMessage = data?.error || 'Dados inválidos';
        } else if (status >= 500) {
          errorMessage = 'Erro interno do servidor. Tente novamente.';
        } else {
          errorMessage = data?.error || `Erro ${status}`;
        }
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

      setError(errorMessage);
      return { success: false, error: errorMessage };
      
    } finally {
      setLoading(false);
    }
  };

  const logout = () => {
    try {
      console.log('Fazendo logout...');
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      setUser(null);
      setError(null);
      console.log('Logout realizado com sucesso');
    } catch (error) {
      console.error('Erro ao fazer logout:', error);
    }
  };

  const isAuthenticated = () => {
    return !!user && !!localStorage.getItem('token');
  };

  const clearError = () => {
    setError(null);
  };

  const value = {
    user,
    login,
    logout,
    loading,
    error,
    clearError,
    API_BASE_URL,
    isAuthenticated,
    token: localStorage.getItem('token'),
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};

