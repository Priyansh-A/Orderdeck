import api from './api';

class RecommendationService {
  async getCartRecommendations(cartId, limit = 5) {
    const response = await api.get(`/recommendations/cart/${cartId}`, {
      params: { limit }
    });
    return response.data;
  }

  async getProductRecommendations(productId, limit = 5) {
    const response = await api.get(`/recommendations/product/${productId}`, {
      params: { limit }
    });
    return response.data;
  }

  async trainModel(minSupport = 0.01, minConfidence = 0.5) {
    const response = await api.post('/recommendations/train', null, {
      params: { min_support: minSupport, min_confidence: minConfidence }
    });
    return response.data;
  }

  async getPopularProducts(limit = 5) {
    const response = await api.get('/recommendations/popular', {
      params: { limit }
    });
    return response.data;
  }
}

export default new RecommendationService();