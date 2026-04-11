import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import CartService from '../services/cart.service';
import ProductService from '../services/product.service';

const useCartStore = create(
  persist(
    (set, get) => ({
      cart: null,
      loading: false,
      error: null,
      selectedTable: null,
      customerName: null,

      fetchCart: async () => {
        set({ loading: true });
        try {
          const cart = await CartService.getActiveCart();
          if (cart && cart.items) {
            const enrichedItems = await Promise.all(
              cart.items.map(async (item) => {
                if (!item.product) {
                  const product = await ProductService.getProductById(item.product_id);
                  return { ...item, product };
                }
                return item;
              })
            );
            cart.items = enrichedItems.sort((a, b) => a.id - b.id);
          }
          set({ cart, loading: false, error: null });
          return cart;
        } catch (error) {
          set({ cart: null, error: error.message, loading: false });
          throw error;
        }
      },

      addItem: async (item) => {
        set({ loading: true });
        try {
          const updatedCart = await CartService.addItemToCart(item);
          if (updatedCart && updatedCart.items) {
            const enrichedItems = await Promise.all(
              updatedCart.items.map(async (item) => {
                if (!item.product) {
                  const product = await ProductService.getProductById(item.product_id);
                  return { ...item, product };
                }
                return item;
              })
            );
            updatedCart.items = enrichedItems.sort((a, b) => a.id - b.id);
          }
          set({ cart: updatedCart, loading: false });
          return updatedCart;
        } catch (error) {
          set({ error: error.message, loading: false });
          throw error;
        }
      },

      updateItem: async (itemId, quantity) => {
        const currentCart = get().cart;
        if (!currentCart) return;
        
        const updatedItems = currentCart.items.map(item => {
          if (item.id === itemId) {
            if (quantity <= 0) {
              return null;
            }
            return {
              ...item,
              quantity: quantity,
              subtotal: item.unit_price * quantity
            };
          }
          return item;
        }).filter(item => item !== null);
        
        updatedItems.sort((a, b) => a.id - b.id);
        
        const newSubtotal = updatedItems.reduce((sum, item) => sum + item.subtotal, 0);
        
        set({
          cart: {
            ...currentCart,
            items: updatedItems,
            subtotal: newSubtotal,
            updated_at: new Date().toISOString()
          },
          loading: true
        });
        
        try {
          const updatedCart = await CartService.updateCartItem(itemId, quantity);
          if (updatedCart && updatedCart.items) {
            const enrichedItems = await Promise.all(
              updatedCart.items.map(async (item) => {
                if (!item.product) {
                  const product = await ProductService.getProductById(item.product_id);
                  return { ...item, product };
                }
                return item;
              })
            );
            updatedCart.items = enrichedItems.sort((a, b) => a.id - b.id);
          }
          set({ cart: updatedCart, loading: false });
          return updatedCart;
        } catch (error) {
          await get().fetchCart();
          set({ loading: false });
          throw error;
        }
      },

      removeItem: async (itemId) => {
        return get().updateItem(itemId, 0);
      },

      clearCartItems: async () => {
        set({ loading: true });
        try {
          await CartService.clearCart();
          const freshCart = await CartService.getActiveCart();
          if (freshCart && freshCart.items) {
            const enrichedItems = await Promise.all(
              freshCart.items.map(async (item) => {
                if (!item.product) {
                  const product = await ProductService.getProductById(item.product_id);
                  return { ...item, product };
                }
                return item;
              })
            );
            freshCart.items = enrichedItems.sort((a, b) => a.id - b.id);
          }
          const currentTable = get().selectedTable;
          const currentCustomer = get().customerName;
          set({ cart: freshCart, loading: false });
          return freshCart;
        } catch (error) {
          set({ error: error.message, loading: false });
          throw error;
        }
      },

      resetCart: async () => {
        set({ loading: true });
        try {
          await CartService.clearCart();
          const freshCart = await CartService.getActiveCart();
          if (freshCart && freshCart.items) {
            const enrichedItems = await Promise.all(
              freshCart.items.map(async (item) => {
                if (!item.product) {
                  const product = await ProductService.getProductById(item.product_id);
                  return { ...item, product };
                }
                return item;
              })
            );
            freshCart.items = enrichedItems.sort((a, b) => a.id - b.id);
          }
          set({ cart: freshCart, loading: false, selectedTable: null, customerName: null });
          return freshCart;
        } catch (error) {
          set({ error: error.message, loading: false });
          throw error;
        }
      },

      setTable: async (tableId) => {
        set({ loading: true });
        try {
          const updatedCart = await CartService.setCartTable(tableId);
          if (updatedCart && updatedCart.items) {
            const enrichedItems = await Promise.all(
              updatedCart.items.map(async (item) => {
                if (!item.product) {
                  const product = await ProductService.getProductById(item.product_id);
                  return { ...item, product };
                }
                return item;
              })
            );
            updatedCart.items = enrichedItems.sort((a, b) => a.id - b.id);
          }
          set({ cart: updatedCart, selectedTable: tableId, loading: false });
          return updatedCart;
        } catch (error) {
          set({ error: error.message, loading: false });
          throw error;
        }
      },

      setCustomerName: (name) => {
        set({ customerName: name });
      },
      
      clearTableAndCustomer: () => set({ 
        selectedTable: null, 
        customerName: '', 
        items: [] }),
    }),
    {
      name: 'cart-storage',
    }
  )
);

export default useCartStore;