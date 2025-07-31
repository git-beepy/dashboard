import React from 'react';
import { AlertCircle, RefreshCw } from 'lucide-react';
import { Button } from '../ui/button';

const ErrorMessage = ({ 
  message = 'Ocorreu um erro inesperado', 
  onRetry = null,
  showRetry = true 
}) => {
  return (
    <div className="flex flex-col items-center justify-center p-8 text-center">
      <div className="bg-red-100 rounded-full p-3 mb-4">
        <AlertCircle className="h-8 w-8 text-red-600" />
      </div>
      
      <h3 className="text-lg font-medium text-gray-900 mb-2">
        Ops! Algo deu errado
      </h3>
      
      <p className="text-gray-600 mb-6 max-w-md">
        {message}
      </p>
      
      {showRetry && onRetry && (
        <Button 
          onClick={onRetry}
          variant="outline"
          className="flex items-center gap-2"
        >
          <RefreshCw size={16} />
          Tentar novamente
        </Button>
      )}
    </div>
  );
};

export default ErrorMessage;

