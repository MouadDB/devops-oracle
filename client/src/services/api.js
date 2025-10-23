import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 60000, // 60 seconds
});

export const analyzeIncident = async (description, userId = null) => {
  try {
    const response = await api.post('/api/v1/incidents/analyze', {
      description,
      user_id: userId,
    });
    return response.data;
  } catch (error) {
    console.error('API Error:', error);
    throw error;
  }
};

export const getHealth = async () => {
  try {
    const response = await api.get('/health');
    return response.data;
  } catch (error) {
    console.error('Health check failed:', error);
    throw error;
  }
};

export const getStats = async () => {
  try {
    const response = await api.get('/api/v1/stats');
    return response.data;
  } catch (error) {
    console.error('Stats error:', error);
    throw error;
  }
};

export const getIncidentById = async (incidentId) => {
  try {
    const response = await api.get(`/api/v1/incidents/${incidentId}`);
    return response.data;
  } catch (error) {
    console.error('Get incident error:', error);
    throw error;
  }
};

export default api;