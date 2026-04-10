import React, { useState } from 'react';
import { MdClose, MdSave } from 'react-icons/md';
import authService from '../../services/auth.service';
import toast from 'react-hot-toast';
import { notifySuccess, notifyError } from '../../utils/notificationHelper';

const UserModal = ({ user, onClose, onSuccess }) => {
  const [formData, setFormData] = useState({
    username: user?.username || '',
    email: user?.email || '',
    password: '',
    role: user?.role || 'staff'
  });
  const [loading, setLoading] = useState(false);

  const handleSubmit = async () => {
    if (!formData.username || !formData.email) {
      toast.error('Please fill all required fields');
      return;
    }
    if (!user && !formData.password) {
      toast.error('Password is required for new users');
      return;
    }

    setLoading(true);
    try {
      if (user) {
        await authService.updateUser(user.id, formData);
        notifySuccess('User Updated', `User ${formData.username} has been updated`);
        toast.success('User updated successfully');
      } else {
        await authService.signup(formData);
        notifySuccess('User Created', `User ${formData.username} has been created`);
        toast.success('User created successfully');
      }
      onSuccess();
      onClose();
    } catch (error) {
      notifyError(error.response?.data?.detail || 'Operation failed');
      toast.error('Operation failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4">
      <div className="bg-white rounded-2xl w-full max-w-md p-6">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-xl font-bold">{user ? 'Edit User' : 'Add User'}</h2>
          <button onClick={onClose} className="p-1 hover:bg-gray-100 rounded-lg">
            <MdClose size={20} />
          </button>
        </div>
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium mb-1">Username *</label>
            <input
              type="text"
              value={formData.username}
              onChange={(e) => setFormData({ ...formData, username: e.target.value })}
              className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-[#3A707A] outline-none"
              placeholder="Enter username"
            />
          </div>
          <div>
            <label className="block text-sm font-medium mb-1">Email *</label>
            <input
              type="email"
              value={formData.email}
              onChange={(e) => setFormData({ ...formData, email: e.target.value })}
              className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-[#3A707A] outline-none"
              placeholder="Enter email"
            />
          </div>
          {!user && (
            <div>
              <label className="block text-sm font-medium mb-1">Password *</label>
              <input
                type="password"
                value={formData.password}
                onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-[#3A707A] outline-none"
                placeholder="Enter password"
              />
            </div>
          )}
          <div>
            <label className="block text-sm font-medium mb-1">Role</label>
            <select
              value={formData.role}
              onChange={(e) => setFormData({ ...formData, role: e.target.value })}
              className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-[#3A707A] outline-none"
            >
              <option value="staff">Staff</option>
              <option value="manager">Manager</option>
            </select>
          </div>
        </div>
        <div className="flex gap-3 mt-6">
          <button onClick={handleSubmit} disabled={loading} className="flex-1 py-2 bg-[#3A707A] text-white rounded-lg font-medium disabled:opacity-50">
            <MdSave size={16} className="inline mr-1" /> {loading ? 'Saving...' : (user ? 'Update' : 'Create')}
          </button>
          <button onClick={onClose} className="flex-1 py-2 bg-gray-200 rounded-lg font-medium">
            Cancel
          </button>
        </div>
      </div>
    </div>
  );
};

export default UserModal;