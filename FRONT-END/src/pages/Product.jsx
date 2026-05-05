import React, { useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import stores from '../data/stores';

export default function Product() {
  const { storeId, productId } = useParams();
  const sId = Number(storeId);
  const store = stores.find((s) => s.id === sId);
  if (!store) return (
    <div style={{ maxWidth: 800, margin: '24px auto' }}>
      <p>Loja não encontrada.</p>
      <Link to="/">Voltar</Link>
    </div>
  );

  const product = store.products.find((p) => p.id === productId);
  if (!product) return (
    <div style={{ maxWidth: 800, margin: '24px auto' }}>
      <p>Produto não encontrado.</p>
      <Link to={`/store/${store.id}`}>Voltar à loja</Link>
    </div>
  );

  const [active, setActive] = useState(0);
  const [zoomed, setZoomed] = useState(false);

  function prev() {
    setActive((a) => (a - 1 + product.images.length) % product.images.length);
  }

  function next() {
    setActive((a) => (a + 1) % product.images.length);
  }

  return (
    <div style={{ maxWidth: 800, margin: '24px auto' }}>
      <div className="card">
        <div style={{ position: 'relative', overflow: 'hidden', borderRadius: 6 }}>
          {product.images && product.images[active] && (
            <img
              src={product.images[active]}
              alt={product.name}
              onMouseEnter={() => setZoomed(true)}
              onMouseLeave={() => setZoomed(false)}
              style={{ width: '100%', height: 300, objectFit: 'cover', transition: 'transform 200ms ease', transform: zoomed ? 'scale(1.2)' : 'scale(1)' }}
            />
          )}
          <button onClick={prev} style={{ position: 'absolute', left: 8, top: '50%', transform: 'translateY(-50%)', background: 'rgba(0,0,0,0.4)', color: '#fff', border: 'none', padding: '8px 10px', borderRadius: 4, cursor: 'pointer' }}>{'‹'}</button>
          <button onClick={next} style={{ position: 'absolute', right: 8, top: '50%', transform: 'translateY(-50%)', background: 'rgba(0,0,0,0.4)', color: '#fff', border: 'none', padding: '8px 10px', borderRadius: 4, cursor: 'pointer' }}>{'›'}</button>
        </div>
        <div style={{ display: 'flex', gap: 8, marginTop: 8 }}>
          {product.images && product.images.map((img, idx) => (
            <img
              key={img}
              src={img}
              alt={`${product.name} ${idx+1}`}
              onClick={() => setActive(idx)}
              style={{ width: 80, height: 60, objectFit: 'cover', borderRadius: 6, cursor: 'pointer', border: idx === active ? '2px solid var(--primary)' : '1px solid #ddd' }}
            />
          ))}
        </div>

        <h2 style={{ marginTop: 12 }}>{product.name}</h2>
        <div style={{ color: 'var(--secondary)' }}>R$ {product.price.toFixed(2)}</div>
        <p style={{ marginTop: 12 }}>Descrição do produto não disponível no dataset de exemplo.</p>
        <div style={{ marginTop: 12 }}>
          <Link className="btn-secondary" to={`/store/${store.id}`}>Voltar à loja</Link>
        </div>
      </div>
    </div>
  );
}
