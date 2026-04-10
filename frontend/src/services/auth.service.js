import api from './api';

class AuthService {
  async login(credentials) {
    const formData = new FormData();
    formData.append('username', credentials.username);
    formData.append('password', credentials.password);

    const response = await api.post('/auth/login', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    
    if (response.data.access_token) {
      localStorage.setItem('token', response.data.access_token);
    }
    
    return response.data;
  }

  async signup(userData) {
    const response = await api.post('/users/', userData);
    return response.data;
  }

  async getCurrentUser() {
    const response = await api.get('/auth/me');
    return response.data;
  }

  async getAllUsers() {
  const response = await api.get('/users/');
  return response.data;
  }

  async updateUser(id, userData) {
  const response = await api.put(`/users/${id}`, userData);
  return response.data;
  }

  async deleteUser(id) {
  const response = await api.delete(`/users/${id}`);
  return response.data;
  }

  logout() {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
  }

  getToken() {
    return localStorage.getItem('token');
  }

  isAuthenticated() {
    return !!this.getToken();
  }


}


export default new AuthService();