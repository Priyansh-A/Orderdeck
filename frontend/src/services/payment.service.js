import api from './api';

class PaymentService {
  async processCashPayment(orderId) {
    const response = await api.post(`/payments/cash/${orderId}`);
    return response.data;
  }

  async initiateEsewaPayment(orderId) {
    const response = await api.post(`/payments/esewa/initiate/${orderId}`);
    return response.data;
  }

  async verifyPayment(orderId) {
    const response = await api.get(`/payments/verify/${orderId}`);
    return response.data;
  }

  async getAllPayments(params = {}) {
    try {
      const response = await api.get('/payments/', { params });
      return response.data;
    } catch (error) {
      console.warn('Payments endpoint not available:', error);
      return [];
    }
  }
}

export default new PaymentService();