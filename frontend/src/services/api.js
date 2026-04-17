import axios from 'axios';

// Use environment variable for API URL, fallback to localhost for development
const API_BASE_URL = import.meta.env.VITE_API_URL 
  ? `https://${import.meta.env.VITE_API_URL}` 
  : 'http://localhost:8001';

// Create axios instance
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Token management
const getAccessToken = () => localStorage.getItem('access_token');
const getRefreshToken = () => localStorage.getItem('refresh_token');
const setTokens = (accessToken, refreshToken) => {
  localStorage.setItem('access_token', accessToken);
  localStorage.setItem('refresh_token', refreshToken);
};
const clearTokens = () => {
  localStorage.removeItem('access_token');
  localStorage.removeItem('refresh_token');
};

// Request interceptor to add auth header
api.interceptors.request.use(
  (config) => {
    const token = getAccessToken();
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor to handle 401 errors
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      try {
        const refreshToken = getRefreshToken();
        if (refreshToken) {
          const response = await axios.post(`${API_BASE_URL}/auth/refresh`, {
            refresh_token: refreshToken,
          });

          const { access_token, refresh_token: newRefreshToken } = response.data;
          setTokens(access_token, newRefreshToken);

          // Retry the original request with new token
          originalRequest.headers.Authorization = `Bearer ${access_token}`;
          return api(originalRequest);
        }
      } catch (refreshError) {
        // Refresh failed, clear tokens and redirect to login
        clearTokens();
        window.location.href = '/login';
      }
    }

    return Promise.reject(error);
  }
);

// Auth API functions
export const authAPI = {
  signup: async (userData) => {
    const response = await api.post('/auth/signup', userData);
    return response.data;
  },

  login: async (credentials) => {
    const response = await api.post('/auth/login', credentials);
    const { access_token, refresh_token } = response.data;
    setTokens(access_token, refresh_token);
    return response.data;
  },

  logout: () => {
    clearTokens();
  },

  isAuthenticated: () => {
    return !!getAccessToken();
  },

  // Debug function to check current user token
  getCurrentUser: () => {
    const token = getAccessToken();
    if (token) {
      try {
        // Decode JWT payload (simple base64 decode)
        const payload = JSON.parse(atob(token.split('.')[1]));
        console.log('Current user from token:', payload);
        return payload;
      } catch (e) {
        console.error('Error decoding token:', e);
        return null;
      }
    }
    return null;
  },
};

// Patient API functions
export const patientsAPI = {
  // Get all patients for the authenticated doctor
  getPatients: async (skip = 0, limit = 100) => {
    console.log('API: Fetching patients...'); // Debug log
    const response = await api.get(`/api/patients/`, {
      params: { skip, limit }
    });
    console.log('API: Raw patients response:', response.data); // Debug log
    // Backend returns { message, data, count } - extract just the patients array
    return { data: response.data.data || [] };
  },

  // Get specific patient by ID
  getPatient: async (patientId) => {
    const response = await api.get(`/api/patients/${patientId}`);
    return response.data;
  },

  // Add new patient
  addPatient: async (patientData) => {
    console.log('API: Adding patient with data:', patientData); // Debug log
    const response = await api.post('/api/patients/add', patientData);
    console.log('API: Add patient response:', response.data); // Debug log
    return response.data;
  },

  // Get patient via MCP
  getMCPPatient: async (patientId) => {
    const response = await api.get(`/api/mcp/patient/${patientId}`);
    return response.data;
  },
};

// LLM Chat API functions
export const llmAPI = {
  // Send query to LLM
  queryLLM: async (query, patientId = null) => {
    console.log('🔍 Frontend LLM API Call:', {
      query,
      patientId,
      timestamp: new Date().toISOString(),
      endpoint: '/api/llm/query'
    });
    
    try {
      // Construct the request with proper context structure
      const requestData = {
        query: query,
        patient_id: patientId
      };
      
      console.log('📤 Sending request data:', requestData);
      
      // Use the configured API base URL (no port scanning needed for production)
      const response = await api.post('/api/llm/query', requestData);
      
      console.log('📥 LLM API Response:', {
        status: response.status,
        data: response.data,
        timestamp: new Date().toISOString()
      });
      
      return response.data;
    } catch (error) {
      console.error('❌ LLM API Error:', {
        error: error.message,
        response: error.response?.data,
        status: error.response?.status,
        timestamp: new Date().toISOString()
      });
      throw error;
    }
  },
};

// RAG Search API functions
export const ragAPI = {
  // Search medical knowledge
  searchMedical: async (query) => {
    const response = await api.post('/api/rag-search', null, {
      params: { query }
    });
    return response.data;
  },
};

// File Upload API functions
export const fileAPI = {
  // Upload lab results PDF
  uploadLabResults: async (patientId, file) => {
    const formData = new FormData();
    formData.append('file', file);
    
    const response = await api.post(`/api/upload-lab-results/`, formData, {
      params: { patient_id: patientId },
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },
};

// Lab Results API functions
export const labAPI = {
  // Get lab results for a patient
  getLabResults: async (patientId) => {
    const response = await api.get(`/api/patients/${patientId}/lab-results`);
    return response.data;
  },

  // Get lab results summary for a patient
  getLabResultsSummary: async (patientId) => {
    const response = await api.get(`/api/patients/${patientId}/lab-results/summary`);
    return response.data;
  },
};

export default api;