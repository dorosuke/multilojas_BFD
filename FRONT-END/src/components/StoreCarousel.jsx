import React, { useEffect, useState } from 'react';
import '../styles/theme.css';

export default function StoreCarousel() {
  const [stores, setStores] = useState([]);

  useEffect(() => {
    fetch('http://127.0.0.1:8000/api/lojas/')
      .then(r => r.json())
      .then(data => setStores(data.data || []))
      .catch(() => setStores([]));
  }, []);

  if (!stores || stores.length === 0) return null;

  return (
    <div style={{ overflowX: 'auto', whiteSpace: 'nowrap', padding: 8 }}>
      {stores.map(s => (
        <a key={s.id} href={`/loja/${s.slug || s.id}`} style={{ display: 'inline-block', width: 200, marginRight: 12, textDecoration: 'none', color: 'inherit' }}>
          <div className="card" style={{ padding: 12, height: 140 }}>
            <div style={{ display: 'flex', alignItems: 'center' }}>
              <img src={s.logo_url || '/'} alt={s.nome_loja} style={{ width: 64, height: 64, objectFit: 'cover', marginRight: 12 }} />
              <div>
                <div style={{ fontWeight: 'bold' }}>{s.nome_loja}</div>
                <div style={{ color: 'var(--secondary)', fontSize: 13 }}>{s.descricao_loja}</div>
              </div>
            </div>
          </div>
        </a>
      ))}
    </div>
  );
}
