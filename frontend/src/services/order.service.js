import api from './api';

class OrderService {
  async checkout(checkoutData) {
    const response = await api.post('/orders/checkout', checkoutData);
    return response.data;
  }

  async getAllOrders(skip = 0, limit = 100, statusFilter = null, orderType = null) {
    const params = { skip, limit };
    if (statusFilter) params.status_filter = statusFilter;
    if (orderType) params.order_type = orderType;
    
    const response = await api.get('/orders/', { params });
    return response.data;
  }

  async getActiveOrders() {
    const response = await api.get('/orders/active');
    return response.data;
  }

  async getOrderById(id) {
  const response = await api.get(`/orders/${id}`);
  if (response.data.items) {
    response.data.items = response.data.items.map(item => ({
      ...item,
      product_name: item.product?.name || item.product_name || `Product #${item.product_id}`
    }));
  }
  return response.data;
  }

  async updateOrderStatus(id, status) {
    const response = await api.patch(`/orders/${id}/status`, { status });
    return response.data;
  }

  async markTakeawayReady(id) {
    const response = await api.patch(`/orders/${id}/ready-for-pickup`);
    return response.data;
  }

  async cancelOrder(id) {
    const response = await api.delete(`/orders/${id}`);
    return response.status === 204;
  }

  async permanentDeleteOrder(id) {
    const response = await api.delete(`/orders/${id}/permanent`);
    return response.status === 204;
  }
}

export default new OrderService();