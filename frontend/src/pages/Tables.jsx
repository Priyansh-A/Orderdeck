import React, { useEffect, useState } from 'react';
import TableCard from '../components/Tables/TableCard';
import useTableStore from '../store/tableStore';
import useCartStore from '../store/cartStore';
import { MdAdd, MdRefresh } from 'react-icons/md';
import toast from 'react-hot-toast';

const Tables = () => {
  const { tables, loading, fetchTables, resetAll, addTable } = useTableStore();
  const { clearTableAndCustomer } = useCartStore(); 
  const [filter, setFilter] = useState('all');
  const [showAddModal, setShowAddModal] = useState(false);
  const [newTable, setNewTable] = useState({ table_number: '', capacity: 4 });
  const [processing, setProcessing] = useState(false);

  
  useEffect(() => {
    fetchTables();
  }, [fetchTables]);

  const handleAddTable = async () => {
    if (!newTable.table_number.trim()) return toast.error('Enter table number');
    setProcessing(true);
    try {
      await addTable(newTable);
      toast.success(`Table ${newTable.table_number} added`);
      setShowAddModal(false);
      setNewTable({ table_number: '', capacity: 4 });
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to add table');
    } finally {
      setProcessing(false);
    }
  };

  const handleResetAll = async () => {
    if (!window.confirm('Reset ALL tables to available? This will also clear your current selection.')) return;
    
    setProcessing(true);
    const loadingToast = toast.loading('Resetting tables...');
    try {
      await resetAll();
      clearTableAndCustomer();
      
      toast.success('System reset: All tables available and cart cleared', { id: loadingToast });
    } catch (error) {
      toast.error('Reset failed', { id: loadingToast });
    } finally {
      setProcessing(false);
    }
  };

  const statusFilters = [
    { value: 'all', label: 'All', count: tables.length, color: 'bg-gray-100 text-gray-600', active: 'bg-[#3A707A] text-white' },
    { value: 'available', label: 'Available', count: tables.filter(t => t.status === 'available').length, color: 'bg-green-50 text-green-600', active: 'bg-green-600 text-white' },
    { value: 'occupied', label: 'Occupied', count: tables.filter(t => t.status === 'occupied').length, color: 'bg-orange-50 text-orange-600', active: 'bg-orange-600 text-white' },
  ];

  const filteredTables = filter === 'all' ? tables : tables.filter(t => t.status === filter);

  if (loading && tables.length === 0) {
    return (
      <div className="flex justify-center py-20">
        <div className="animate-spin rounded-full h-10 w-10 border-4 border-[#3A707A] border-t-transparent"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[#FDFDFD] p-6 pb-32">
      <div className="max-w-7xl mx-auto mb-8">
        <div className="flex gap-3 overflow-x-auto no-scrollbar pb-2">
          {statusFilters.map((opt) => (
            <button
              key={opt.value}
              onClick={() => setFilter(opt.value)}
              className={`px-5 py-2 rounded-lg font-bold text-sm flex items-center gap-2 transition-all whitespace-nowrap
                ${filter === opt.value ? opt.active : `${opt.color} hover:opacity-80`}`}
            >
              {opt.label}
              <span className={`text-[10px] px-1.5 py-0.5 rounded-full ${filter === opt.value ? 'bg-white/20' : 'bg-black/5'}`}>
                {opt.count}
              </span>
            </button>
          ))}
        </div>
      </div>

      <div className="max-w-7xl mx-auto grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-6 gap-4">
        {filteredTables.length === 0 ? (
          <div className="col-span-full text-center py-20 bg-white rounded-2xl border border-dashed border-gray-200 text-gray-400">
            No tables found.
          </div>
        ) : (
          filteredTables.map(table => <TableCard key={table.id} table={table} />)
        )}
      </div>

      {/* Floating Action Bar */}
      <div className="fixed bottom-6 left-1/2 -translate-x-1/2 bg-white shadow-2xl border border-gray-100 px-4 py-2 rounded-xl flex gap-3 z-40 items-center">
        <button onClick={() => setShowAddModal(true)} className="flex items-center gap-1.5 bg-green-500 text-white px-4 py-2 rounded-lg font-bold text-[10px] uppercase">
          <MdAdd size={16} /> Add Table
        </button>
        <button onClick={handleResetAll} disabled={processing} className="flex items-center gap-1.5 bg-orange-500 text-white px-4 py-2 rounded-lg font-bold text-[10px] uppercase disabled:opacity-50">
          <MdRefresh size={16} /> Reset All
        </button>
      </div>

      {/* Add Table Modal */}
      {showAddModal && (
        <div className="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl shadow-2xl w-full max-w-md p-6">
            <h3 className="text-lg font-bold mb-4">Add New Table</h3>
            <div className="space-y-4">
              <input
                placeholder="Table Number (e.g., T1)"
                className="w-full px-3 py-2 border rounded-lg outline-none focus:ring-2 focus:ring-[#3A707A]"
                value={newTable.table_number}
                onChange={e => setNewTable({...newTable, table_number: e.target.value})}
              />
              <input
                type="number"
                placeholder="Capacity"
                className="w-full px-3 py-2 border rounded-lg outline-none focus:ring-2 focus:ring-[#3A707A]"
                value={newTable.capacity}
                onChange={e => setNewTable({...newTable, capacity: parseInt(e.target.value) || 1})}
              />
              <div className="flex gap-3 pt-2">
                <button onClick={handleAddTable} disabled={processing} className="flex-1 py-2 bg-[#3A707A] text-white rounded-lg font-bold">
                  {processing ? 'Adding...' : 'Add Table'}
                </button>
                <button onClick={() => setShowAddModal(false)} className="flex-1 py-2 bg-gray-200 text-gray-700 rounded-lg font-bold">
                  Cancel
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Tables;