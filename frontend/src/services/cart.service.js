import api from './api';

class CartService {
  async getActiveCart() {
    const response = await api.get('/cart/');
    return response.data;
  }

  async addItemToCart(itemData) {
    const response = await api.post('/cart/add-item', itemData);
    return response.data;
  }

  async updateCartItem(itemId, quantity) {
    const response = await api.patch(`/cart/update-item/${itemId}`, null, {
      params: { quantity }
    });
    return response.data;
  }

  async clearCart() {
    const response = await api.delete('/cart/clear');
    return response.status === 204;
  }

  async setCartTable(tableId) {
    const response = await api.post(`/cart/set-table/${tableId}`);
    return response.data;
  }
}

export default new CartService();