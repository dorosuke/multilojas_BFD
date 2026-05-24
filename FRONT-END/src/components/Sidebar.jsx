import React from 'react';
import { Link } from 'react-router-dom';

export default function Sidebar({ open, onClose }) {
  return (
    <>
      <div className={`sidebar-overlay ${open ? 'open' : ''}`} onClick={onClose} />
      <aside className={`sidebar ${open ? 'open' : ''}`} aria-hidden={!open}>
        <button type="button" className="sidebar-close" onClick={onClose} aria-label="Fechar menu">×</button>
        <nav className="sidebar-nav">
          <ul>
            <li><Link to="/register" onClick={onClose}>Criar conta</Link></li>
            <li><Link to="/login" onClick={onClose}>Entrar / Logar</Link></li>
            <li><Link to="/forgot-password" onClick={onClose}>Recuperar senha</Link></li>
          </ul>
        </nav>
      </aside>
    </>
  );
}
