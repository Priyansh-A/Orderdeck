import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import PaymentService from '../../services/payment.service';
import { MdPayments, MdAccountBalanceWallet, MdClose } from 'react-icons/md';
import toast from 'react-hot-toast';

const PaymentModal = ({ order, onClose }) => {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);

  const settle = async (type) => {
    setLoading(true);
    try {
      if (type === 'cash') {
        const result = await PaymentService.processCashPayment(order.id);
        if (result.success) {
          navigate(`/payment/success?order=${order.order_number}&method=cash`);
        }
      } else {
        const result = await PaymentService.initiateEsewaPayment(order.id);
        
        const form = document.createElement('form');
        form.method = 'POST';
        form.action = result.esewa_url;
        
        const fields = {
          'amount': result.total_amount,
          'tax_amount': '0',
          'total_amount': result.total_amount,
          'transaction_uuid': result.transaction_uuid,
          'product_code': result.product_code,
          'product_service_charge': '0',
          'product_delivery_charge': '0',
          'success_url': result.success_url,
          'failure_url': result.failure_url,
          'signed_field_names': result.signed_field_names,
          'signature': result.signature
        };
        
        for (const [key, value] of Object.entries(fields)) {
          const input = document.createElement('input');
          input.type = 'hidden';
          input.name = key;
          input.value = value;
          form.appendChild(input);
        }
        
        document.body.appendChild(form);
        form.submit();
      }
    } catch (err) {
      console.error(err);
      toast.error(err.response?.data?.detail || 'Payment failed');
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-text-black/80 z-120 flex items-center justify-center p-4 backdrop-blur-sm">
      <div className="bg-white rounded-[3rem] max-w-md w-full p-10">
        <div className="flex justify-between items-center mb-10">
          <h2 className="text-3xl font-black uppercase tracking-tighter">Settle Bill</h2>
          <button onClick={onClose} className="p-3 bg-gray-50 rounded-full">
            <MdClose size={20} />
          </button>
        </div>
        
        <div className="space-y-4">
          <button 
            disabled={loading} 
            onClick={() => settle('cash')} 
            className="w-full p-6 border-2 border-gray-100 rounded-4xl flex items-center hover:border-text-black transition-all group"
          >
            <div className="w-12 h-12 bg-gray-100 rounded-2xl flex items-center justify-center mr-4 group-hover:bg-text-black group-hover:text-white">
              <MdPayments size={24}/>
            </div>
            <div className="text-left font-black uppercase text-xs">
              Cash Settlement
            </div>
          </button>
          
          <button 
            disabled={loading} 
            onClick={() => settle('esewa')} 
            className="w-full p-6 border-2 border-gray-100 rounded-4xl flex items-center hover:border-[#3A707A] transition-all group"
          >
            <div className="w-12 h-12 bg-gray-100 rounded-2xl flex items-center justify-center mr-4 group-hover:bg-[#3A707A] group-hover:text-white">
              <MdAccountBalanceWallet size={24}/>
            </div>
            <div className="text-left font-black uppercase text-xs">
              eSewa Digital
            </div>
          </button>
        </div>
      </div>
    </div>
  );
};

export default PaymentModal;