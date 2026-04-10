import React, { useState, useEffect } from 'react';
import ProductService from '../../services/product.service';
import MenuCard from './MenuCard';
import CategoryTabs from './CategoryTabs';

const MenuList = () => {
  const [products, setProducts] = useState([]);
  const [filteredProducts, setFilteredProducts] = useState([]);
  const [selectedCategory, setSelectedCategory] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => { loadProducts(); }, []);

  useEffect(() => {
    const filtered = selectedCategory 
      ? products.filter(p => p.category_id === selectedCategory) 
      : products;
    setFilteredProducts(filtered);
  }, [selectedCategory, products]);

  const loadProducts = async () => {
    try {
      const data = await ProductService.getAvailableProducts();
      setProducts(data);
      setFilteredProducts(data);
    } catch (error) {
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) return <div className="p-10 text-center">Loading...</div>;

  return (
    <div className="container mx-auto px-2">
      <CategoryTabs 
        selectedCategory={selectedCategory}
        onCategoryChange={setSelectedCategory}
      />
      <div className="grid grid-cols-1 xs:grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-6 gap-3 sm:gap-4">
        {filteredProducts.map((product) => (
          <MenuCard key={product.id} product={product} />
        ))}
      </div>
    </div>
  );
};

export default MenuList;