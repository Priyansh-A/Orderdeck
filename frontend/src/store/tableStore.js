import { create } from 'zustand';
import TableService from '../services/table.service';

const useTableStore = create((set, get) => ({
  tables: [],
  loading: false,
  error: null,

  fetchTables: async () => {
    set({ loading: true });
    try {
      const data = await TableService.getAllTables();
      set({ tables: data, loading: false });
    } catch (error) {
      set({ error: error.message, loading: false });
    }
  },

  occupyTable: async (id, customerName, partyId) => {
    try {
      await TableService.occupyTable(id, customerName, partyId);
      await get().fetchTables();
    } catch (error) {
      throw error;
    }
  },

  updateStatus: async (id, status) => {
    try {
      await TableService.updateTableStatus(id, status);
      await get().fetchTables();
    } catch (error) {
      throw error;
    }
  },

  resetAll: async () => {
    try {
      await TableService.resetAllTables();
      await get().fetchTables();
    } catch (error) {
      throw error;
    }
  },

  deleteTable: async (id) => {
    try {
      await TableService.deleteTable(id);
      await get().fetchTables();
    } catch (error) {
      throw error;
    }
  },

  addTable: async (tableData) => {
    try {
      await TableService.createTable(tableData);
      await get().fetchTables();
    } catch (error) {
      throw error;
    }
  }
}));

export default useTableStore;