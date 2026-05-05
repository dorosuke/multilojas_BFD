import React from 'react';
import '../styles/theme.css';

export default function SellerDashboard() {
  return (
    <div className="card" style={{ maxWidth: 600, margin: '40px auto' }}>
      <h2 style={{ color: 'var(--primary)' }}>Painel do Vendedor</h2>
      <p style={{ color: 'var(--secondary)' }}>Acompanhe suas vendas, produtos e informações da loja.</p>
      <div style={{ marginTop: 32 }}>
        <a className="btn-primary" href="/my-store" style={{ marginRight: 12 }}>Minha Loja</a>
        <a className="btn-secondary" href="/my-products">Meus Produtos</a>
      </div>
    </div>
  );
}
