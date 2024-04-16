import axios from 'axios';

const API = axios.create({
  baseURL: 'http://localhost:8000/', // Adjust to your Django server URL
});

// Intercept requests to include the auth token
API.interceptors.request.use((config) => {
    const token = localStorage.getItem('token');
    config.headers.Authorization = token ? `Token ${token}` : '';
    return config;
});

export default API;