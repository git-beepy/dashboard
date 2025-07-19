// src/App.jsx
import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom'; // ✅ sem o BrowserRouter aqui
import Login from './components/Login';
import Dashboard from './components/Dashboard';
import Indications from './components/Indications';
import Commissions from './components/Commissions';
import Users from './components/Users';
import Sidebar from './components/Sidebar';
import PrivateRoute from './components/PrivateRoute';

function ProtectedRoutes() {
  return (
    <div className="flex h-screen bg-gray-100 overflow-hidden">
      <Sidebar />
      <div className="flex-1 overflow-auto lg:ml-0">
        <div className="lg:hidden h-16"></div>
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/indications" element={<Indications />} />
          <Route path="/commissions" element={<Commissions />} />
          <Route path="/users" element={<Users />} />
          <Route path="*" element={<Navigate to="/dashboard" replace />} />
        </Routes>
      </div>
    </div>
  );
}

function App() {
  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      <Route
        path="/*"
        element={
          <PrivateRoute>
            <ProtectedRoutes />
          </PrivateRoute>
        }
      />
    </Routes>
  );
}

export default App;
