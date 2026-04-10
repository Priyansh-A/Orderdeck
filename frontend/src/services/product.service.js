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

  async createProduct(productData) {
    const response = await api.post('/products/', productData);
    return response.data;
  }

  async updateProduct(id, productData) {
    const response = await api.patch(`/products/${id}`, productData);
    return response.data;
  }

  async deleteProduct(id) {
    const response = await api.delete(`/products/${id}`);
    return response.status === 204;
  }
}

export default new ProductService();