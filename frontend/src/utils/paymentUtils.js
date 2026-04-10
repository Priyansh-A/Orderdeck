export const normalizePaymentMethod = (data) => {
  const rawMethod = typeof data === 'string' 
    ? data 
    : data?.payment_method || data?.method || 'CASH';

  console.log("DEBUG: Raw Payment Data received:", data, "Extracted:", rawMethod);

  const m = rawMethod.toLowerCase();
  
  if (m === 'online' || m === 'esewa' || m === 'digital') {
    return 'ESEWA';
  }
  
  return 'CASH';
};

export const getPaymentColor = (method) => {
  const normalized = normalizePaymentMethod(method);
  return normalized === 'ESEWA' ? '#3A707A' : '#1E1616';
};