import React, { createContext, useContext, useEffect, useState } from 'react';
import * as api from '../services/api';

const StoreContext = createContext();

export function StoreProvider({ children }) {
  const [stores, setStores] = useState([]);
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    async function load() {
      setLoading(true);
      try {
        const s = await api.fetchStores();
        setStores(s || []);
      } catch (e) {
        setStores([]);
      }
      setLoading(false);
    }
    load();
  }, []);

  async function loadProductsForStore(storeId) {
    const p = await api.fetchProducts(storeId);
    setProducts(p || []);
    return p;
  }

  function getStoreById(id) {
    return stores.find(s => String(s.id) === String(id));
  }

  function getProductById(id) {
    return products.find(p => String(p.id) === String(id));
  }

  return (
    <StoreContext.Provider value={{ stores, products, loading, loadProductsForStore, getStoreById, getProductById }}>
      {children}
    </StoreContext.Provider>
  );
}

export function useStore() {
  return useContext(StoreContext);
}
