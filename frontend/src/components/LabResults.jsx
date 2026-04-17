import { useState, useEffect } from 'react';
import { labAPI } from '../services/api';

const LabResults = ({ patient }) => {
  const [labResults, setLabResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (patient?.id) {
      fetchLabResults();
    } else {
      setLabResults([]);
    }
  }, [patient?.id]);

  const fetchLabResults = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await labAPI.getLabResults(patient.id);
      
      let results = [];
      if (response.results) {
        results = response.results;
      } else if (Array.isArray(response)) {
        results = response;
      } else {
        results = [];
      }
      
      setLabResults(results);
    } catch (err) {
      console.error('Error fetching lab results:', err);
      
      if (err.response?.status === 503) {
        setError('Database service is temporarily unavailable.');
      } else if (err.response?.status === 404) {
        setError('No lab results found for this patient.');
        setLabResults([]);
      } else if (err.response?.status >= 500) {
        setError('Server error. Please try again later.');
      } else {
        setError('Failed to load lab results.');
      }
      
      if (err.response?.status !== 404) {
        setLabResults([]);
      }
    } finally {
      setLoading(false);
    }
  };

  const formatDate = (dateStr) => {
    if (!dateStr) return 'N/A';
    try {
      return new Date(dateStr).toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
      });
    } catch {
      return dateStr;
    }
  };

  const getStatusConfig = (status) => {
    switch (status) {
      case 'normal':
        return { 
          bg: 'bg-gradient-to-r from-green-50 to-emerald-50', 
          text: 'text-green-700', 
          icon: '✓',
          label: 'Normal',
          gradient: 'from-green-400 to-emerald-500',
          border: 'border-green-200',
          iconBg: 'bg-green-100',
          glow: 'shadow-glow-green'
        };
      case 'high':
        return { 
          bg: 'bg-gradient-to-r from-red-50 to-rose-50', 
          text: 'text-red-700', 
          icon: '↑',
          label: 'High',
          gradient: 'from-red-400 to-rose-500',
          border: 'border-red-200',
          iconBg: 'bg-red-100',
          glow: 'hover:shadow-red-200/50'
        };
      case 'low':
        return { 
          bg: 'bg-gradient-to-r from-amber-50 to-orange-50', 
          text: 'text-amber-700', 
          icon: '↓',
          label: 'Low',
          gradient: 'from-amber-400 to-orange-500',
          border: 'border-amber-200',
          iconBg: 'bg-amber-100',
          glow: 'hover:shadow-amber-200/50'
        };
      default:
        return { 
          bg: 'bg-gradient-to-r from-gray-50 to-slate-50', 
          text: 'text-gray-700', 
          icon: '?',
          label: 'N/A',
          gradient: 'from-gray-400 to-slate-500',
          border: 'border-gray-200',
          iconBg: 'bg-gray-100',
          glow: ''
        };
    }
  };

  if (!patient) {
    return (
      <div className="h-full flex flex-col items-center justify-center bg-gradient-mesh p-8">
        <div className="relative">
          <div className="w-28 h-28 rounded-3xl bg-gradient-to-br from-purple-100 to-blue-100 
            flex items-center justify-center mb-8 animate-float shadow-glass animate-pulse-soft">
            <svg className="h-14 w-14 text-purple-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} 
                d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
          </div>
          {/* Decorative elements */}
          <div className="absolute -top-4 -right-4 w-8 h-8 rounded-full bg-gradient-to-br from-teal-400 to-blue-500 opacity-60 animate-bounce-gentle"></div>
          <div className="absolute -bottom-2 -left-4 w-6 h-6 rounded-full bg-gradient-to-br from-purple-400 to-pink-500 opacity-60 animate-bounce-gentle" style={{ animationDelay: '0.5s' }}></div>
        </div>
        <h3 className="text-2xl font-bold text-gradient mb-3">No Patient Selected</h3>
        <p className="text-gray-500 text-center max-w-sm leading-relaxed">
          Select a patient from the list to view their lab results and clinical data.
        </p>
        <div className="mt-6 flex items-center space-x-2 text-sm text-gray-400">
          <svg className="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 19l-7-7m0 0l7-7m-7 7h18" />
          </svg>
          <span>Select from the patient list</span>
        </div>
      </div>
    );
  }

  return (
    <div className="h-full flex flex-col bg-gradient-to-b from-white to-gray-50/50">
      {/* Header */}
      <div className="p-4 border-b border-gray-100 bg-white/80 backdrop-blur-sm">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-purple-500 to-indigo-600 
              flex items-center justify-center shadow-glow-sm">
              <span className="text-2xl">🧪</span>
            </div>
            <div>
              <h2 className="text-xl font-bold text-gradient">Lab Results</h2>
              <p className="text-sm text-gray-500 flex items-center mt-0.5">
                <span className="w-2 h-2 rounded-full bg-green-400 mr-2 animate-pulse"></span>
                <span className="font-medium text-gray-700">{patient.name}</span>
              </p>
            </div>
          </div>
          <button
            onClick={fetchLabResults}
            disabled={loading}
            className="p-3 text-gray-500 hover:text-blue-600 bg-white hover:bg-blue-50 
              rounded-xl transition-all duration-300 hover:shadow-card hover:scale-105 
              active:scale-95 disabled:opacity-50 border border-gray-100"
            title="Refresh"
          >
            <svg className={`h-5 w-5 ${loading ? 'animate-spin' : ''}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} 
                d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
            </svg>
          </button>
        </div>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-y-auto p-4 scrollbar-hide">
        {loading ? (
          <div className="flex flex-col items-center justify-center h-full">
            <div className="relative">
              <div className="w-16 h-16 border-4 border-purple-100 rounded-full"></div>
              <div className="absolute top-0 w-16 h-16 border-4 border-transparent border-t-purple-500 rounded-full animate-spin"></div>
            </div>
            <div className="mt-6 text-center">
              <p className="text-sm text-gray-600 font-medium">Loading lab results...</p>
              <div className="flex justify-center space-x-1 mt-3">
                <div className="typing-dot" style={{ animationDelay: '0s' }}></div>
                <div className="typing-dot" style={{ animationDelay: '0.2s' }}></div>
                <div className="typing-dot" style={{ animationDelay: '0.4s' }}></div>
              </div>
            </div>
          </div>
        ) : error ? (
          <div className="flex flex-col items-center justify-center h-full p-6 animate-fade-in">
            <div className="w-20 h-20 rounded-2xl bg-gradient-to-br from-red-100 to-rose-100 flex items-center justify-center mb-6 shadow-lg">
              <svg className="w-10 h-10 text-red-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} 
                  d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <p className="text-red-600 font-semibold text-center text-lg">{error}</p>
            <button onClick={fetchLabResults} 
              className="mt-6 px-6 py-3 bg-gradient-to-r from-blue-500 to-indigo-600 text-white 
                font-medium rounded-xl shadow-glow-sm hover:shadow-glow-md transition-all 
                duration-300 hover:scale-105 active:scale-95">
              Try again
            </button>
          </div>
        ) : labResults.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full p-6 animate-fade-in">
            <div className="w-20 h-20 rounded-2xl bg-gradient-to-br from-gray-100 to-slate-100 flex items-center justify-center mb-6 shadow-lg">
              <svg className="w-10 h-10 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} 
                  d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
            </div>
            <p className="text-gray-600 font-semibold text-lg">No lab results available</p>
            <p className="text-sm text-gray-400 mt-2">Upload a PDF to add lab results</p>
          </div>
        ) : (
          <div className="space-y-4">
            {labResults.map((result, index) => {
              const statusConfig = getStatusConfig(result.status);
              return (
                <div
                  key={result.id || index}
                  className={`card-modern p-5 ${statusConfig.border} border-l-4
                    hover:shadow-card-hover transition-all duration-300 
                    animate-fade-in group cursor-pointer`}
                  style={{ animationDelay: `${index * 80}ms` }}
                >
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center gap-3 mb-3">
                        <div className={`w-3 h-3 rounded-full bg-gradient-to-r ${statusConfig.gradient} shadow-sm`}></div>
                        <h3 className="font-bold text-gray-900 text-lg group-hover:text-gradient transition-all">
                          {result.test_name}
                        </h3>
                      </div>
                      <div className="flex items-baseline gap-3 mb-2">
                        <span className={`text-3xl font-bold ${
                          result.status === 'normal' ? 'text-green-600' :
                          result.status === 'high' ? 'text-red-600' :
                          result.status === 'low' ? 'text-amber-600' :
                          'text-gray-700'
                        }`}>
                          {result.result}
                        </span>
                        {result.unit && (
                          <span className="text-base text-gray-500 font-medium">{result.unit}</span>
                        )}
                      </div>
                      {result.reference_range && (
                        <p className="text-sm text-gray-400 flex items-center gap-2">
                          <svg className="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                          </svg>
                          Reference: {result.reference_range}
                        </p>
                      )}
                    </div>
                    <div className="text-right flex flex-col items-end gap-3">
                      <span className={`inline-flex items-center gap-2 px-4 py-2 rounded-xl text-sm font-bold
                        ${statusConfig.bg} ${statusConfig.text} ${statusConfig.border} border
                        shadow-sm transition-all duration-300 group-hover:scale-105`}>
                        <span className={`w-6 h-6 rounded-lg ${statusConfig.iconBg} flex items-center justify-center text-xs`}>
                          {statusConfig.icon}
                        </span>
                        {statusConfig.label}
                      </span>
                      {result.timestamp && (
                        <p className="text-xs text-gray-400 flex items-center gap-1">
                          <svg className="h-3 w-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                          </svg>
                          {formatDate(result.timestamp)}
                        </p>
                      )}
                    </div>
                  </div>
                  
                  {/* Progress bar visualization */}
                  <div className="mt-4 pt-4 border-t border-gray-100">
                    <div className="flex items-center justify-between text-xs text-gray-400 mb-2">
                      <span>Low</span>
                      <span>Normal</span>
                      <span>High</span>
                    </div>
                    <div className="h-2 bg-gradient-to-r from-amber-100 via-green-100 to-red-100 rounded-full overflow-hidden relative">
                      {/* Indicator */}
                      <div 
                        className={`absolute top-0 h-full w-4 rounded-full bg-gradient-to-r ${statusConfig.gradient} 
                          shadow-lg transition-all duration-1000 ease-out transform -translate-x-1/2`}
                        style={{ 
                          left: result.status === 'normal' ? '50%' : 
                                result.status === 'high' ? '85%' : 
                                result.status === 'low' ? '15%' : '50%' 
                        }}
                      />
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>

      {/* Footer Summary */}
      {labResults.length > 0 && (
        <div className="p-4 border-t border-gray-100 bg-white/90 backdrop-blur-sm">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-6 text-sm">
              <span className="flex items-center gap-2 px-3 py-1.5 bg-green-50 rounded-lg border border-green-100">
                <span className="w-3 h-3 rounded-full bg-gradient-to-r from-green-400 to-emerald-500"></span>
                <span className="text-green-700 font-medium">
                  {labResults.filter(r => r.status === 'normal').length} Normal
                </span>
              </span>
              <span className="flex items-center gap-2 px-3 py-1.5 bg-red-50 rounded-lg border border-red-100">
                <span className="w-3 h-3 rounded-full bg-gradient-to-r from-red-400 to-rose-500"></span>
                <span className="text-red-700 font-medium">
                  {labResults.filter(r => r.status === 'high').length} High
                </span>
              </span>
              <span className="flex items-center gap-2 px-3 py-1.5 bg-amber-50 rounded-lg border border-amber-100">
                <span className="w-3 h-3 rounded-full bg-gradient-to-r from-amber-400 to-orange-500"></span>
                <span className="text-amber-700 font-medium">
                  {labResults.filter(r => r.status === 'low').length} Low
                </span>
              </span>
            </div>
            <span className="text-sm text-gray-500 font-medium px-3 py-1.5 bg-gray-50 rounded-lg">
              {labResults.length} total result{labResults.length !== 1 ? 's' : ''}
            </span>
          </div>
        </div>
      )}
    </div>
  );
};

export default LabResults;
