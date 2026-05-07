import React from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';

export default function Header() {
  const { user } = useAuth();
  return (
    <header className="toolbar-header">
      <div className="toolbar-content">
        <div className="toolbar-left">Seja bem-vindo</div>
        <div className="toolbar-right">
          {user ? (
            <Link to="/profile" className="toolbar-link">{user.name || 'Perfil'}</Link>
          ) : (
            <Link to="/login" className="toolbar-link">Entrar / Logar</Link>
          )}
        </div>
      </div>
    </header>
  );
}
