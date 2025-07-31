import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:10000';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 15000, // 15 segundos
  headers: {
    'Content-Type': 'application/json',
  },
});

// Interceptor para adicionar o token de autenticação
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    console.log(`[API Request] ${config.method?.toUpperCase()} ${config.url}`);
    return config;
  },
  (error) => {
    console.error('[API Request Error]', error);
    return Promise.reject(error);
  }
);

// Interceptor para lidar com erros de resposta (ex: 401 Unauthorized)
api.interceptors.response.use(
  (response) => {
    console.log(`[API Response] ${response.status} ${response.config.url}`);
    return response;
  },
  (error) => {
    console.error('[API Response Error]', error.response?.status, error.response?.data);
    if (error.response?.status === 401) {
      // Opcional: Redirecionar para a página de login ou forçar logout
      console.log('Token expirado ou inválido. Forçando logout...');
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      window.location.href = '/login'; // Redireciona para a página de login
    }
    return Promise.reject(error);
  }
);

export default api;


