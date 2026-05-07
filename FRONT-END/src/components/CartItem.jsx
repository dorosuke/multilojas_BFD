import React from 'react';

export default function CartItem({ item, onRemove, onChangeQty }) {
  return (
    <div className="cart-item">
      <img src={item.product.image} alt={item.product.name} />
      <div className="info">
        <div className="name">{item.product.name}</div>
        <div className="qty">
          <button onClick={() => onChangeQty(item.product.id, item.qty - 1)}>-</button>
          <span>{item.qty}</span>
          <button onClick={() => onChangeQty(item.product.id, item.qty + 1)}>+</button>
        </div>
        <button onClick={() => onRemove(item.product.id)}>Remover</button>
      </div>
    </div>
  );
}
