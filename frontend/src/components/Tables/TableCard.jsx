import { useState } from 'react';
import { MdDelete, MdAccessTime, MdPerson } from 'react-icons/md';
import useCartStore from '../../store/cartStore';
import TableService from '../../services/table.service';
import toast from 'react-hot-toast';
import { notifyTableOccupied, notifyTableCleared, notifyError, notifySuccess } from '../../utils/notificationHelper';

const TableCard = ({ table, onUpdate }) => {
  const { setTable, setCustomerName, selectedTable, clearTableAndCustomer } = useCartStore();
  const [showSelectModal, setShowSelectModal] = useState(false);
  const [tempCustomerName, setTempCustomerName] = useState('');
  const [updating, setUpdating] = useState(false);
  const [localStatus, setLocalStatus] = useState(table.status);
  const [localCustomer, setLocalCustomer] = useState(table.occupied_by_customer);

  const isOccupied = localStatus === 'occupied';
  const isSelected = selectedTable === table.id;

  const formatTime = (dateString) => {
    if (!dateString) return '';
    const date = new Date(dateString);
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };

  const handleSelectTable = () => {
    // Only allow selection if table is occupied
    if (!isOccupied) {
      toast.error('Please check-in to a table first');
      return;
    }
    
    if (isSelected) {
      // Unselect the table
      clearTableAndCustomer();
      toast.success(`Table ${table.table_number} unselected`);
    } else {
      // Select the table
      setTable(table.id);
      if (localCustomer) {
        setCustomerName(localCustomer);
      }
      toast.success(`Table ${table.table_number} selected`);
    }
  };

  const handleConfirmSelect = async () => {
    if (!tempCustomerName.trim()) {
      const errorMsg = 'Enter customer name';
      notifyError(errorMsg);
      toast.error(errorMsg);
      return;
    }
    setUpdating(true);
    
    setLocalStatus('occupied');
    setLocalCustomer(tempCustomerName);
    
    try {
      const partyId = `P-${table.id}-${Date.now()}`;
      await TableService.occupyTable(table.id, tempCustomerName, partyId);
      notifyTableOccupied(table.table_number, tempCustomerName); 
      setTable(table.id);
      setCustomerName(tempCustomerName);
      toast.success(`Table ${table.table_number} selected for ${tempCustomerName}`);
      setShowSelectModal(false);
      setTempCustomerName('');
      
      if (onUpdate) await onUpdate();
    } catch (error) {
      setLocalStatus(table.status);
      setLocalCustomer(table.occupied_by_customer);
      notifyError(error.response?.data?.detail || 'Failed to select table');
      toast.error('Failed to occupy');
    } finally {
      setUpdating(false);
    }
  };

  const handleClearTable = async (e) => {
    e.stopPropagation();
    if (!window.confirm(`Clear Table ${table.table_number}?`)) return;
    
    setUpdating(true);
    setLocalStatus('available');
    setLocalCustomer(null);
    
    try {
      await TableService.updateTableStatus(table.id, 'available');
      notifyTableCleared(table.table_number);
      if (isSelected) clearTableAndCustomer();
      toast.success('Table is now free');
      
      if (onUpdate) await onUpdate();
    } catch (error) {
      setLocalStatus('occupied');
      setLocalCustomer(table.occupied_by_customer);
      notifyError(error.response?.data?.detail || 'Failed to clear table');  
      toast.error('Failed to clear table');
    } finally {
      setUpdating(false);
    }
  };

  const handleDelete = async (e) => {
    e.stopPropagation();
    if (!window.confirm(`Delete Table ${table.table_number}?`)) return;
    
    setUpdating(true);
    try {
      await TableService.deleteTable(table.id);
      notifySuccess('Table Deleted', `Table ${table.table_number} has been permanently deleted`);
      toast.success('Table deleted');
      
      if (onUpdate) await onUpdate();
    } catch (error) {
      const errorMsg = error.response?.data?.detail || 'Delete failed';
      notifyError(errorMsg);
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
        ${isSelected && isOccupied ? 'ring-4 ring-emerald-300 shadow-md scale-[1.02]' : !isOccupied ? 'cursor-pointer' : 'hover:shadow-md'}
          ${updating ? 'opacity-70 pointer-events-none' : ''}
        `}
      >
        <div className="text-center flex flex-col items-center justify-center gap-1 sm:gap-1.5 grow w-full">
          <span className="text-gray-600 font-black text-sm sm:text-lg uppercase tracking-wider">
            {table.table_number}
          </span>
          
          <div className="flex items-center text-gray-400 gap-1 mb-1">
            <MdPerson size={14} className="sm:w-4" />
            <span className="text-[10px] sm:text-xs font-bold text-gray-500">{table.capacity} Seats</span>
          </div>
          
          <div className="border-t border-gray-100 w-3/4 mb-1"></div>

          {isOccupied ? (
            <div className="flex flex-col items-center gap-0.5 sm:gap-1 w-full px-1">
              <span className="text-[11px] sm:text-sm font-bold text-gray-800 truncate max-w-full">
                {localCustomer || table.occupied_by_customer}
              </span>
              <div className="flex items-center gap-1 text-[#F28C28]">
                <MdAccessTime size={10} className="sm:w-3" />
                <span className="text-[9px] sm:text-[10px] font-bold">
                  {formatTime(table.updated_at || table.occupied_at)}
                </span>
              </div>
            </div>
          ) : (
            <span className="text-[10px] sm:text-sm font-bold text-[#58D39E] uppercase tracking-widest">
              Free
            </span>
          )}
        </div>

        {!isOccupied && (
          <button 
            onClick={(e) => {
              e.stopPropagation();
              setShowSelectModal(true);
            }}
            disabled={updating}
            className="sm:absolute sm:bottom-2 sm:left-2 mt-2 w-full sm:w-auto text-[9px] bg-gray-100 hover:bg-orange-50 hover:text-[#F28C28] text-gray-500 px-2 py-1 rounded uppercase font-bold transition-colors shadow-sm disabled:opacity-50"
          >
            Check-in
          </button>
        )}
        
        {isOccupied && (
          <button 
            onClick={handleClearTable}
            disabled={updating}
            className="sm:absolute sm:bottom-2 sm:left-2 mt-2 w-full sm:w-auto text-[9px] bg-gray-100 hover:bg-red-50 hover:text-red-500 text-gray-500 px-2 py-1 rounded uppercase font-bold transition-colors shadow-sm disabled:opacity-50"
          >
            Clear
          </button>
        )}
        
        <button 
          onClick={handleDelete}
          disabled={updating}
          className="absolute top-2 right-2 opacity-100 lg:opacity-0 lg:group-hover:opacity-100 text-gray-300 hover:text-red-500 transition-opacity p-1 disabled:opacity-50"
        >
          <MdDelete size={18} />
        </button>
      </div>

      {/* Responsive Modal */}
      {showSelectModal && (
        <div className="fixed inset-0 bg-black/60 flex items-center justify-center z-100 p-4 backdrop-blur-sm">
          <div className="bg-white rounded-2xl p-6 w-full max-w-[320px] shadow-2xl animate-in fade-in zoom-in duration-200">
            <h3 className="font-black text-gray-800 mb-2 text-lg">Check-in</h3>
            <p className="text-gray-500 text-xs mb-4">Assigning Customer to Table {table.table_number}</p>
            
            <input 
              className="w-full border-2 border-gray-100 rounded-xl p-3 mb-5 outline-none focus:border-[#F28C28] text-sm transition-colors"
              placeholder="Enter Customer Name"
              value={tempCustomerName}
              onChange={(e) => setTempCustomerName(e.target.value)}
              autoFocus
            />
            
            <div className="flex flex-col gap-2">
              <button 
                onClick={handleConfirmSelect} 
                disabled={updating}
                className="w-full bg-[#F28C28] text-white py-3 rounded-xl font-bold text-sm shadow-lg shadow-orange-200 active:scale-95 transition-transform disabled:opacity-50"
              >
                {updating ? 'Processing...' : 'Confirm Check-in'}
              </button>
              <button 
                onClick={() => setShowSelectModal(false)} 
                className="w-full bg-gray-50 text-gray-500 py-3 rounded-xl font-bold text-sm hover:bg-gray-100 transition-colors"
              >
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