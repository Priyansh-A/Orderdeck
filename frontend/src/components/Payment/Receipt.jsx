import { MdPrint } from 'react-icons/md';
import { normalizePaymentMethod } from '../../utils/paymentUtils';

const Receipt = ({ order, onClose }) => {
  if (!order) return null;

  const rawItems = order.items || order.order_items || [];
  const method = normalizePaymentMethod(order.payment || order.payment_method);

  const getItemName = (item) => {
  if (item.product?.name) return item.product.name;
  if (item.product_name) return item.product_name;
  if (item.name) return item.name;
  
  if (item.product && typeof item.product === 'object') {
    for (const key of Object.keys(item.product)) {
      if (key.toLowerCase().includes('name') && typeof item.product[key] === 'string') {
        return item.product[key];
      }
    }
  }
  
  for (const key of Object.keys(item)) {
    if (key.toLowerCase().includes('name') && typeof item[key] === 'string' && item[key]) {
      return item[key];
    }
  }
  if (item.product_id) return `Item #${item.product_id}`;
  return 'Unknown Item';
  };

  const getTableNumber = () => {
    if (order.table?.table_number) return order.table.table_number;
    if (order.table_number) return order.table_number;
    if (order.table?.number) return order.table.number;
    if (order.table_id) return `Table ${order.table_id}`;
    if (order.order_type === 'dine_in') return 'Assigned Table';
    return 'N/A';
  };

  return (
    <div className="fixed inset-0 bg-text-black/95 z-200 flex items-center justify-center p-4 backdrop-blur-md">
      <div className="bg-white max-w-sm w-full rounded-[3rem] overflow-hidden shadow-2xl flex flex-col max-h-[90vh]">
        
        <div className="p-6 font-mono text-black bg-white overflow-y-auto" id="printable-receipt">
          <div className="text-center border-b-2 border-black pb-4 mb-6">
            <h2 className="text-2xl font-black uppercase tracking-tighter">Order-Deck</h2>
            <p className="text-[9px] font-bold tracking-[0.3em] mt-1 italic uppercase">Official Transaction Receipt</p>
          </div>

          {/* Header Information */}
          <div className="text-[10px] mb-6 space-y-1.5 uppercase font-bold border-b border-dashed border-gray-200 pb-4">
            <div className="flex justify-between flex-wrap gap-1">
              <span className="text-gray-500">Order No:</span>
              <span className="font-black">#{order.order_number}</span>
            </div>
            <div className="flex justify-between flex-wrap gap-1">
              <span className="text-gray-500">Customer:</span>
              <span className="font-black">{order.customer_name || 'Walking Guest'}</span>
            </div>
            <div className="flex justify-between flex-wrap gap-1">
              <span className="text-gray-500">Table:</span>
              <span className="font-black">{getTableNumber()}</span>
            </div>
            <div className="flex justify-between flex-wrap gap-1">
              <span className="text-gray-500">Date:</span>
              <span className="font-black">{new Date(order.created_at || Date.now()).toLocaleString()}</span>
            </div>
            <div className="flex justify-between flex-wrap gap-1">
              <span className="text-gray-500">Type:</span>
              <span className="font-black capitalize">{order.order_type === 'dine_in' ? 'Dine In' : 'Takeaway'}</span>
            </div>
          </div>

          {/* TABLE HEADER */}
          <div className="border-b-2 border-black py-2 mb-3 flex justify-between text-[10px] font-black uppercase">
            <span className="w-[55%]">Item Description</span>
            <span className="w-[15%] text-center">Qty</span>
            <span className="w-[30%] text-right">Total</span>
          </div>

          {/* DYNAMIC ITEM LIST */}
          <div className="space-y-4 mb-8">
            {rawItems.length > 0 ? rawItems.map((item, idx) => {
              const itemName = getItemName(item);
              const unitPrice = item.unit_price || item.price || 0;
              const subtotal = item.subtotal || (unitPrice * item.quantity);
              
              return (
                <div key={idx} className="flex justify-between text-[11px] leading-tight items-start">
                  <div className="w-[55%]">
                    <span className="uppercase block font-black leading-none mb-1 wrap-break-word">
                      {itemName}
                    </span>
                    <span className="text-[9px] text-gray-500">
                      Rate: रु {unitPrice}
                    </span>
                  </div>
                  <span className="w-[15%] text-center font-black text-gray-600">x{item.quantity}</span>
                  <span className="w-[30%] text-right font-black">
                    रु {subtotal.toLocaleString()}
                  </span>
                </div>
              );
            }) : (
              <div className="text-center py-4 text-[10px] font-bold text-gray-400 border border-dashed rounded-xl uppercase">
                No item data found
              </div>
            )}
          </div>

          {/* TOTAL SECTION */}
          <div className="border-t-2 border-black pt-4">
            <div className="flex justify-between font-black text-2xl items-baseline flex-wrap gap-2">
              <span className="text-xs uppercase">Grand Total</span>
              <span>रु {order.total_amount?.toLocaleString()}</span>
            </div>
            
            <div className="mt-8 pt-4 border-t border-dashed border-gray-300 text-center">
              <p className="text-[10px] font-black uppercase tracking-widest bg-gray-100 py-1 rounded">
                Payment: {method}
              </p>
              <div className="mt-6 flex flex-col items-center opacity-70">
                <div className="w-16 h-0.5 bg-black mb-1"></div>
                <p className="text-[9px] font-black uppercase">Thank You - Visit Again</p>
                <p className="text-[7px] mt-1">Order-Deck POS v1.0</p>
              </div>
            </div>
          </div>
        </div>

        {/* ACTIONS */}
        <div className="p-4 bg-gray-50 flex gap-3 border-t border-gray-100">
          <button 
            onClick={() => window.print()} 
            className="flex-1 py-3 bg-text-black text-white rounded-2xl font-black uppercase text-[10px] tracking-widest active:scale-95 transition-all flex items-center justify-center gap-2 shadow-lg shadow-black/20"
          >
            <MdPrint size={16}/> Print
          </button>
          <button 
            onClick={onClose} 
            className="flex-1 py-3 bg-white border border-gray-200 text-gray-500 rounded-2xl font-black uppercase text-[10px] tracking-widest hover:bg-gray-100 transition-colors"
          >
            Close
          </button>
        </div>
      </div>

      <style>{`
        @media print {
          body * { visibility: hidden; }
          #printable-receipt, #printable-receipt * { visibility: visible; }
          #printable-receipt { 
            position: fixed; 
            left: 0; 
            top: 0; 
            width: 80mm; 
            max-height: none !important;
            overflow: visible !important;
            padding: 20px !important;
          }
        }
      `}</style>
    </div>
  );
};

export default Receipt;