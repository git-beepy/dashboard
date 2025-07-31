import React, { useState } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { 
  Home, 
  Users, 
  UserPlus, 
  DollarSign, 
  CreditCard, 
  LogOut, 
  Menu, 
  X 
} from 'lucide-react';
import { authService, apiUtils } from '../../services/apiService';
import { Button } from '../ui/button';

const Sidebar = () => {
  const [isOpen, setIsOpen] = useState(false);
  const location = useLocation();
  const navigate = useNavigate();
  const user = apiUtils.getCurrentUser();
  const isAdmin = apiUtils.isAdmin();

  const handleLogout = () => {
    authService.logout();
    navigate('/login');
  };

  const toggleSidebar = () => {
    setIsOpen(!isOpen);
  };

  const menuItems = [
    {
      path: '/dashboard',
      icon: Home,
      label: 'Dashboard',
      roles: ['admin', 'ambassador']
    },
    {
      path: '/indications',
      icon: UserPlus,
      label: 'Indicações',
      roles: ['admin', 'ambassador']
    },
    {
      path: '/commissions',
      icon: DollarSign,
      label: 'Comissões',
      roles: ['admin', 'ambassador']
    },
    {
      path: '/commission-installments',
      icon: CreditCard,
      label: 'Parcelas',
      roles: ['admin', 'ambassador']
    },
    {
      path: '/users',
      icon: Users,
      label: 'Usuários',
      roles: ['admin']
    }
  ];

  const filteredMenuItems = menuItems.filter(item => 
    item.roles.includes(user?.role)
  );

  const isActive = (path) => location.pathname === path;

  return (
    <>
      {/* Mobile menu button */}
      <div className="lg:hidden fixed top-4 left-4 z-50">
        <Button
          variant="outline"
          size="sm"
          onClick={toggleSidebar}
          className="bg-white shadow-md"
        >
          {isOpen ? <X size={20} /> : <Menu size={20} />}
        </Button>
      </div>

      {/* Overlay for mobile */}
      {isOpen && (
        <div 
          className="lg:hidden fixed inset-0 bg-black bg-opacity-50 z-40"
          onClick={toggleSidebar}
        />
      )}

      {/* Sidebar */}
      <div className={`
        fixed lg:static inset-y-0 left-0 z-50 w-64 bg-white shadow-lg transform transition-transform duration-300 ease-in-out
        ${isOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'}
      `}>
        <div className="flex flex-col h-full">
          {/* Header */}
          <div className="p-6 border-b border-gray-200">
            <h1 className="text-2xl font-bold text-gray-900">Beepy</h1>
            <p className="text-sm text-gray-600 mt-1">
              {user?.name || 'Usuário'}
            </p>
            <p className="text-xs text-gray-500 capitalize">
              {user?.role === 'admin' ? 'Administrador' : 'Embaixador'}
            </p>
          </div>

          {/* Navigation */}
          <nav className="flex-1 p-4 space-y-2">
            {filteredMenuItems.map((item) => {
              const Icon = item.icon;
              return (
                <Link
                  key={item.path}
                  to={item.path}
                  onClick={() => setIsOpen(false)}
                  className={`
                    flex items-center px-4 py-3 rounded-lg transition-colors duration-200
                    ${isActive(item.path)
                      ? 'bg-blue-100 text-blue-700 border border-blue-200'
                      : 'text-gray-700 hover:bg-gray-100'
                    }
                  `}
                >
                  <Icon size={20} className="mr-3" />
                  <span className="font-medium">{item.label}</span>
                </Link>
              );
            })}
          </nav>

          {/* Footer */}
          <div className="p-4 border-t border-gray-200">
            <Button
              variant="outline"
              onClick={handleLogout}
              className="w-full justify-start text-red-600 hover:text-red-700 hover:bg-red-50"
            >
              <LogOut size={20} className="mr-3" />
              Sair
            </Button>
          </div>
        </div>
      </div>
    </>
  );
};

export default Sidebar;

