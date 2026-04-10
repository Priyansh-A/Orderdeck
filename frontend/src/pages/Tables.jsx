import React, { useEffect, useState } from 'react';
import TableCard from '../components/Tables/TableCard';
import TableService from '../services/table.service';
import { MdAdd, MdRefresh, MdBlock } from 'react-icons/md';
import toast from 'react-hot-toast';

const Tables = () => {
  const [tables, setTables] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState('all');
  const [showAddModal, setShowAddModal] = useState(false);
  const [newTable, setNewTable] = useState({ table_number: '', capacity: 4 });
  const [adding, setAdding] = useState(false);

  useEffect(() => { loadTables(); }, []);

  const loadTables = async () => {
    try {
      const data = await TableService.getAllTables();
      setTables(data);
    } catch (error) {
      toast.error('Failed to load tables');
    } finally {
      setLoading(false);
    }
  };

  const handleAddTable = async () => {
    if (!newTable.table_number.trim()) {
      toast.error('Please enter table number');
      return;
    }
    setAdding(true);
    try {
      await TableService.createTable(newTable);
      toast.success(`Table ${newTable.table_number} added`);
      setShowAddModal(false);
      setNewTable({ table_number: '', capacity: 4 });
      loadTables();
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to add table');
    } finally {
      setAdding(false);
    }
  };

  const handleResetAll = async () => {
    if (window.confirm('Reset ALL tables to available?')) {
      await TableService.resetAllTables();
      loadTables();
      toast.success('All tables reset');
    }
  };

  // Status filter config with colors
  const statusFilters = [
    { value: 'all', label: 'All', count: tables.length, color: 'bg-gray-100 text-gray-600' },
    { value: 'available', label: 'Available', count: tables.filter(t => t.status === 'available').length, color: 'bg-green-50 text-green-600' },
    { value: 'occupied', label: 'Occupied', count: tables.filter(t => t.status === 'occupied').length, color: 'bg-orange-50 text-orange-600' },
  ];

  const getActiveColor = (optValue) => {
    if (filter !== optValue) return optValue.color;
    switch(optValue) {
      case 'available': return 'bg-green-600 text-white';
      case 'occupied': return 'bg-orange-600 text-white';
      default: return 'bg-[#3A707A] text-white';
    }
  };

  if (loading) return <div className="p-10 text-center text-sm font-bold text-gray-400">Loading...</div>;

  return (
    <div className="pb-24 px-4">
      {/* Filters with Status Colors */}
      <div className="flex gap-3 mb-8 overflow-x-auto no-scrollbar py-2">
        {statusFilters.map((opt) => (
          <button
            key={opt.value}
            onClick={() => setFilter(opt.value)}
            className={`px-5 py-2 rounded-lg font-bold text-sm flex items-center gap-2 transition-all whitespace-nowrap
              ${filter === opt.value 
                ? getActiveColor(opt.value) 
                : `${opt.color} hover:opacity-80`
              }`}
          >
            {opt.label}
            <span className={`text-[10px] px-1.5 py-0.5 rounded-full ${
              filter === opt.value 
                ? 'bg-white/20 text-white' 
                : 'bg-black/5 text-gray-600'
            }`}>
              {opt.count}
            </span>
          </button>
        ))}
      </div>

      {/* Table Grid */}
      <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-6 gap-4">
        {tables
          .filter(t => filter === 'all' || t.status === filter)
          .map((table) => (
            <TableCard key={table.id} table={table} onUpdate={loadTables} />
          ))}
      </div>

      {/* Action Bar */}
      <div className="fixed bottom-6 left-1/2 -translate-x-1/2 bg-white shadow-2xl border border-gray-100 px-4 py-2 rounded-xl flex gap-3 z-40 items-center">
        <button 
          onClick={() => setShowAddModal(true)}
          className="flex items-center gap-1.5 bg-green-500 text-white px-4 py-2 rounded-lg font-bold text-[10px] uppercase hover:bg-green-600 transition-colors"
        >
          <MdAdd size={16} /> Add Table
        </button>
        <button 
          onClick={handleResetAll}
          className="flex items-center gap-1.5 bg-orange-500 text-white px-4 py-2 rounded-lg font-bold text-[10px] uppercase hover:bg-orange-600 transition-colors"
        >
          <MdRefresh size={16} /> Reset All
        </button>
      </div>

      {/* Add Table Modal */}
      {showAddModal && (
        <>
          <div className="fixed inset-0 bg-black/50 z-50" onClick={() => setShowAddModal(false)} />
          <div className="fixed top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-full max-w-md bg-white rounded-2xl shadow-2xl z-50 p-6">
            <h3 className="text-lg font-bold mb-4">Add New Table</h3>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium mb-1">Table Number</label>
                <input
                  type="text"
                  value={newTable.table_number}
                  onChange={(e) => setNewTable({ ...newTable, table_number: e.target.value })}
                  placeholder="e.g., T1, Table 1"
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-[#3A707A] outline-none"
                  autoFocus
                />
              </div>
              <div>
                <label className="block text-sm font-medium mb-1">Capacity</label>
                <input
                  type="number"
                  value={newTable.capacity}
                  onChange={(e) => setNewTable({ ...newTable, capacity: parseInt(e.target.value) || 1 })}
                  min="1"
                  max="20"
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-[#3A707A] outline-none"
                />
              </div>
              <div className="flex gap-3 pt-4">
                <button
                  onClick={handleAddTable}
                  disabled={adding}
                  className="flex-1 py-2 bg-[#3A707A] text-white rounded-lg font-bold hover:bg-[#2E5A63] transition-colors disabled:opacity-50"
                >
                  {adding ? 'Adding...' : 'Add Table'}
                </button>
                <button
                  onClick={() => setShowAddModal(false)}
                  className="flex-1 py-2 bg-gray-200 text-gray-700 rounded-lg font-bold hover:bg-gray-300 transition-colors"
                >
                  Cancel
                </button>
              </div>
            </div>
          </div>
        </>
      )}
    </div>
  );
};

export default Tables;