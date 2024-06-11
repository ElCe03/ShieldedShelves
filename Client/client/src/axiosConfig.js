import axios from 'axios';

const axiosInstance5000 = axios.create({
  baseURL: 'http://localhost:5000',
  withCredentials: true,
});

axiosInstance5000.interceptors.request.use(async config => {
  const csrfResponse = await axios.get('http://localhost:5000/get_csrf_token', { withCredentials: true });
  const csrfToken = csrfResponse.data.csrf_token;
  config.headers['X-CSRFToken'] = csrfToken;
  return config;
});

const axiosInstance5001 = axios.create({
  baseURL: 'http://localhost:5001',
  withCredentials: true,
});

axiosInstance5001.interceptors.request.use(async config => {
  const csrfResponse = await axios.get('http://localhost:5001/get_csrf_token', { withCredentials: true });
  const csrfToken = csrfResponse.data.csrf_token;
  config.headers['X-CSRFToken'] = csrfToken;
  return config;
});

const axiosInstance5002 = axios.create({
  baseURL: 'http://localhost:5002',
  withCredentials: true,
});

axiosInstance5002.interceptors.request.use(async config => {
  const csrfResponse = await axios.get('http://localhost:5002/get_csrf_token', { withCredentials: true });
  const csrfToken = csrfResponse.data.csrf_token;
  config.headers['X-CSRFToken'] = csrfToken;
  return config;
});

const axiosInstance5003 = axios.create({ // Nuova istanza per il server Flask sulla porta 5003
  baseURL: 'http://localhost:5003',
  withCredentials: true,
});

axiosInstance5003.interceptors.request.use(async config => {
  const csrfResponse = await axios.get('http://localhost:5003/get_csrf_token', { withCredentials: true });
  const csrfToken = csrfResponse.data.csrf_token;
  config.headers['X-CSRFToken'] = csrfToken;
  return config;
});

export { axiosInstance5000, axiosInstance5001, axiosInstance5002, axiosInstance5003 }; // Assicurati di esportare l'istanza axios corretta
