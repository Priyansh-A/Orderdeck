import api from './api';

class ProductService {
  async getAllProducts() {
    const response = await api.get('/products/');
    return response.data;
  }

  async getAvailableProducts() {
    const response = await api.get('/products/available');
    return response.data;
  }

  async getProductById(id) {
    const response = await api.get(`/products/${id}`);
    return response.data;
  }

  async createProduct(formData) {
    if (formData.image instanceof File) {
      const data = new FormData();
      data.append('name', formData.name);
      data.append('price', formData.price);
      data.append('category_id', formData.category_id);
      data.append('description', formData.description || '');
      data.append('is_available', formData.is_available);
      data.append('image', formData.image);
      
      const response = await api.post('/products/', data, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      return response.data;
    } else {
      const response = await api.post('/products/', formData);
      return response.data;
    }
  }

  async updateProduct(id, formData) {
    if (formData.image instanceof File) {
      const data = new FormData();
      if (formData.name) data.append('name', formData.name);
      if (formData.price) data.append('price', formData.price);
      if (formData.category_id) data.append('category_id', formData.category_id);
      if (formData.description) data.append('description', formData.description);
      if (formData.is_available !== undefined) data.append('is_available', formData.is_available);
      if (formData.image) data.append('image', formData.image);
      
      const response = await api.patch(`/products/${id}`, data, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      return response.data;
    } else {
      const response = await api.patch(`/products/${id}`, formData);
      return response.data;
    }
  }

  async deleteProduct(id) {
    const response = await api.delete(`/products/${id}`);
    return response.status === 204;
  }
}

export default new ProductService();