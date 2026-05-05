import React from 'react';
import { Link } from 'react-router-dom';
import '../styles/theme.css';
import StoreCarousel from '../components/StoreCarousel';
import stores from '../data/stores';

export default function Home() {
  return (
    <div style={{ maxWidth: 1000, margin: '24px auto' }}>
      <div className="card" style={{ textAlign: 'center' }}>
        <h1 style={{ color: 'var(--primary)' }}>Bem-vindo ao MultiLojas</h1>
        <p style={{ color: 'var(--secondary)', fontSize: 18 }}>
          Marketplace para pequenos empreendedores.<br />
          Faça login, cadastre-se ou navegue pelas funcionalidades do sistema.
        </p>
        <div style={{ marginTop: 16 }}>
          <a className="btn-primary" href="/login" style={{ marginRight: 12 }}>Entrar</a>
          <a className="btn-secondary" href="/register">Criar conta</a>
        </div>
      </div>

      <div style={{ marginTop: 20 }}>
        <h3 style={{ marginLeft: 8 }}>Lojas em destaque</h3>
        <StoreCarousel />
      </div>

      <div style={{ marginTop: 20 }}>
        <h3 style={{ marginLeft: 8 }}>Todas as lojas</h3>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: 12, marginTop: 8 }}>
          {stores.map((s) => (
            <div key={s.id} className="card">
              {s.products && s.products[0] && (
                <img src={s.products[0].images ? s.products[0].images[0] : ''} alt={s.products[0].name} style={{ width: '100%', height: 140, objectFit: 'cover', borderRadius: 6 }} />
              )}
              <h4 style={{ margin: '6px 0' }}>{s.name}</h4>
              <div style={{ color: 'var(--secondary)', fontSize: 13 }}>{s.category} — {s.location}</div>
              <p style={{ marginTop: 8, fontSize: 14 }}>{s.description}</p>
              <div style={{ marginTop: 8 }}>
                <Link className="btn-secondary" to={`/store/${s.id}`}>Ver loja</Link>
              </div>
            </div>
          ))}
        </div>
      </div>

      <div style={{ marginTop: 20 }}>
        <a className="btn-primary" href="/busca">Ir para busca</a>
      </div>
    </div>
  );
}
