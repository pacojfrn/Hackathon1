import axios from 'axios';

const API_BASE_URL = 'http://10.0.2.2:8000/api'; // Cambia por tu IP local

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 5000,
});

export const loginUser = async (username, password) => {
  try {
    const response = await api.post('/login', { username, password });
    return response.data;
  } catch (error) {
    console.error('Error en login:', error.response?.data || error.message);
    throw error;
  }
};
