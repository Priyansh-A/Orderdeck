import useNotificationStore from '../services/notification.service';

export const showNotification = (type, title, message, link = null) => {
  const store = useNotificationStore.getState();
  store.addNotification({
    type,
    title,
    message,
    link
  });
};

export const notifyOrderCreated = (orderNumber) => {
  showNotification(
    'order',
    'Order Created',
    `Order #${orderNumber} has been created successfully.`,
    `/orders`
  );
};

export const notifyOrderStatusUpdated = (orderNumber, status) => {
  const statusMessages = {
    preparing: 'is now being prepared in the kitchen',
    ready: 'is ready for serving',
    served: 'has been served to the customer',
    completed: 'has been completed',
    cancelled: 'has been cancelled'
  };
  
  showNotification(
    'order',
    'Order Updated',
    `Order #${orderNumber} ${statusMessages[status] || `status changed to ${status}`}.`,
    `/orders`
  );
};

export const notifyPaymentSuccess = (orderNumber, amount, method) => {
  showNotification(
    'payment',
    'Payment Received',
    `Payment of रु ${amount} received for order #${orderNumber} via ${method}.`,
    `/payments`
  );
};

export const notifyTableOccupied = (tableNumber, customerName) => {
  showNotification(
    'success',
    'Table Occupied',
    `Table ${tableNumber} is now occupied by ${customerName}.`,
    `/tables`
  );
};

export const notifyTableCleared = (tableNumber) => {
  showNotification(
    'info',
    'Table Available',
    `Table ${tableNumber} is now available for next customers.`,
    `/tables`
  );
};

export const notifyError = (message) => {
  showNotification(
    'error',
    'Error',
    message,
    null
  );
};

export const notifySuccess = (title, message) => {
  showNotification(
    'success',
    title,
    message,
    null
  );
};