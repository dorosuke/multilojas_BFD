import React from 'react';
import { useParams, Link } from 'react-router-dom';
import stores from '../data/stores';

export default function Store() {
  const { id } = useParams();
  const storeId = Number(id);
  const store = stores.find((s) => s.id === storeId);

  if (!store) return (
    <div style={{ maxWidth: 800, margin: '24px auto' }}>
      <p>Loja não encontrada.</p>
      <Link to="/">Voltar</Link>
    </div>
  );

  return (
    <div style={{ maxWidth: 1000, margin: '24px auto' }}>
      <div className="card">
        <h2>{store.name}</h2>
        <div style={{ color: 'var(--secondary)' }}>{store.category} — {store.location}</div>
        <p style={{ marginTop: 8 }}>{store.description}</p>
      </div>

      <div style={{ marginTop: 16 }}>
        <h3>Produtos</h3>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: 12, marginTop: 8 }}>
          {store.products.map((p) => (
            <div key={p.id} className="card">
              {p.images && p.images[0] && <img src={p.images[0]} alt={p.name} style={{ width: '100%', height: 160, objectFit: 'cover', borderRadius: 6 }} />}
              <h4 style={{ margin: '8px 0' }}>{p.name}</h4>
              <div style={{ color: 'var(--secondary)' }}>R$ {p.price.toFixed(2)}</div>
              <div style={{ marginTop: 8 }}>
                <Link className="btn-primary" to={`/store/${store.id}/product/${p.id}`}>Ver produto</Link>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
