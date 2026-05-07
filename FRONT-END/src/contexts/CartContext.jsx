import React, { createContext, useContext, useState, useEffect } from 'react';
import { getItem, setItem, removeItem } from '../services/storage';

const CartContext = createContext();

export function CartProvider({ children }) {
  const [cart, setCart] = useState(() => getItem('cart') || { storeId: null, items: [] });

  useEffect(() => {
    setItem('cart', cart);
  }, [cart]);

  function addItem(storeId, product, qty = 1, variation = null) {
    if (cart.storeId && cart.storeId !== storeId) {
      return { error: 'Carrinho só pode conter produtos de uma loja por vez.' };
    }
    const existing = cart.items.find(i => i.product.id === product.id && i.variation === variation);
    let items;
    if (existing) {
      items = cart.items.map(i => i === existing ? { ...i, qty: i.qty + qty } : i);
    } else {
      items = [...cart.items, { product, qty, variation }];
    }
    setCart({ storeId, items });
    return { success: true };
  }

  function removeItem(productId, variation = null) {
    const items = cart.items.filter(i => !(i.product.id === productId && i.variation === variation));
    const storeId = items.length ? cart.storeId : null;
    setCart({ storeId, items });
  }

  function updateQty(productId, qty, variation = null) {
    const items = cart.items.map(i => (i.product.id === productId && i.variation === variation) ? { ...i, qty } : i);
    setCart({ ...cart, items });
  }

  function clearCart() {
    setCart({ storeId: null, items: [] });
    removeItem('cart');
  }

  const totalItems = cart.items.reduce((s, i) => s + i.qty, 0);

  return (
    <CartContext.Provider value={{ cart, addItem, removeItem, updateQty, clearCart, totalItems }}>
      {children}
    </CartContext.Provider>
  );
}

export function useCart() {
  return useContext(CartContext);
}
