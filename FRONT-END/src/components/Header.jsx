import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import Sidebar from './Sidebar.jsx';

export default function Header() {
  const { user } = useAuth();
  const [open, setOpen] = useState(false);

  return (
    <>
      <header className="toolbar-header">
        <div className="toolbar-content">
          <div className="toolbar-left">
            <button
              type="button"
              className="hamburger"
              aria-label="Abrir menu"
              aria-expanded={open}
              onClick={() => setOpen(true)}
            >
              <span />
              <span />
              <span />
            </button>
            <span className="toolbar-welcome">Seja bem-vindo</span>
          </div>
          <div className="toolbar-right">
            {user ? (
              <Link to="/profile" className="toolbar-link">{user.name || 'Perfil'}</Link>
            ) : (
              <Link to="/login" className="toolbar-link">Entrar / Logar</Link>
            )}
          </div>
        </div>
      </header>
      <Sidebar open={open} onClose={() => setOpen(false)} />
    </>
  );
}
