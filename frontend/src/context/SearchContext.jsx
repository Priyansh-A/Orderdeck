import React, { createContext, useContext, useState } from 'react';

const SearchContext = createContext(undefined);

export const SearchProvider = ({ children }) => {
  const [searchTerm, setSearchTerm] = useState('');
  const [searchResults, setSearchResults] = useState({
    products: [],
    orders: [],
    tables: []
  });

  const clearSearch = () => {
    setSearchTerm('');
    setSearchResults({ products: [], orders: [], tables: [] });
  };

  return (
    <SearchContext.Provider value={{ searchTerm, setSearchTerm, searchResults, setSearchResults, clearSearch }}>
      {children}
    </SearchContext.Provider>
  );
};

export const useSearch = () => {
  const context = useContext(SearchContext);
  if (context === undefined) {
    throw new Error('useSearch must be used within a SearchProvider');
  }
  return context;
};