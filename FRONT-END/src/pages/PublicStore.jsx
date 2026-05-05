import React, { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import '../styles/theme.css';

export default function PublicStore() {
  const { slug } = useParams();
  const [store, setStore] = useState(null);
  const [error, setError] = useState('');

  useEffect(() => {
    fetch(`http://127.0.0.1:8000/api/front/loja/${slug}/`)
      .then(r => r.json())
      .then(data => setStore(data.data))
      .catch(() => setError('Erro ao carregar loja.'));
  }, [slug]);

  if (error) return <div className="card" style={{ maxWidth: 600, margin: '40px auto' }}>{error}</div>;
  if (!store) return <div className="card" style={{ maxWidth: 600, margin: '40px auto' }}>Carregando...</div>;

  return (
    <div className="card" style={{ maxWidth: 900, margin: '24px auto' }}>
      <h2 style={{ color: 'var(--primary)' }}>{store.nome_loja}</h2>
      <div style={{ display: 'flex', gap: 16 }}>
        <div style={{ flex: 1 }}>
          <div><b>Descrição:</b> {store.descricao_loja}</div>
          <div><b>Endereço:</b> {store.endereco_completo}</div>
          <div><b>Chave PIX:</b> {store.chave_pix}</div>
        </div>
        <div style={{ width: 220 }}>
          <img src={store.logo_url} alt="Logo" style={{ width: '100%', height: 'auto' }} />
        </div>
      </div>
      <h3 style={{ marginTop: 20 }}>Produtos</h3>
      <ul style={{ listStyle: 'none', padding: 0 }}>
        {(store.produtos || []).map(p => (
          <li key={p.id} style={{ padding: 12, borderBottom: '1px solid #eee' }}>
            <a href={`/produto/${p.slug || p.id}`} style={{ fontWeight: 'bold' }}>{p.nome}</a>
            <div style={{ color: 'var(--secondary)' }}>{p.descricao}</div>
            <div style={{ marginTop: 6 }}>R$ {p.preco}</div>
          </li>
        ))}
      </ul>
    </div>
  );
}
