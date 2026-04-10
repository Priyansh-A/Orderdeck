import React, { useState, useEffect } from 'react';
import { MdAdd, MdEdit, MdDelete, MdPerson } from 'react-icons/md';
import authService from '../../services/auth.service';
import UserModal from './UserModal';
import toast from 'react-hot-toast';
import { notifySuccess, notifyError } from '../../utils/notificationHelper';

const UsersTab = () => {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [editingUser, setEditingUser] = useState(null);

  useEffect(() => {
    loadUsers();
  }, []);

  const loadUsers = async () => {
    setLoading(true);
    try {
      const data = await authService.getAllUsers();
      setUsers(data);
    } catch (error) {
      toast.error('Failed to load users');
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (user) => {
    if (!window.confirm(`Delete user ${user.username}?`)) return;
    try {
      await authService.deleteUser(user.id);
      notifySuccess('User Deleted', `User ${user.username} has been deleted`);
      toast.success('User deleted');
      loadUsers();
    } catch (error) {
      notifyError(error.response?.data?.detail || 'Failed to delete user');
      toast.error('Failed to delete user');
    }
  };

  const openModal = (user = null) => {
    setEditingUser(user);
    setShowModal(true);
  };

  if (loading) {
    return (
      <div className="flex justify-center py-20">
        <div className="animate-spin rounded-full h-10 w-10 border-4 border-[#3A707A] border-t-transparent"></div>
      </div>
    );
  }

  return (
    <>
      <div className="mb-6 flex justify-end">
        <button
          onClick={() => openModal()}
          className="flex items-center gap-2 px-4 py-2 bg-[#3A707A] text-white rounded-lg text-sm font-bold hover:bg-[#2E5A63] transition-colors"
        >
          <MdAdd size={18} />
          Add User
        </button>
      </div>

      <div className="bg-white rounded-2xl shadow-sm overflow-hidden border border-gray-50">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-[#E9EDF2]">
              <tr className="text-[#6C757D] text-[11px] uppercase font-bold tracking-widest">
                <th className="py-4 px-6 text-left">User</th>
                <th className="py-4 px-6 text-left">Email</th>
                <th className="py-4 px-6 text-left">Role</th>
                <th className="py-4 px-6 text-center">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-50">
              {users.map((user) => (
                <tr key={user.id} className="hover:bg-gray-50 transition-colors">
                  <td className="py-4 px-6">
                    <div className="flex items-center gap-3">
                      <div className="w-8 h-8 rounded-full bg-[#3A707A]/10 flex items-center justify-center">
                        <MdPerson className="text-[#3A707A]" size={16} />
                      </div>
                      <span className="font-medium text-gray-800">{user.username}</span>
                    </div>
                  </td>
                  <td className="py-4 px-6 text-gray-600">{user.email}</td>
                  <td className="py-4 px-6">
                    <span className={`px-2 py-1 rounded-full text-xs font-medium capitalize ${
                      user.role === 'manager' ? 'bg-purple-100 text-purple-700' :
                      'bg-blue-100 text-blue-700'
                    }`}>
                      {user.role}
                    </span>
                  </td>
                  <td className="py-4 px-6 text-center">
                    <div className="flex justify-center gap-2">
                      <button onClick={() => openModal(user)} className="p-1.5 text-blue-500 hover:bg-blue-50 rounded-lg transition-colors">
                        <MdEdit size={18} />
                      </button>
                      <button onClick={() => handleDelete(user)} className="p-1.5 text-red-500 hover:bg-red-50 rounded-lg transition-colors">
                        <MdDelete size={18} />
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {showModal && (
        <UserModal
          user={editingUser}
          onClose={() => {
            setShowModal(false);
            setEditingUser(null);
          }}
          onSuccess={loadUsers}
        />
      )}
    </>
  );
};

export default UsersTab;