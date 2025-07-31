import React from 'react';

export const Badge = ({ 
  children, 
  variant = 'default', 
  className = '', 
  ...props 
}) => {
  const baseClasses = 'inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-semibold transition-colors focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2';
  
  const variants = {
    default: 'border-transparent bg-blue-600 text-white hover:bg-blue-700',
    secondary: 'border-transparent bg-gray-100 text-gray-900 hover:bg-gray-200',
    destructive: 'border-transparent bg-red-600 text-white hover:bg-red-700',
    outline: 'text-gray-900 border-gray-300',
    success: 'border-transparent bg-green-600 text-white hover:bg-green-700',
    warning: 'border-transparent bg-yellow-600 text-white hover:bg-yellow-700'
  };
  
  return (
    <div 
      className={`${baseClasses} ${variants[variant]} ${className}`}
      {...props}
    >
      {children}
    </div>
  );
};

