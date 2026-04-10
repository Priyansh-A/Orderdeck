import { create } from 'zustand';
import { persist } from 'zustand/middleware';

const useNotificationStore = create(
  persist(
    (set, get) => ({
      notifications: [],
      unreadCount: 0,
      
      addNotification: (notification) => {
        const newNotification = {
          id: Date.now(),
          timestamp: new Date().toISOString(),
          read: false,
          ...notification
        };
        set((state) => ({
          notifications: [newNotification, ...state.notifications],
          unreadCount: state.unreadCount + 1
        }));
        
        setTimeout(() => {
          get().markAsRead(newNotification.id);
        }, 5000);
      },
      
      markAsRead: (id) => {
        set((state) => ({
          notifications: state.notifications.map(notif =>
            notif.id === id ? { ...notif, read: true } : notif
          ),
          unreadCount: state.unreadCount - 1
        }));
      },
      
      markAllAsRead: () => {
        set((state) => ({
          notifications: state.notifications.map(notif => ({ ...notif, read: true })),
          unreadCount: 0
        }));
      },
      
      clearAll: () => {
        set({ notifications: [], unreadCount: 0 });
      },
      
      removeNotification: (id) => {
        set((state) => ({
          notifications: state.notifications.filter(n => n.id !== id),
          unreadCount: state.unreadCount - (state.notifications.find(n => n.id === id)?.read ? 0 : 1)
        }));
      }
    }),
    {
      name: 'notifications-storage'
    }
  )
);

export default useNotificationStore;