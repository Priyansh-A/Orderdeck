import { useNavigate, useSearchParams } from 'react-router-dom';
import { MdError } from 'react-icons/md';

const PaymentFailure = () => {
  const navigate = useNavigate();
  const [params] = useSearchParams();

  return (
    <div className="min-h-screen bg-white flex items-center justify-center p-6 text-center">
      <div className="max-w-md w-full">
        <MdError size={100} className="text-red-500 mx-auto mb-8" />
        <h1 className="text-4xl font-black uppercase tracking-tighter text-text-black">Transaction Failed</h1>
        <p className="text-gray-400 font-bold text-[10px] uppercase tracking-widest mt-4">The payment for Order #{params.get('order')} was not completed.</p>
        <button onClick={() => navigate('/payments')} className="mt-12 w-full py-5 bg-[#1E1616] text-white rounded-[1.5rem] font-black uppercase text-[11px] tracking-widest">Try Again</button>
      </div>
    </div>
  );
};
export default PaymentFailure;