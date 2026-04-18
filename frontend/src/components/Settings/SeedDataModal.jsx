import React, { useState } from 'react';
import { MdClose } from 'react-icons/md';
import api from '../../services/api';
import toast from 'react-hot-toast';

const menuData = {
  "categories": [
    {
      "name": "Salads",
      "products": [
        { "name": "Caesar Salad", "description": "Crisp romaine lettuce, parmesan cheese, croutons", "price": 129, "image_filename": "ceasar_salad.jpg", "is_available": true },
        { "name": "Country Ranch Green Salad", "description": "Fresh mixed greens with creamy ranch dressing", "price": 199, "image_filename": "country_ranch_green_salad.jpg", "is_available": true },
        { "name": "Greek Salad", "description": "Cucumber, tomato, feta cheese, olives", "price": 249, "image_filename": "greek_salad.jpg", "is_available": true }
      ]
    },
    {
      "name": "Burgers & Sandwiches",
      "products": [
        { "name": "Chicken Burger", "description": "Grilled chicken patty with lettuce, tomato, and mayo", "price": 499, "image_filename": "chicken_burger.jpg", "is_available": true },
        { "name": "Veg Burger", "description": "Plant-based patty with fresh vegetables", "price": 299, "image_filename": "veg_burger.jpg", "is_available": true }
      ]
    },
    {
      "name": "Pizza",
      "products": [
        { "name": "Margaretta Pizza", "description": "Fresh mozzarella, tomato sauce, basil", "price": 699, "image_filename": "margaretta_pizza.jpg", "is_available": true },
        { "name": "Veg Pizza", "description": "Bell peppers, mushrooms, onions, olives", "price": 599, "image_filename": "veg_pizza.jpg", "is_available": true }
      ]
    },
    {
      "name": "Appetizers & Sides",
      "products": [
        { "name": "Chimichuri Wings", "description": "Crispy chicken wings with chimichurri sauce", "price": 399, "image_filename": "chimichuri_wings.jpg", "is_available": true },
        { "name": "Mozzarella Sticks", "description": "Golden fried mozzarella with marinara sauce", "price": 399, "image_filename": "mozzarella_sticks.jpg", "is_available": true },
        { "name": "French Fries", "description": "Crispy golden fries with sea salt", "price": 199, "image_filename": "french_fries.jpg", "is_available": true },
        { "name": "Fish Finger", "description": "Crispy breaded fish strips with tartar sauce", "price": 299, "image_filename": "fishfinger.jpg", "is_available": true }
      ]
    },
    {
      "name": "Soups",
      "products": [
        { "name": "Creamy Soup", "description": "Rich and creamy vegetable soup", "price": 299, "image_filename": "creamysoup.jpg", "is_available": true },
        { "name": "Hot and Sour Soup", "description": "Spicy and tangy Asian-style soup", "price": 399, "image_filename": "hotandsoursoup.jpg", "is_available": true }
      ]
    },
    {
      "name": "Desserts",
      "products": [
        { "name": "Chocolate Lava Cake", "description": "Warm chocolate cake with molten center", "price": 249, "image_filename": "chocolate_lava_cake.jpg", "is_available": true },
        { "name": "Ice Cream", "description": "Vanilla, chocolate, or strawberry", "price": 199, "image_filename": "ice_cream.jpg", "is_available": true },
        { "name": "Nutella-Stuffed Cookies", "description": "Warm cookies filled with Nutella", "price": 199, "image_filename": "nutella-stuffed-cookies.jpg", "is_available": true },
        { "name": "Peanut Butter Brownies", "description": "Rich brownies with peanut butter swirl", "price": 169, "image_filename": "peanut-butter-brownies.jpg", "is_available": true },
        { "name": "Crepes", "description": "Thin pancakes with Nutella and strawberries", "price": 439, "image_filename": "crepese.jpg", "is_available": true }
      ]
    },
    {
      "name": "Main Courses",
      "products": [
        { "name": "Roast Chicken", "description": "Herb-roasted chicken with vegetables", "price": 799, "image_filename": "roast_chicken.jpg", "is_available": true }
      ]
    },
    {
      "name": "Beverages",
      "products": [
        { "name": "Mojito", "description": "Fresh mint, lime, rum, and soda water", "price": 199, "image_filename": "mojito.jpg", "is_available": true }
      ]
    }
  ]
};

const createFileFromImagePath = async (imagePath) => {
  try {
    const response = await fetch(`http://localhost:8000/assets/products/${imagePath}`);
    if (!response.ok) {
      throw new Error('Image not found');
    }
    const blob = await response.blob();
    return new File([blob], imagePath, { type: blob.type });
  } catch (error) {
    console.error(`Failed to load image ${imagePath}:`, error);
    return null;
  }
};

const SeedDataModal = ({ onClose }) => {
  const [loading, setLoading] = useState(false);

  const handleSeedData = async () => {
    const totalProducts = menuData.categories.reduce((sum, cat) => sum + cat.products.length, 0);
    if (!window.confirm(`Seed ${menuData.categories.length} categories and ${totalProducts} products?`)) {
      return;
    }
    
    setLoading(true);
    let seededCount = 0;
    
    try {
      for (const categoryData of menuData.categories) {
        const categoryRes = await api.post('/categories/', { name: categoryData.name });
        const categoryId = categoryRes.data.id;
        
        for (const productData of categoryData.products) {
          const formData = new FormData();
          formData.append('name', productData.name);
          formData.append('price', productData.price);
          formData.append('category_id', categoryId);
          formData.append('description', productData.description || '');
          formData.append('is_available', productData.is_available);
          formData.append('keep_original_name', 'true'); 
          
          const imageFile = await createFileFromImagePath(productData.image_filename);
          if (imageFile) {
            formData.append('image', imageFile);
          } else {
            formData.append('image_url', `assets/products/${productData.image_filename}`);
          }
          
          await api.post('/products/', formData, {
            headers: { 'Content-Type': 'multipart/form-data' }
          });
          
          seededCount++;
          console.log(`Seeded ${seededCount}/${totalProducts} products`);
        }
      }
      
      toast.success(`Successfully seeded ${menuData.categories.length} categories and ${totalProducts} products!`);
      setTimeout(() => window.location.reload(), 1500);
    } catch (error) {
      console.error('Seed error:', error);
      toast.error('Failed to seed menu. Check console for details.');
      setLoading(false);
    }
  };

  const totalProducts = menuData.categories.reduce((sum, cat) => sum + cat.products.length, 0);

  return (
    <div className="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4">
      <div className="bg-white rounded-xl w-full max-w-sm p-5">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-lg font-bold">Seed Menu Data</h2>
          <button onClick={onClose} className="text-gray-400 hover:text-gray-600">
            <MdClose size={20} />
          </button>
        </div>
        <p className="text-sm text-gray-600 mb-4">
          This will add {menuData.categories.length} categories and {totalProducts} products to your menu.
          <br />
          <span className="text-xs text-gray-500 mt-1 block">
            Images will be copied from your assets folder
          </span>
        </p>
        <div className="flex gap-3">
          <button
            onClick={handleSeedData}
            disabled={loading}
            className="flex-1 py-2 bg-green-600 text-white rounded-lg text-sm font-medium hover:bg-green-700 disabled:opacity-50"
          >
            {loading ? `Seeding... (${Math.round(loading)}%)` : 'Seed Data'}
          </button>
          <button
            onClick={onClose}
            className="flex-1 py-2 bg-gray-200 text-gray-700 rounded-lg text-sm font-medium hover:bg-gray-300"
          >
            Cancel
          </button>
        </div>
      </div>
    </div>
  );
};

export default SeedDataModal;