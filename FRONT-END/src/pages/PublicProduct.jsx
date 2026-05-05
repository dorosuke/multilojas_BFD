import React, { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import '../styles/theme.css';

export default function PublicProduct() {
  const { slug } = useParams();
  const [product, setProduct] = useState(null);
  const [error, setError] = useState('');

  useEffect(() => {
    fetch(`http://127.0.0.1:8000/api/front/produto/${slug}/`)
      .then(r => r.json())
      .then(data => setProduct(data.data))
      .catch(() => setError('Erro ao carregar produto.'));
  }, [slug]);

  if (error) return <div className="card" style={{ maxWidth: 600, margin: '40px auto' }}>{error}</div>;
  if (!product) return <div className="card" style={{ maxWidth: 600, margin: '40px auto' }}>Carregando...</div>;

  return (
    <div className="card" style={{ maxWidth: 900, margin: '24px auto' }}>
      <h2 style={{ color: 'var(--primary)' }}>{product.nome}</h2>
      <div style={{ display: 'flex', gap: 16 }}>
        <div style={{ flex: 1 }}>
          <div style={{ color: 'var(--secondary)' }}>{product.descricao}</div>
          <div style={{ marginTop: 8, fontWeight: 'bold' }}>R$ {product.preco}</div>
        </div>
        <div style={{ width: 320 }}>
          {(product.fotos || []).length === 0 ? <div style={{ height: 200, background: '#f5f5f5' }}>Sem imagem</div> : (
            <img src={product.fotos[0].url} alt={product.nome} style={{ width: '100%', height: 'auto' }} />
          )}
        </div>
      </div>
    </div>
  );
}
