import { useNavigate, useSearchParams } from 'react-router-dom';
import { MdCheckCircle } from 'react-icons/md';
import { normalizePaymentMethod, getPaymentColor } from '../utils/paymentUtils';

const PaymentSuccess = () => {
  const navigate = useNavigate();
  const [params] = useSearchParams();
  const method = normalizePaymentMethod(params.get('method'));

  return (
    <div className="min-h-screen bg-[#FDFDFD] flex items-center justify-center p-6">
      <div className="max-w-md w-full bg-white rounded-[3.5rem] shadow-2xl p-12 text-center border border-gray-50">
        <MdCheckCircle size={100} style={{ color: getPaymentColor(method) }} className="mx-auto mb-8" />
        <h1 className="text-4xl font-black text-text-black uppercase tracking-tighter">Success!</h1>
        <p className="text-gray-400 font-bold text-[10px] uppercase tracking-[0.3em] mt-3">
          Order #{params.get('order')} settled via {method}
        </p>
        <div className="mt-12 space-y-4">
          <button onClick={() => navigate('/payments')} className="w-full h-18 bg-[#1E1616] text-white rounded-[1.5rem] font-black uppercase text-[11px] tracking-widest py-5 shadow-xl">Back to Payments</button>
          <button onClick={() => navigate('/')} className="w-full h-18 text-gray-400 font-black uppercase text-[11px] tracking-widest">New Order</button>
        </div>
      </div>
    </div>
  );
};
export default PaymentSuccess;