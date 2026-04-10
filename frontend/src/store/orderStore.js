import { create } from 'zustand';
import OrderService from '../services/order.service';
import ProductService from '../services/product.service';

const useOrderStore = create((set, get) => ({
  orders: [],
  activeOrders: [],
  loading: false,
  error: null,

  enrichOrderData: async (orders) => {
    if (!orders) return [];
    const orderArray = Array.isArray(orders) ? orders : [orders];
    return await Promise.all(
      orderArray.map(async (order) => {
        if (order.items) {
          const enrichedItems = await Promise.all(
            order.items.map(async (item) => {
              if (!item.product && item.product_id) {
                try {
                  const product = await ProductService.getProductById(item.product_id);
                  return { ...item, product };
                } catch (err) { return item; }
              }
              return item;
            })
          );
          return { ...order, items: enrichedItems };
        }
        return order;
      })
    );
  },

  fetchOrders: async (params = {}) => {
    set({ loading: true });
    try {
      const response = await OrderService.getAllOrders(params);
      const enriched = await get().enrichOrderData(response);
      set({ orders: enriched, loading: false });
      return enriched;
    } catch (error) {
      set({ error: error.message, loading: false });
      throw error;
    }
  },

  updateStatus: async (id, status) => {
    try {
      const updatedOrder = await OrderService.updateOrderStatus(id, status);
      await get().fetchOrders();
      return updatedOrder;
    } catch (error) {
      set({ error: error.message });
      throw error;
    }
  },

  cancelOrder: async (id) => {
    try {
      await OrderService.updateOrderStatus(id, 'cancelled');
      await get().fetchOrders();
    } catch (error) {
      set({ error: error.message });
      throw error;
    }
  },
}));

export default useOrderStore;