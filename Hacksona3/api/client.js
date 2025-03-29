import axios from 'axios';
import AsyncStorage from '@react-native-async-storage/async-storage';

// Configura la URL base de tu API (ajusta según tu despliegue)
const api = axios.create({
  baseURL: 'https://tu-api-fastapi.com', // Ej: http://192.168.1.X:8000 para desarrollo local
});

// Interceptor para añadir el token JWT a las peticiones
api.interceptors.request.use(
  async (config) => {
    const token = await AsyncStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

export default api;