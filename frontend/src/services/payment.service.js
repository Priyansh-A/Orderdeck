import axios from 'axios';

const API_URL = 'http://localhost:8000/api/payments';

export const paymentService = {
  initiatePayment: async (orderId, token) => {
    const response = await axios.post(
      `${API_URL}/initiate/${orderId}`,
      {},
      { headers: { Authorization: `Bearer ${token}` } }
    );
    return response.data;
  },

  // Process cash payment
  processCashPayment: async (orderId, token) => {
    const response = await axios.post(
      `${API_URL}/cash/${orderId}`,
      {},
      { headers: { Authorization: `Bearer ${token}` } }
    );
    return response.data;
  },

  // Initiate eSewa payment
  initiateEsewaPayment: async (orderId, token) => {
    const response = await axios.post(
      `${API_URL}/esewa/initiate/${orderId}`,
      {},
      { headers: { Authorization: `Bearer ${token}` } }
    );
    return response.data;
  },

  // Verify payment status
  verifyPayment: async (orderId, token) => {
    const response = await axios.get(
      `${API_URL}/verify/${orderId}`,
      { headers: { Authorization: `Bearer ${token}` } }
    );
    return response.data;
  }
};