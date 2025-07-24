import React, { useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { useAuth } from "../contexts/AuthContext";
import { 
  LayoutDashboard, 
  Users, 
  DollarSign, 
  LogOut,
  UserCheck,
  Menu,
  X
} from 'lucide-react';

const Sidebar = () => {
  const { user, logout } = useAuth();
  const location = useLocation();
  const [isCollapsed, setIsCollapsed] = useState(false);
  const [isMobileOpen, setIsMobileOpen] = useState(false);

  const menuItems = [
    {
      name: 'Dashboard',
      icon: LayoutDashboard,
      path: '/dashboard',
      roles: ['admin', 'embaixadora']
    },
    {
      name: 'Indicações',
      icon: Users,
      path: '/indications',
      roles: ['admin', 'embaixadora']
    },
    {
      name: 'Comissões',
      icon: DollarSign,
      path: '/commissions',
      roles: ['admin', 'embaixadora']
    },
    {
      name: 'Usuários',
      icon: UserCheck,
      path: '/users',
      roles: ['admin']
    }
  ];

  const filteredMenuItems = menuItems.filter(item => 
    item.roles.includes(user?.role)
  );

  const toggleSidebar = () => {
    setIsCollapsed(!isCollapsed);
  };

  const toggleMobileSidebar = () => {
    setIsMobileOpen(!isMobileOpen);
  };

  return (
    <>
      {/* Mobile Menu Button */}
      <button
        onClick={toggleMobileSidebar}
        className={`lg:hidden fixed z-50 p-2 bg-orange-500 text-white rounded-lg shadow-lg transition-all duration-300 ${
          isMobileOpen ? 'top-4 right-4' : 'top-4 left-4'
        }`}
      >
        {isMobileOpen ? <X className="h-6 w-6" /> : <Menu className="h-6 w-6" />}
      </button>

      {/* Mobile Overlay */}
      {isMobileOpen && (
        <div 
          className="lg:hidden fixed inset-0 bg-black bg-opacity-50 z-40"
          onClick={toggleMobileSidebar}
        />
      )}

      {/* Sidebar */}
      <div className={`
        sidebar-dark text-white min-h-screen flex flex-col transition-all duration-300 z-40
        ${isCollapsed ? 'w-16' : 'w-64'}
        ${isMobileOpen ? 'fixed' : 'hidden lg:flex'}
        lg:relative lg:flex
      `}>
        {/* Logo */}
        <div className="p-6 border-b border-gray-700">
          <div className="flex items-center space-x-3">
            <button
              onClick={toggleSidebar}
              className="hidden lg:block p-1 hover:bg-gray-700 rounded transition-colors"
            >
              <Menu className="h-8 w-8 text-orange-400" />
            </button>
            {!isCollapsed && (
              <div>
                <h1 className="text-xl font-bold text-white">beepy</h1>
                <p className="text-gray-400 text-sm">gestão</p>
              </div>
            )}
          </div>
        </div>

        {/* Navigation */}
        <nav className="flex-1 p-4">
          <ul className="space-y-2">
            {filteredMenuItems.map((item) => {
              const Icon = item.icon;
              const isActive = location.pathname === item.path;
              
              return (
                <li key={item.path}>
                  <Link
                    to={item.path}
                    onClick={() => setIsMobileOpen(false)}
                    className={`flex items-center space-x-3 p-3 rounded-lg transition-all duration-200 group ${
                      isActive
                        ? 'bg-orange-500 text-white shadow-lg'
                        : 'text-gray-300 hover:bg-gray-800 hover:text-white'
                    }`}
                    title={isCollapsed ? item.name : ''}
                  >
                    <Icon className="h-5 w-5 flex-shrink-0" />
                    {!isCollapsed && (
                      <span className="font-medium">{item.name}</span>
                    )}
                  </Link>
                </li>
              );
            })}
          </ul>
        </nav>

        {/* User Info & Logout */}
        <div className="p-4 border-t border-gray-700">
          {!isCollapsed && (
            <div className="mb-4 p-3 bg-gray-800 rounded-lg">
              <div className="flex items-center space-x-3">
                <div className="w-10 h-10 bg-orange-500 rounded-full flex items-center justify-center flex-shrink-0">
                  <span className="text-white font-bold text-sm">
                    {user?.name?.charAt(0)?.toUpperCase() || user?.email?.charAt(0)?.toUpperCase()}
                  </span>
                </div>
                <div className="flex-1 min-w-0">
                  <p className="font-medium text-white truncate">{user?.name || user?.email}</p>
                  <p className="text-sm text-gray-400 capitalize">{user?.role}</p>
                </div>
              </div>
            </div>
          )}
          
          <button
            onClick={logout}
            className={`flex items-center p-3 w-full text-gray-300 hover:bg-gray-800 hover:text-white rounded-lg transition-colors ${
              isCollapsed ? 'justify-center' : 'space-x-3'
            }`}
            title={isCollapsed ? 'Logout' : ''}
          >
            <LogOut className="h-5 w-5 flex-shrink-0" />
            {!isCollapsed && <span>Logout</span>}
          </button>
        </div>
      </div>
    </>
  );
};

export default Sidebar;

