import React, { useState, useEffect } from 'react';
import { MdRefresh, MdShoppingCart, MdTrendingUp, MdHistory, MdCheckCircle, MdWarning } from 'react-icons/md';
import RecommendationService from '../../services/recommendation.service';
import toast from 'react-hot-toast';
import { notifySuccess, notifyError } from '../../utils/notificationHelper';

const RecommendationsTab = () => {
  const [training, setTraining] = useState(false);
  const [lastTrained, setLastTrained] = useState(null);
  const [stats, setStats] = useState({
    totalOrders: 0,
    totalProducts: 0,
    rulesCount: 0,
    lastTrainingStatus: null
  });
  const [loading, setLoading] = useState(true);
  const [popularProducts, setPopularProducts] = useState([]);

  useEffect(() => {
    loadStats();
    loadPopularProducts();
  }, []);

  const loadStats = async () => {
    try {
      const popular = await RecommendationService.getPopularProducts(5);
      setStats(prev => ({
        ...prev,
        totalProducts: popular.length
      }));
    } catch (error) {
      console.error('Failed to load stats:', error);
    } finally {
      setLoading(false);
    }
  };

  const loadPopularProducts = async () => {
    try {
      const products = await RecommendationService.getPopularProducts(10);
      setPopularProducts(products);
    } catch (error) {
      console.error('Failed to load popular products:', error);
    }
  };

  const handleTrainModel = async () => {
    setTraining(true);
    try {
      const result = await RecommendationService.trainModel(0.01, 0.5);
      
      if (result.rules_count > 0) {
        notifySuccess('Model Trained', `Successfully trained with ${result.rules_count} association rules`);
        toast.success(`Model trained with ${result.rules_count} rules`);
        setStats(prev => ({
          ...prev,
          rulesCount: result.rules_count,
          lastTrainingStatus: 'success'
        }));
        setLastTrained(new Date().toISOString());
      } else {
        notifyError('Insufficient data. Add more orders first.');
        toast.error('Insufficient data. Add more orders first.');
        setStats(prev => ({
          ...prev,
          lastTrainingStatus: 'failed'
        }));
      }
    } catch (error) {
      notifyError(error.response?.data?.detail || 'Training failed');
      toast.error('Training failed');
      setStats(prev => ({
        ...prev,
        lastTrainingStatus: 'failed'
      }));
    } finally {
      setTraining(false);
      await loadPopularProducts();
    }
  };

  const formatDate = (dateString) => {
    if (!dateString) return 'Never';
    const date = new Date(dateString);
    return date.toLocaleString();
  };

  if (loading) {
    return (
      <div className="flex justify-center py-20">
        <div className="animate-spin rounded-full h-10 w-10 border-4 border-[#3A707A] border-t-transparent"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Training Card */}
      <div className="bg-white rounded-2xl shadow-sm overflow-hidden border border-gray-50">
        <div className="p-6 border-b border-gray-100">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-[#3A707A]/10 rounded-lg">
              <MdRefresh className="text-[#3A707A]" size={24} />
            </div>
            <div>
              <h3 className="font-bold text-gray-800">Train Recommendation Model</h3>
              <p className="text-xs text-gray-400 mt-1">Update the recommendation engine with latest order data</p>
            </div>
          </div>
        </div>
        
        <div className="p-6">
          <div className="bg-blue-50 rounded-lg p-4 mb-6">
            <p className="text-sm text-blue-800">
              The recommendation system uses the Apriori algorithm to find products frequently bought together.
              Training the model with historical order data will improve product recommendations.
            </p>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
            <div className="bg-gray-50 rounded-lg p-4 text-center">
              <p className="text-2xl font-bold text-[#3A707A]">{stats.rulesCount}</p>
              <p className="text-xs text-gray-500 mt-1">Association Rules</p>
            </div>
            <div className="bg-gray-50 rounded-lg p-4 text-center">
              <p className="text-2xl font-bold text-[#3A707A]">{stats.totalProducts}</p>
              <p className="text-xs text-gray-500 mt-1">Products Analyzed</p>
            </div>
            <div className="bg-gray-50 rounded-lg p-4 text-center">
              <p className="text-2xl font-bold text-[#3A707A]">{stats.lastTrainingStatus === 'success' ? '✓' : '—'}</p>
              <p className="text-xs text-gray-500 mt-1">Last Training</p>
              <p className="text-[10px] text-gray-400">{formatDate(lastTrained)}</p>
            </div>
          </div>
          
          <button
            onClick={handleTrainModel}
            disabled={training}
            className="w-full py-3 bg-[#3A707A] text-white rounded-xl font-bold text-sm hover:bg-[#2E5A63] transition-colors disabled:opacity-50 flex items-center justify-center gap-2"
          >
            {training ? (
              <>
                <div className="animate-spin rounded-full h-4 w-4 border-2 border-white border-t-transparent"></div>
                Training...
              </>
            ) : (
              <>
                <MdRefresh size={18} />
                Train Recommendation Model
              </>
            )}
          </button>
        </div>
      </div>

      {/* Popular Products Card */}
      <div className="bg-white rounded-2xl shadow-sm overflow-hidden border border-gray-50">
        <div className="p-6 border-b border-gray-100">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-orange-100 rounded-lg">
              <MdTrendingUp className="text-orange-600" size={24} />
            </div>
            <div>
              <h3 className="font-bold text-gray-800">Popular Products</h3>
              <p className="text-xs text-gray-400 mt-1">Top selling items based on order history</p>
            </div>
          </div>
        </div>
        
        <div className="divide-y divide-gray-100">
          {popularProducts.length === 0 ? (
            <div className="p-6 text-center text-gray-400">
              <MdShoppingCart size={40} className="mx-auto mb-2" />
              <p>No popular products yet</p>
              <p className="text-xs">Complete more orders to see popular items</p>
            </div>
          ) : (
            popularProducts.map((product, index) => (
              <div key={product.product_id} className="p-4 hover:bg-gray-50 transition-colors">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <div className="w-8 h-8 rounded-full bg-[#3A707A]/10 flex items-center justify-center">
                      <span className="text-sm font-bold text-[#3A707A]">#{index + 1}</span>
                    </div>
                    <div>
                      <p className="font-medium text-gray-800">{product.name}</p>
                      <p className="text-xs text-gray-500">रु {product.price}</p>
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    <span className="text-xs text-gray-400">Score: {product.recommendation_score}</span>
                    <MdCheckCircle className="text-green-500" size={16} />
                  </div>
                </div>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
};

export default RecommendationsTab;