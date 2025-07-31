import React, { useState } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import { Button } from ../ui/button';
import { LogOut, User, BarChart3, DollarSign, Users, TrendingUp } from 'lucide-react';
import AdminDashboard from '../AdminDashboard';
import CommissionsPage from './CommissionsPage';
import CommissionReports from './CommissionReports';

const AdminLayout = () => {
  const { user, logout } = useAuth();
  const [currentPage, setCurrentPage] = useState('dashboard');

  const handleLogout = () => {
    logout();
  };

  const menuItems = [
    {
      id: 'dashboard',
      label: 'Dashboard',
      icon: BarChart3,
      component: AdminDashboard
    },
    {
      id: 'commissions',
      label: 'Comissões',
      icon: DollarSign,
      component: CommissionsPage
    },
    {
      id: 'users',
      label: 'Usuários',
      icon: Users,
      component: () => <div>Página de usuários em desenvolvimento</div>
    },
    {
      id: 'reports',
      label: 'Relatórios',
      icon: TrendingUp,
      component: CommissionReports
    }
  ];

  const currentMenuItem = menuItems.find(item => item.id === currentPage);
  const CurrentComponent = currentMenuItem?.component || AdminDashboard;

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center">
              <div className="flex items-center space-x-2">
                <div className="w-8 h-8 bg-yellow-400 rounded-lg flex items-center justify-center">
                  <BarChart3 className="w-5 h-5 text-gray-900" />
                </div>
                <h1 className="text-xl font-bold text-gray-900">Beepy</h1>
              </div>
            </div>
            
            <div className="flex items-center space-x-4">
              <div className="flex items-center space-x-2">
                <User className="w-4 h-4 text-gray-500" />
                <span className="text-sm text-gray-700">{user?.name}</span>
                <span className="text-xs bg-gray-100 px-2 py-1 rounded-full text-gray-600">
                  {user?.user_type}
                </span>
              </div>
              <Button
                variant="outline"
                size="sm"
                onClick={handleLogout}
                className="flex items-center space-x-1"
              >
                <LogOut className="w-4 h-4" />
                <span>Sair</span>
              </Button>
            </div>
          </div>
        </div>
      </header>

      <div className="flex">
        {/* Sidebar */}
        <aside className="w-64 bg-white shadow-sm min-h-screen">
          <nav className="mt-8">
            <div className="px-4">
              <h2 className="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-4">
                Menu Principal
              </h2>
              <ul className="space-y-2">
                {menuItems.map((item) => {
                  const Icon = item.icon;
                  return (
                    <li key={item.id}>
                      <button
                        onClick={() => setCurrentPage(item.id)}
                        className={`w-full flex items-center px-3 py-2 text-sm font-medium rounded-md transition-colors ${
                          currentPage === item.id
                            ? 'bg-yellow-100 text-yellow-800 border-r-2 border-yellow-500'
                            : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
                        }`}
                      >
                        <Icon className="w-5 h-5 mr-3" />
                        {item.label}
                      </button>
                    </li>
                  );
                })}
              </ul>
            </div>
          </nav>
        </aside>

        {/* Main Content */}
        <main className="flex-1 px-8 py-8">
          <CurrentComponent />
        </main>
      </div>
    </div>
  );
};

export default AdminLayout;

