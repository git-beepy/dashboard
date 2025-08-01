import React from 'react';

const LoadingSpinner = ({ size = 'md', text = 'Carregando...' }) => {
  const sizeClasses = {
    sm: 'h-4 w-4',
    md: 'h-8 w-8',
    lg: 'h-12 w-12'
  };

  return (
    <div className="flex flex-col items-center justify-center p-8">
      <div className={`
        animate-spin rounded-full border-b-2 border-blue-600 
        ${sizeClasses[size]}
      `} />
      {text && (
        <p className="mt-4 text-gray-600 text-sm">{text}</p>
      )}
    </div>
  );
};

export default LoadingSpinner;

