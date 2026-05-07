import React from 'react';
import { Link } from 'react-router-dom';
import ShareComponent from './ShareComponent';

export default function ProductCard({ product, store }) {
  return (
    <article className="product-card">
      <Link to={`/produto/${product.slug || product.id}`}>
        <img src={product.image || '/images/stores/placeholder.png'} alt={product.name} />
        <h4>{product.name}</h4>
      </Link>
      <div className="meta">
        <div className="price">R$ {product.price?.toFixed?.(2) ?? '0.00'}</div>
        <div className="store">{store?.name}</div>
      </div>
      <ShareComponent title={product.name} url={window.location.origin + `/produto/${product.slug || product.id}`} />
    </article>
  );
}
