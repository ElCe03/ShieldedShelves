import axios from 'axios';

const axiosInstance = axios.create({
  baseURL: 'http://localhost:5000',
  withCredentials: true,
});

axiosInstance.interceptors.request.use(async config => {
  const csrfResponse = await axios.get('http://localhost:5000/get_csrf_token', { withCredentials: true });
  const csrfToken = csrfResponse.data.csrf_token;
  config.headers['X-CSRFToken'] = csrfToken;
  return config;
});

export default axiosInstance;