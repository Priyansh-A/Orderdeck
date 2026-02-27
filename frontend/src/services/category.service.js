import axiosInstance from '../config/api';

class CategoryService {
  async getAllCategories() {
    const response = await axiosInstance.get('/categories/');
    return response.data;
  }

  async getCategoryById(id) {
    const response = await axiosInstance.get(`/categories/${id}`);
    return response.data;
  }

  async createCategory(name) {
    const response = await axiosInstance.post('/categories/', { name });
    return response.data;
  }

  async updateCategory(id, name) {
    const response = await axiosInstance.patch(`/categories/${id}`, { name });
    return response.data;
  }

  async deleteCategory(id) {
    await axiosInstance.delete(`/categories/${id}`);
  }
}

export default new CategoryService();