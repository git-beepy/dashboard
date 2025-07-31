import React, { useEffect, useState } from 'react';
import { Navigate } from 'react-router-dom';
import { authService, apiUtils } from '../../services/apiService';

const PrivateRoute = ({ children }) => {
  const [isAuthenticated, setIsAuthenticated] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const checkAuth = async () => {
      try {
        // Verificar se há token no localStorage
        if (!apiUtils.isAuthenticated()) {
          setIsAuthenticated(false);
          setLoading(false);
          return;
        }

        // Verificar se o token é válido
        await authService.verify();
        setIsAuthenticated(true);
      } catch (error) {
        console.error('Erro na verificação de autenticação:', error);
        // Token inválido ou expirado
        authService.logout();
        setIsAuthenticated(false);
      } finally {
        setLoading(false);
      }
    };

    checkAuth();
  }, []);

  // Mostrar loading enquanto verifica autenticação
  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Verificando autenticação...</p>
        </div>
      </div>
    );
  }

  // Redirecionar para login se não autenticado
  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  // Renderizar componente protegido
  return children;
};

export default PrivateRoute;

