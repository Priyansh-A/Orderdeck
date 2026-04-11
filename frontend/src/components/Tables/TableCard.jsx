import React, { useState } from 'react';
import { MdDelete, MdAccessTime, MdPerson } from 'react-icons/md';
import useCartStore from '../../store/cartStore';
import useTableStore from '../../store/tableStore';
import toast from 'react-hot-toast';
import { notifySuccess } from '../../utils/notificationHelper';

const TableCard = ({ table }) => {
  const { setTable, setCustomerName, selectedTable, clearTableAndCustomer } = useCartStore();
  const { occupyTable, updateStatus, deleteTable } = useTableStore();
  
  const [showSelectModal, setShowSelectModal] = useState(false);
  const [tempCustomerName, setTempCustomerName] = useState('');
  const [updating, setUpdating] = useState(false);

  const isOccupied = table.status === 'occupied';
  const isSelected = selectedTable === table.id;

  const formatTime = (dateString) => {
    if (!dateString) return '';
    const date = new Date(dateString);
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };

  const handleSelectTable = () => {
    if (!isOccupied) {
      toast.error('Please check-in to a table first');
      return;
    }
    
    if (isSelected) {
      clearTableAndCustomer();
      toast.success(`Table ${table.table_number} unselected`);
    } else {
      setTable(table.id);
      if (table.occupied_by_customer) setCustomerName(table.occupied_by_customer);
      toast.success(`Table ${table.table_number} selected`);
    }
  };
  
  const handleConfirmSelect = async () => {
    if (!tempCustomerName.trim()) return toast.error('Enter customer name');
    setUpdating(true);
    try {
      const partyId = `P-${table.id}-${Date.now()}`;
      await occupyTable(table.id, tempCustomerName, partyId);
      
      setTable(table.id);
      setCustomerName(tempCustomerName);
      toast.success(`Table ${table.table_number} occupied`);
      setShowSelectModal(false);
    } catch (error) {
      toast.error('Failed to occupy');
    } finally {
      setUpdating(false);
    }
  };

  const handleClearTable = async (e) => {
    e.stopPropagation();
    if (!window.confirm(`Clear Table ${table.table_number}?`)) return;
    setUpdating(true);
    try {
      await updateStatus(table.id, 'available');
        if (selectedTable === table.id) {
        clearTableAndCustomer();
        toast.success('Table cleared and removed from cart');
      } else {
        toast.success('Table cleared');
      }
      
      notifyTableCleared(table.table_number);
    } catch (error) {
      toast.error('Failed to clear table');
    } finally {
      setUpdating(false);
    }
  };

  const handleDeleteTable = async (e) => {
    e.stopPropagation();
    if (!window.confirm(`Delete Table ${table.table_number}?`)) return;
    setUpdating(true);
    try {
      await deleteTable(table.id);
      notifySuccess('Deleted', `Table ${table.table_number} removed`);
      toast.success('Table deleted');
    } catch (error) {
      toast.error('Delete failed');
    } finally {
      setUpdating(false);
    }
  };

  return (
    <div className="relative group w-full">
      <div 
        onClick={handleSelectTable}
        className={`w-full aspect-square sm:aspect-auto sm:min-h-35 flex flex-col items-center justify-center p-3 sm:p-4 rounded-xl border-[3px] transition-all cursor-pointer bg-white
          ${isOccupied ? 'border-[#F28C28]' : 'border-[#58D39E]'} 
          ${isSelected && isOccupied ? 'ring-4 ring-emerald-300 shadow-md scale-[1.02]' : 'hover:shadow-md'}
          ${updating ? 'opacity-70 pointer-events-none' : ''}
        `}
      >
        <div className="text-center flex flex-col items-center justify-center gap-1 sm:gap-1.5 grow w-full">
          <span className="text-gray-600 font-black text-sm sm:text-lg uppercase tracking-wider">{table.table_number}</span>
          <div className="flex items-center text-gray-400 gap-1 mb-1">
            <MdPerson size={14} />
            <span className="text-[10px] sm:text-xs font-bold text-gray-500">{table.capacity} Seats</span>
          </div>
          
          <div className="border-t border-gray-100 w-3/4 mb-1"></div>

          {isOccupied ? (
            <div className="flex flex-col items-center gap-0.5 w-full px-1">
              <span className="text-[11px] sm:text-sm font-bold text-gray-800 truncate max-w-full">
                {table.occupied_by_customer}
              </span>
              <div className="flex items-center gap-1 text-[#F28C28]">
                <MdAccessTime size={10} />
                <span className="text-[9px] sm:text-[10px] font-bold">
                  {formatTime(table.updated_at || table.occupied_at)}
                </span>
              </div>
            </div>
          ) : (
            <span className="text-[10px] sm:text-sm font-bold text-[#58D39E] uppercase tracking-widest">Free</span>
          )}
        </div>

        {isOccupied ? (
          <button onClick={handleClearTable} disabled={updating} className="mt-2 w-full sm:w-auto text-[9px] bg-gray-100 hover:text-red-500 px-2 py-1 rounded uppercase font-bold transition-colors">
            Clear
          </button>
        ) : (
          <button onClick={(e) => { e.stopPropagation(); setShowSelectModal(true); }} disabled={updating} className="mt-2 w-full sm:w-auto text-[9px] bg-gray-100 hover:text-[#F28C28] px-2 py-1 rounded uppercase font-bold transition-colors">
            Check-in
          </button>
        )}
        
        <button onClick={handleDeleteTable} className="absolute top-2 right-2 text-gray-300 hover:text-red-500 p-1">
          <MdDelete size={18} />
        </button>
      </div>

      {showSelectModal && (
        <div className="fixed inset-0 bg-black/60 flex items-center justify-center z-100 p-4 backdrop-blur-sm">
          <div className="bg-white rounded-2xl p-6 w-full max-w-[320px] shadow-2xl">
            <h3 className="font-black text-gray-800 mb-2 text-lg">Check-in</h3>
            <p className="text-gray-500 text-xs mb-4">Assigning Customer to Table {table.table_number}</p>
            <input 
              className="w-full border-2 border-gray-100 rounded-xl p-3 mb-5 outline-none focus:border-[#F28C28] text-sm"
              placeholder="Enter Customer Name"
              value={tempCustomerName}
              onChange={(e) => setTempCustomerName(e.target.value)}
              autoFocus
            />
            <div className="flex flex-col gap-2">
              <button onClick={handleConfirmSelect} disabled={updating} className="w-full bg-[#F28C28] text-white py-3 rounded-xl font-bold text-sm">
                {updating ? 'Processing...' : 'Confirm Check-in'}
              </button>
              <button onClick={() => setShowSelectModal(false)} className="w-full bg-gray-50 text-gray-500 py-3 rounded-xl font-bold text-sm">
                Cancel
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default TableCard;