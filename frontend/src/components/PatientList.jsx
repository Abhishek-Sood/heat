import { useState, useEffect } from 'react';
import { patientsAPI, authAPI } from '../services/api';

const PatientList = ({ onSelectPatient, selectedPatientId }) => {
  const [patients, setPatients] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [showAddForm, setShowAddForm] = useState(false);
  const [newPatient, setNewPatient] = useState({
    name: '',
    dob: '',
    gender: '',
    contact: '',
    address: ''
  });
  const [adding, setAdding] = useState(false);

  useEffect(() => {
    fetchPatients();
    
    // Debug: Test auth and connection (removed - don't use localhost in production)
  }, []);

  const fetchPatients = async () => {
    try {
      setLoading(true);
      
      // Debug: Check current user
      const currentUser = authAPI.getCurrentUser();
      console.log('Current authenticated user:', currentUser);
      
      const response = await patientsAPI.getPatients();
      console.log('Fetched patients response:', response); // Debug log
      // API service now returns { data: [...] } with patients array
      setPatients(response.data || []);
      setError(null);
    } catch (err) {
      console.error('Error fetching patients:', err);
      setError('Failed to load patients');
      setPatients([]);
    } finally {
      setLoading(false);
    }
  };

  const handleAddPatient = async (e) => {
    e.preventDefault();
    if (!newPatient.name || !newPatient.dob || !newPatient.gender) {
      alert('Please fill in all required fields');
      return;
    }

    setAdding(true);
    try {
      console.log('Adding patient:', newPatient); // Debug log
      const result = await patientsAPI.addPatient(newPatient);
      console.log('Add patient result:', result); // Debug log
      
      setNewPatient({
        name: '',
        dob: '',
        gender: '',
        contact: '',
        address: ''
      });
      setShowAddForm(false);
      
      // Wait a moment before refreshing to ensure database commit
      setTimeout(async () => {
        await fetchPatients(); // Refresh the list
      }, 100);
      
    } catch (err) {
      console.error('Error adding patient:', err);
      alert(`Failed to add patient: ${err.response?.data?.detail || err.message}`);
    } finally {
      setAdding(false);
    }
  };

  const filteredPatients = (Array.isArray(patients) ? patients : []).filter(patient =>
    patient.name?.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const formatDate = (dateStr) => {
    if (!dateStr) return 'N/A';
    try {
      return new Date(dateStr).toLocaleDateString();
    } catch {
      return dateStr;
    }
  };

  const getAvatarColor = (name) => {
    const colors = [
      'from-blue-400 to-blue-600',
      'from-teal-400 to-teal-600',
      'from-purple-400 to-purple-600',
      'from-pink-400 to-pink-600',
      'from-indigo-400 to-indigo-600',
      'from-cyan-400 to-cyan-600',
    ];
    const index = (name?.charCodeAt(0) || 0) % colors.length;
    return colors[index];
  };

  if (loading) {
    return (
      <div className="h-full flex flex-col items-center justify-center bg-gradient-to-b from-white to-gray-50">
        <div className="relative">
          <div className="w-14 h-14 border-4 border-blue-100 rounded-full"></div>
          <div className="absolute top-0 w-14 h-14 border-4 border-transparent border-t-blue-600 rounded-full animate-spin"></div>
        </div>
        <p className="mt-4 text-sm text-gray-500 font-medium animate-pulse">Loading patients...</p>
      </div>
    );
  }

  return (
    <div className="h-full flex flex-col bg-gradient-to-b from-white to-gray-50/50">
      {/* Header */}
      <div className="p-4 border-b border-gray-100">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-blue-500 to-indigo-600 flex items-center justify-center shadow-glow-sm">
              <svg className="h-5 w-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
              </svg>
            </div>
            <div>
              <h2 className="text-lg font-bold text-gradient">Patients</h2>
              <p className="text-xs text-gray-500">{filteredPatients.length} registered</p>
            </div>
          </div>
          <button
            onClick={() => setShowAddForm(!showAddForm)}
            className={`
              px-4 py-2 text-sm font-medium rounded-xl transition-all duration-300
              ${showAddForm 
                ? 'bg-gray-100 text-gray-600 hover:bg-gray-200' 
                : 'bg-gradient-to-r from-blue-500 to-indigo-600 text-white shadow-glow-sm hover:shadow-glow-md hover:scale-105'
              }
              active:scale-95
            `}
          >
            {showAddForm ? (
              <span className="flex items-center space-x-1">
                <svg className="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
                <span>Cancel</span>
              </span>
            ) : (
              <span className="flex items-center space-x-1">
                <svg className="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
                </svg>
                <span>Add Patient</span>
              </span>
            )}
          </button>
        </div>
        
        {/* Search Input */}
        <div className="relative group">
          <input
            type="text"
            placeholder="Search patients..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full px-4 py-3 pl-11 bg-white border-2 border-gray-100 rounded-xl text-sm 
              focus:outline-none focus:border-blue-500 focus:ring-4 focus:ring-blue-500/10
              transition-all duration-300 placeholder-gray-400"
          />
          <svg
            className="absolute left-4 top-1/2 -translate-y-1/2 h-5 w-5 text-gray-400 group-focus-within:text-blue-500 transition-colors"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
            />
          </svg>
          {searchTerm && (
            <button
              onClick={() => setSearchTerm('')}
              className="absolute right-3 top-1/2 -translate-y-1/2 p-1 hover:bg-gray-100 rounded-lg transition-colors"
            >
              <svg className="h-4 w-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          )}
        </div>
      </div>

      {/* Add Patient Form */}
      {showAddForm && (
        <div className="p-4 border-b border-gray-100 bg-gradient-to-r from-blue-50/50 to-indigo-50/50 animate-fade-in-down">
          <form onSubmit={handleAddPatient} className="space-y-3">
            <input
              type="text"
              placeholder="Patient Name *"
              value={newPatient.name}
              onChange={(e) => setNewPatient({...newPatient, name: e.target.value})}
              className="w-full px-4 py-2.5 bg-white border-2 border-gray-100 rounded-xl text-sm 
                focus:outline-none focus:border-blue-500 focus:ring-4 focus:ring-blue-500/10 transition-all"
              required
            />
            <div className="grid grid-cols-2 gap-3">
              <input
                type="date"
                placeholder="Date of Birth *"
                value={newPatient.dob}
                onChange={(e) => setNewPatient({...newPatient, dob: e.target.value})}
                className="px-4 py-2.5 bg-white border-2 border-gray-100 rounded-xl text-sm 
                  focus:outline-none focus:border-blue-500 focus:ring-4 focus:ring-blue-500/10 transition-all"
                required
              />
              <select
                value={newPatient.gender}
                onChange={(e) => setNewPatient({...newPatient, gender: e.target.value})}
                className="px-4 py-2.5 bg-white border-2 border-gray-100 rounded-xl text-sm 
                  focus:outline-none focus:border-blue-500 focus:ring-4 focus:ring-blue-500/10 transition-all
                  select-modern"
                required
              >
                <option value="">Gender *</option>
                <option value="male">Male</option>
                <option value="female">Female</option>
                <option value="other">Other</option>
              </select>
            </div>
            <input
              type="text"
              placeholder="Contact Number"
              value={newPatient.contact}
              onChange={(e) => setNewPatient({...newPatient, contact: e.target.value})}
              className="w-full px-4 py-2.5 bg-white border-2 border-gray-100 rounded-xl text-sm 
                focus:outline-none focus:border-blue-500 focus:ring-4 focus:ring-blue-500/10 transition-all"
            />
            <textarea
              placeholder="Address"
              value={newPatient.address}
              onChange={(e) => setNewPatient({...newPatient, address: e.target.value})}
              className="w-full px-4 py-2.5 bg-white border-2 border-gray-100 rounded-xl text-sm 
                focus:outline-none focus:border-blue-500 focus:ring-4 focus:ring-blue-500/10 transition-all resize-none"
              rows={2}
            />
            <button
              type="submit"
              disabled={adding}
              className="w-full py-3 bg-gradient-to-r from-green-500 to-emerald-600 text-white font-medium 
                rounded-xl shadow-glow-green transition-all duration-300 
                hover:shadow-glow-green hover:scale-[1.02] active:scale-[0.98]
                disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:scale-100"
            >
              {adding ? (
                <span className="flex items-center justify-center space-x-2">
                  <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin"></div>
                  <span>Adding Patient...</span>
                </span>
              ) : (
                <span className="flex items-center justify-center space-x-2">
                  <svg className="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M18 9v3m0 0v3m0-3h3m-3 0h-3m-2-5a4 4 0 11-8 0 4 4 0 018 0zM3 20a6 6 0 0112 0v1H3v-1z" />
                  </svg>
                  <span>Add Patient</span>
                </span>
              )}
            </button>
          </form>
        </div>
      )}

      {/* Patient List */}
      <div className="flex-1 overflow-y-auto scrollbar-hide">
        {error ? (
          <div className="p-6 text-center animate-fade-in">
            <div className="w-16 h-16 mx-auto mb-4 rounded-full bg-red-50 flex items-center justify-center">
              <svg className="h-8 w-8 text-red-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <p className="text-red-600 font-medium">{error}</p>
            <button
              onClick={fetchPatients}
              className="mt-3 px-4 py-2 text-sm text-blue-600 hover:text-blue-700 font-medium 
                hover:bg-blue-50 rounded-lg transition-colors"
            >
              Try again
            </button>
          </div>
        ) : filteredPatients.length === 0 ? (
          <div className="p-6 text-center animate-fade-in">
            <div className="w-16 h-16 mx-auto mb-4 rounded-full bg-gray-100 flex items-center justify-center">
              <svg className="h-8 w-8 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0z" />
              </svg>
            </div>
            <p className="text-gray-500 font-medium">
              {searchTerm ? 'No patients found' : 'No patients available'}
            </p>
            {searchTerm && (
              <p className="text-sm text-gray-400 mt-1">Try a different search term</p>
            )}
          </div>
        ) : (
          <ul className="p-3 space-y-2">
            {filteredPatients.map((patient, index) => (
              <li
                key={patient.id}
                onClick={() => onSelectPatient(patient)}
                className={`
                  p-4 cursor-pointer rounded-xl transition-all duration-300
                  hover:shadow-card-hover hover:scale-[1.02] active:scale-[0.98]
                  animate-fade-in
                  ${selectedPatientId === patient.id
                    ? 'bg-gradient-to-r from-blue-500 to-indigo-600 text-white shadow-glow-sm'
                    : 'bg-white hover:bg-gray-50 border border-gray-100'
                  }
                `}
                style={{ animationDelay: `${index * 50}ms` }}
              >
                <div className="flex items-center space-x-4">
                  {/* Avatar */}
                  <div className="flex-shrink-0 relative">
                    <div className={`
                      h-12 w-12 rounded-xl flex items-center justify-center shadow-sm
                      ${selectedPatientId === patient.id 
                        ? 'bg-white/20' 
                        : `bg-gradient-to-br ${getAvatarColor(patient.name)}`
                      }
                    `}>
                      <span className={`font-bold text-lg ${selectedPatientId === patient.id ? 'text-white' : 'text-white'}`}>
                        {patient.name?.charAt(0)?.toUpperCase() || '?'}
                      </span>
                    </div>
                    {/* Online indicator */}
                    <div className={`absolute -bottom-1 -right-1 w-4 h-4 rounded-full border-2 
                      ${selectedPatientId === patient.id ? 'border-blue-500' : 'border-white'}
                      bg-green-400
                    `}></div>
                  </div>
                  
                  {/* Info */}
                  <div className="flex-1 min-w-0">
                    <p className={`font-semibold truncate ${selectedPatientId === patient.id ? 'text-white' : 'text-gray-900'}`}>
                      {patient.name || 'Unknown'}
                    </p>
                    <div className={`flex items-center space-x-2 text-xs mt-1 ${selectedPatientId === patient.id ? 'text-blue-100' : 'text-gray-500'}`}>
                      {patient.gender && (
                        <span className={`px-2 py-0.5 rounded-full capitalize ${
                          selectedPatientId === patient.id 
                            ? 'bg-white/20' 
                            : 'bg-gray-100'
                        }`}>
                          {patient.gender}
                        </span>
                      )}
                      {patient.dob && (
                        <>
                          <span>•</span>
                          <span>{formatDate(patient.dob)}</span>
                        </>
                      )}
                    </div>
                  </div>
                  
                  {/* Arrow indicator */}
                  <svg
                    className={`h-5 w-5 transition-transform duration-300 ${
                      selectedPatientId === patient.id 
                        ? 'text-white translate-x-1' 
                        : 'text-gray-300 group-hover:translate-x-1'
                    }`}
                    fill="currentColor"
                    viewBox="0 0 20 20"
                  >
                    <path
                      fillRule="evenodd"
                      d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z"
                      clipRule="evenodd"
                    />
                  </svg>
                </div>
              </li>
            ))}
          </ul>
        )}
      </div>

      {/* Footer */}
      <div className="p-4 border-t border-gray-100 bg-white/80 backdrop-blur-sm">
        <div className="flex items-center justify-between">
          <p className="text-xs text-gray-500">
            <span className="font-medium text-gray-700">{filteredPatients.length}</span> patient{filteredPatients.length !== 1 ? 's' : ''} total
          </p>
          <button
            onClick={fetchPatients}
            className="p-2 hover:bg-gray-100 rounded-lg transition-colors group"
            title="Refresh"
          >
            <svg className="h-4 w-4 text-gray-400 group-hover:text-blue-500 transition-colors" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
            </svg>
          </button>
        </div>
      </div>
    </div>
  );
};

export default PatientList;
