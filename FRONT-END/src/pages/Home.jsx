import React from 'react';
import '../styles/theme.css';
import StoreCarousel from '../components/StoreCarousel';

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
        <a className="btn-primary" href="/busca">Ir para busca</a>
      </div>
    </div>
  );
}
