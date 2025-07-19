import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import axios from 'axios';
import { Plus, Edit, Trash2, DollarSign } from 'lucide-react';

const Commissions = () => {
  const { user, API_BASE_URL } = useAuth();
  const [commissions, setCommissions] = useState([]);
  const [indications, setIndications] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [editingCommission, setEditingCommission] = useState(null);
  const [formData, setFormData] = useState({
    ambassadorId: '',
    indicationId: '',
    value: '',
    status: 'pending'
  });

  useEffect(() => {
    fetchCommissions();
    fetchIndications();
  }, []);

  const fetchCommissions = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/commissions`);
      setCommissions(response.data);
    } catch (error) {
      console.error('Erro ao buscar comissões:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchIndications = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/indications`);
      setIndications(response.data.filter(ind => ind.converted));
    } catch (error) {
      console.error('Erro ao buscar indicações:', error);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    try {
      if (editingCommission) {
        await axios.put(`${API_BASE_URL}/commissions/${editingCommission.id}`, formData);
      } else {
        await axios.post(`${API_BASE_URL}/commissions`, formData);
      }

      fetchCommissions();
      setShowModal(false);
      setEditingCommission(null);
      setFormData({
        ambassadorId: '',
        indicationId: '',
        value: '',
        status: 'pending'
      });
    } catch (error) {
      console.error('Erro ao salvar comissão:', error);
    }
  };

  const handleEdit = (commission) => {
    setEditingCommission(commission);
    setFormData({
      ambassadorId: commission.ambassadorId,
      indicationId: commission.indicationId,
      value: commission.value,
      status: commission.status
    });
    setShowModal(true);
  };

  const handleDelete = async (id) => {
    if (window.confirm('Tem certeza que deseja excluir esta comissão?')) {
      try {
        await axios.delete(`${API_BASE_URL}/commissions/${id}`);
        fetchCommissions();
      } catch (error) {
        console.error('Erro ao excluir comissão:', error);
      }
    }
  };

  const toggleStatus = async (commission) => {
    try {
      const newStatus = commission.status === 'paid' ? 'pending' : 'paid';
      await axios.put(`${API_BASE_URL}/commissions/${commission.id}`, {
        status: newStatus
      });
      fetchCommissions();
    } catch (error) {
      console.error('Erro ao atualizar status:', error);
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'paid':
        return 'bg-green-100 text-green-800';
      case 'pending':
        return 'bg-yellow-100 text-yellow-800';
      case 'cancelled':
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const getStatusText = (status) => {
    switch (status) {
      case 'paid':
        return 'Paga';
      case 'pending':
        return 'Pendente';
      case 'cancelled':
        return 'Cancelada';
      default:
        return status;
    }
  };

  if (loading) {
    return (
      <div className="p-6">
        <div className="animate-pulse">
          <div className="h-8 bg-gray-200 rounded w-1/4 mb-6"></div>
          <div className="h-64 bg-gray-200 rounded"></div>
        </div>
      </div>
    );
  }

  const totalCommissions = commissions.reduce((sum, comm) => sum + (comm.value || 0), 0);
  const paidCommissions = commissions
    .filter(comm => comm.status === 'paid')
    .reduce((sum, comm) => sum + (comm.value || 0), 0);
  const pendingCommissions = commissions
    .filter(comm => comm.status === 'pending')
    .reduce((sum, comm) => sum + (comm.value || 0), 0);

  return (
    <div className="p-6">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-bold text-gray-900">Comissões</h1>
        {user.role === 'admin' && (
          <button
            onClick={() => setShowModal(true)}
            className="bg-blue-600 text-white px-4 py-2 rounded-lg flex items-center space-x-2 hover:bg-blue-700"
          >
            <Plus className="h-4 w-4" />
            <span>Nova Comissão</span>
          </button>
        )}
      </div>

      {/* Cards de resumo */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
        <div className="bg-white p-6 rounded-lg shadow-md">
          <div className="flex items-center">
            <DollarSign className="h-8 w-8 text-blue-600" />
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Total Comissões</p>
              <p className="text-2xl font-bold text-gray-900">
                R$ {totalCommissions.toLocaleString()}
              </p>
            </div>
          </div>
        </div>

        <div className="bg-white p-6 rounded-lg shadow-md">
          <div className="flex items-center">
            <DollarSign className="h-8 w-8 text-green-600" />
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Pagas</p>
              <p className="text-2xl font-bold text-gray-900">
                R$ {paidCommissions.toLocaleString()}
              </p>
            </div>
          </div>
        </div>

        <div className="bg-white p-6 rounded-lg shadow-md">
          <div className="flex items-center">
            <DollarSign className="h-8 w-8 text-yellow-600" />
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Pendentes</p>
              <p className="text-2xl font-bold text-gray-900">
                R$ {pendingCommissions.toLocaleString()}
              </p>
            </div>
          </div>
        </div>
      </div>

      <div className="bg-white rounded-lg shadow-md overflow-hidden">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Embaixadora
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Indicação
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Valor
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Status
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Ações
              </th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {commissions.map((commission) => {
              const indication = indications.find(ind => ind.id === commission.indicationId);

              return (
                <tr key={commission.id}>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm font-medium text-gray-900">
                      {commission.ambassadorId}
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm text-gray-900">
                      {indication?.clientName || 'N/A'}
                    </div>
                    <div className="text-sm text-gray-500">
                      {indication?.clientEmail || ''}
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm font-medium text-gray-900">
                      R$ {(commission.value || 0).toLocaleString()}
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <button
                      onClick={() => user.role === 'admin' && toggleStatus(commission)}
                      className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${getStatusColor(commission.status)} ${
                        user.role === 'admin' ? 'cursor-pointer hover:opacity-80' : 'cursor-default'
                      }`}
                    >
                      {getStatusText(commission.status)}
                    </button>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                    {user.role === 'admin' && (
                      <div className="flex space-x-2">
                        <button
                          onClick={() => handleEdit(commission)}
                          className="text-blue-600 hover:text-blue-900"
                        >
                          <Edit className="h-4 w-4" />
                        </button>
                        <button
                          onClick={() => handleDelete(commission.id)}
                          className="text-red-600 hover:text-red-900"
                        >
                          <Trash2 className="h-4 w-4" />
                        </button>
                      </div>
                    )}
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>

      {/* Modal */}
      {showModal && user.role === 'admin' && (
        <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
          <div className="relative top-20 mx-auto p-5 border w-96 shadow-lg rounded-md bg-white">
            <div className="mt-3">
              <h3 className="text-lg font-medium text-gray-900 mb-4">
                {editingCommission ? 'Editar Comissão' : 'Nova Comissão'}
              </h3>

              <form onSubmit={handleSubmit} className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700">
                    ID da Embaixadora
                  </label>
                  <input
                    type="text"
                    required
                    value={formData.ambassadorId}
                    onChange={(e) => setFormData({...formData, ambassadorId: e.target.value})}
                    className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700">
                    Indicação
                  </label>
                  <select
                    required
                    value={formData.indicationId}
                    onChange={(e) => setFormData({...formData, indicationId: e.target.value})}
                    className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                  >
                    <option value="">Selecione uma indicação</option>
                    {indications.map((indication) => (
                      <option key={indication.id} value={indication.id}>
                        {indication.clientName} - {indication.clientEmail}
                      </option>
                    ))}
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700">
                    Valor
                  </label>
                  <input
                    type="number"
                    step="0.01"
                    required
                    value={formData.value}
                    onChange={(e) => setFormData({...formData, value: parseFloat(e.target.value)})}
                    className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700">
                    Status
                  </label>
                  <select
                    value={formData.status}
                    onChange={(e) => setFormData({...formData, status: e.target.value})}
                    className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                  >
                    <option value="pending">Pendente</option>
                    <option value="paid">Paga</option>
                    <option value="cancelled">Cancelada</option>
                  </select>
                </div>

                <div className="flex justify-end space-x-3 pt-4">
                  <button
                    type="button"
                    onClick={() => {
                      setShowModal(false);
                      setEditingCommission(null);
                      setFormData({
                        ambassadorId: '',
                        indicationId: '',
                        value: '',
                        status: 'pending'
                      });
                    }}
                    className="px-4 py-2 text-sm font-medium text-gray-700 bg-gray-200 rounded-md hover:bg-gray-300"
                  >
                    Cancelar
                  </button>
                  <button
                    type="submit"
                    className="px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-md hover:bg-blue-700"
                  >
                    {editingCommission ? 'Atualizar' : 'Criar'}
                  </button>
                </div>
              </form>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Commissions;

