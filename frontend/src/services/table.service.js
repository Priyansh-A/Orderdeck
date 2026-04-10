import api from './api';

class TableService {
  async getAllTables(skip = 0, limit = 100, statusFilter = null) {
    const params = { skip, limit };
    if (statusFilter) params.status_filter = statusFilter;
    
    const response = await api.get('/tables/', { params });
    return response.data;
  }

  async getAvailableTables(capacity = null) {
    const params = {};
    if (capacity) params.capacity = capacity;
    
    const response = await api.get('/tables/available', { params });
    return response.data;
  }

  async getOccupiedTables() {
    const response = await api.get('/tables/occupied');
    return response.data;
  }

  async getTable(id) {
    const response = await api.get(`/tables/${id}`);
    return response.data;
  }

  async createTable(tableData) {
    const response = await api.post('/tables/', tableData);
    return response.data;
  }

  async updateTable(id, tableData) {
    const response = await api.patch(`/tables/${id}`, tableData);
    return response.data;
  }

  async updateTableStatus(id, status) {
    const response = await api.patch(`/tables/${id}/status`, { status });
    return response.data;
  }

  async occupyTable(id, customerName, partyId) {
    const response = await api.post(`/tables/${id}/occupy`, null, {
      params: { customer_name: customerName, party_id: partyId }
    });
    return response.data;
  }

  async deleteTable(id) {
    const response = await api.delete(`/tables/${id}`);
    return response.status === 204;
  }

  async resetAllTables() {
    const response = await api.post('/tables/reset');
    return response.data;
  }

  async deleteAllTables() {
    const response = await api.delete('/tables/delete-all');
    return response.data;
  }
}

export default new TableService();