import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import axios from 'axios';
import { Plus, Edit, Trash2, Check, X } from 'lucide-react';

const Indications = () => {
  const { user, API_BASE_URL } = useAuth();
  const [indications, setIndications] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [editingIndication, setEditingIndication] = useState(null);
  const [formData, setFormData] = useState({
    clientName: '',
    clientEmail: '',
    clientPhone: '',
    origin: 'website',
    segment: 'saude',
    customSegment: ''
  });

  useEffect(() => {
    fetchIndications();
  }, []);

  const fetchIndications = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/indications`);
      setIndications(response.data);
    } catch (error) {
      console.error('Erro ao buscar indicações:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    try {
      const submitData = { ...formData };
      
      // Se o segmento for "outro" e há um segmento customizado, usar o customizado
      if (formData.segment === 'outro' && formData.customSegment.trim()) {
        submitData.segment = formData.customSegment.trim();
      }
      
      // Remover o campo customSegment antes de enviar
      delete submitData.customSegment;
      
      if (editingIndication) {
        await axios.put(`${API_BASE_URL}/indications/${editingIndication.id}`, submitData);
      } else {
        await axios.post(`${API_BASE_URL}/indications`, submitData);
      }
      
      fetchIndications();
      setShowModal(false);
      setEditingIndication(null);
      setFormData({
        clientName: '',
        clientEmail: '',
        clientPhone: '',
        origin: 'website',
        segment: 'saude',
        customSegment: ''
      });
    } catch (error) {
      console.error('Erro ao salvar indicação:', error);
    }
  };

  const handleEdit = (indication) => {
    setEditingIndication(indication);
    
    // Verificar se o segmento é um dos padrões ou customizado
    const standardSegments = [
      'saude', 'educacao_pesquisa', 'juridico', 'administracao_negocios', 'engenharias',
      'tecnologia_informacao', 'financeiro_bancario', 'marketing_vendas_comunicacao',
      'industria_producao', 'construcao_civil', 'transportes_logistica', 'comercio_varejo',
      'turismo_hotelaria_eventos', 'gastronomia_alimentacao', 'agronegocio_meio_ambiente',
      'artes_cultura_design', 'midias_digitais_criativas', 'seguranca_defesa', 'servicos_gerais'
    ];
    const isStandardSegment = standardSegments.includes(indication.segment);
    
    setFormData({
      clientName: indication.clientName,
      clientEmail: indication.clientEmail,
      clientPhone: indication.clientPhone,
      origin: indication.origin,
      segment: isStandardSegment ? indication.segment : 'outro',
      customSegment: isStandardSegment ? '' : indication.segment
    });
    setShowModal(true);
  };

  const handleDelete = async (id) => {
    if (window.confirm('Tem certeza que deseja excluir esta indicação?')) {
      try {
        await axios.delete(`${API_BASE_URL}/indications/${id}`);
        fetchIndications();
      } catch (error) {
        console.error('Erro ao excluir indicação:', error);
      }
    }
  };

  const toggleConversion = async (indication) => {
    try {
      await axios.put(`${API_BASE_URL}/indications/${indication.id}`, {
        converted: !indication.converted
      });
      fetchIndications();
    } catch (error) {
      console.error('Erro ao atualizar conversão:', error);
    }
  };

  const updateIndicationStatus = async (indicationId, newStatus) => {
    try {
      await axios.put(`${API_BASE_URL}/indications/${indicationId}/status`, {
        status: newStatus
      });
      fetchIndications();
    } catch (error) {
      console.error('Erro ao atualizar status da indicação:', error);
      alert('Erro ao atualizar status da indicação');
    }
  };

  const closeModal = () => {
    setShowModal(false);
    setEditingIndication(null);
    setFormData({
      clientName: '',
      clientEmail: '',
      clientPhone: '',
      origin: 'website',
      segment: 'saude',
      customSegment: ''
    });
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

  return (
    <div className="p-6">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-bold text-gray-900">Indicações</h1>
        <button
          onClick={() => setShowModal(true)}
          className="bg-blue-600 text-white px-4 py-2 rounded-lg flex items-center space-x-2 hover:bg-blue-700"
        >
          <Plus className="h-4 w-4" />
          <span>Nova Indicação</span>
        </button>
      </div>

      {/* Tabela para desktop */}
      <div className="hidden lg:block bg-white rounded-lg shadow-md overflow-hidden">
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Cliente
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Contato
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Origem
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Segmento
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
              {indications.map((indication) => (
                <tr key={indication.id}>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div>
                      <div className="text-sm font-medium text-gray-900">
                        {indication.clientName}
                      </div>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm text-gray-900">{indication.clientEmail}</div>
                    <div className="text-sm text-gray-500">{indication.clientPhone}</div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-blue-100 text-blue-800">
                      {indication.origin}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {indication.segment}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    {user.role === 'admin' ? (
                      <select
                        value={indication.status || 'pendente'}
                        onChange={(e) => updateIndicationStatus(indication.id, e.target.value)}
                        className="px-2 py-1 text-xs font-semibold rounded-full border-0 bg-gray-100 focus:ring-2 focus:ring-blue-500"
                      >
                        <option value="agendado">Agendado</option>
                        <option value="aprovado">Aprovado</option>
                        <option value="não aprovado">Não Aprovado</option>
                      </select>
                    ) : (
                      <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${
                        indication.status === 'aprovado' ? 'bg-green-100 text-green-800' :
                        indication.status === 'não aprovado' ? 'bg-red-100 text-red-800' :
                        indication.status === 'agendado' ? 'bg-yellow-100 text-yellow-800' :
                        'bg-gray-100 text-gray-800'
                      }`}>
                        {indication.status || 'Pendente'}
                      </span>
                    )}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                    <div className="flex space-x-2">
                      <button
                        onClick={() => handleEdit(indication)}
                        className="text-blue-600 hover:text-blue-900"
                      >
                        <Edit className="h-4 w-4" />
                      </button>
                      {user.role === 'admin' && (
                        <button
                          onClick={() => handleDelete(indication.id)}
                          className="text-red-600 hover:text-red-900"
                        >
                          <Trash2 className="h-4 w-4" />
                        </button>
                      )}
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Cards para mobile */}
      <div className="lg:hidden space-y-4">
        {indications.map((indication) => (
          <div key={indication.id} className="bg-white rounded-lg shadow-md p-4">
            <div className="flex justify-between items-start mb-3">
              <div className="flex-1">
                <h3 className="text-lg font-medium text-gray-900">
                  {indication.clientName}
                </h3>
                <p className="text-sm text-gray-600">{indication.clientEmail}</p>
                <p className="text-xs text-gray-500">{indication.clientPhone}</p>
              </div>
              <div className="flex space-x-2 ml-4">
                <button
                  onClick={() => handleEdit(indication)}
                  className="text-blue-600 hover:text-blue-900 p-1"
                >
                  <Edit className="h-4 w-4" />
                </button>
                {user.role === 'admin' && (
                  <button
                    onClick={() => handleDelete(indication.id)}
                    className="text-red-600 hover:text-red-900 p-1"
                  >
                    <Trash2 className="h-4 w-4" />
                  </button>
                )}
              </div>
            </div>
            
            <div className="grid grid-cols-2 gap-3 text-sm">
              <div>
                <span className="text-gray-500">Origem:</span>
                <div className="mt-1">
                  <span className="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-blue-100 text-blue-800">
                    {indication.origin}
                  </span>
                </div>
              </div>
              
              <div>
                <span className="text-gray-500">Segmento:</span>
                <p className="text-gray-900 mt-1">{indication.segment}</p>
              </div>
              
              <div className="col-span-2">
                <span className="text-gray-500">Status:</span>
                <div className="mt-1">
                  {user.role === 'admin' ? (
                    <select
                      value={indication.status || 'pendente'}
                      onChange={(e) => updateIndicationStatus(indication.id, e.target.value)}
                      className="px-2 py-1 text-xs font-semibold rounded-full border-0 bg-gray-100 focus:ring-2 focus:ring-blue-500 w-full"
                    >
                      <option value="agendado">Agendado</option>
                      <option value="aprovado">Aprovado</option>
                      <option value="não aprovado">Não Aprovado</option>
                    </select>
                  ) : (
                    <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${
                      indication.status === 'aprovado' ? 'bg-green-100 text-green-800' :
                      indication.status === 'não aprovado' ? 'bg-red-100 text-red-800' :
                      indication.status === 'agendado' ? 'bg-yellow-100 text-yellow-800' :
                      'bg-gray-100 text-gray-800'
                    }`}>
                      {indication.status || 'Pendente'}
                    </span>
                  )}
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Modal */}
      {showModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg shadow-xl w-full max-w-md mx-4">
            {/* Header */}
            <div className="px-6 py-4 border-b border-gray-200">
              <h2 className="text-lg font-semibold text-gray-900">
                Nova Indicação
              </h2>
            </div>

            {/* Form */}
            <form onSubmit={handleSubmit} className="px-6 py-4 space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Nome do Cliente
                </label>
                <input
                  type="text"
                  required
                  value={formData.clientName}
                  onChange={(e) => setFormData({...formData, clientName: e.target.value})}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  placeholder=""
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Email
                </label>
                <input
                  type="email"
                  required
                  value={formData.clientEmail}
                  onChange={(e) => setFormData({...formData, clientEmail: e.target.value})}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  placeholder=""
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Telefone
                </label>
                <input
                  type="tel"
                  required
                  value={formData.clientPhone}
                  onChange={(e) => setFormData({...formData, clientPhone: e.target.value})}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  placeholder=""
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Origem
                </label>
                <select
                  value={formData.origin}
                  onChange={(e) => setFormData({...formData, origin: e.target.value})}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                >
                  <option value="website">Website</option>
                  <option value="social_media">Redes Sociais</option>
                  <option value="referral">Indicação</option>
                  <option value="event">Evento</option>
                  <option value="other">Outro</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Segmento
                </label>
                <select
                  value={formData.segment}
                  onChange={(e) => setFormData({...formData, segment: e.target.value, customSegment: ''})}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                >
                  <option value="saude">🏥 Saúde</option>
                  <option value="educacao_pesquisa">🧠 Educação e Pesquisa</option>
                  <option value="juridico">🏛️ Jurídico</option>
                  <option value="administracao_negocios">💼 Administração e Negócios</option>
                  <option value="engenharias">🏢 Engenharias</option>
                  <option value="tecnologia_informacao">💻 Tecnologia da Informação</option>
                  <option value="financeiro_bancario">🏦 Financeiro e Bancário</option>
                  <option value="marketing_vendas_comunicacao">📣 Marketing, Vendas e Comunicação</option>
                  <option value="industria_producao">🏭 Indústria e Produção</option>
                  <option value="construcao_civil">🧱 Construção Civil</option>
                  <option value="transportes_logistica">🚛 Transportes e Logística</option>
                  <option value="comercio_varejo">🛒 Comércio e Varejo</option>
                  <option value="turismo_hotelaria_eventos">🏨 Turismo, Hotelaria e Eventos</option>
                  <option value="gastronomia_alimentacao">🍳 Gastronomia e Alimentação</option>
                  <option value="agronegocio_meio_ambiente">🌱 Agronegócio e Meio Ambiente</option>
                  <option value="artes_cultura_design">🎭 Artes, Cultura e Design</option>
                  <option value="midias_digitais_criativas">📱 Mídias Digitais e Criativas</option>
                  <option value="seguranca_defesa">👮 Segurança e Defesa</option>
                  <option value="servicos_gerais">🧹 Serviços Gerais</option>
                  <option value="outro">Outro (especificar)</option>
                </select>
              </div>

              {formData.segment === 'outro' && (
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Especificar Segmento
                  </label>
                  <input
                    type="text"
                    required
                    value={formData.customSegment}
                    onChange={(e) => setFormData({...formData, customSegment: e.target.value})}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    placeholder="Digite o segmento específico"
                  />
                </div>
              )}
            </form>

            {/* Footer */}
            <div className="px-6 py-4 border-t border-gray-200 flex justify-end space-x-3">
              <button
                type="button"
                onClick={closeModal}
                className="px-4 py-2 text-sm font-medium text-gray-700 bg-gray-100 border border-gray-300 rounded-md hover:bg-gray-200 focus:outline-none focus:ring-2 focus:ring-gray-500"
              >
                Cancelar
              </button>
              <button
                type="submit"
                onClick={handleSubmit}
                className="px-4 py-2 text-sm font-medium text-white bg-blue-600 border border-transparent rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                Criar
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Indications;

