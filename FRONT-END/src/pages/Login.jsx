import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import '../styles/theme.css';

export default function Login() {
  const { login } = useAuth();
  const navigate = useNavigate();
  const [email, setEmail] = useState('');
  const [senha, setSenha] = useState('');
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    try {
      const res = await fetch('http://localhost:8000/api/auth/login/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, senha })
      });
      const data = await res.json();
      if (!res.ok || data.success === false) throw new Error(data.message || 'Erro ao logar');
      login(data.data.user, data.data.access);
      navigate('/profile');
    } catch (err) {
      setError(err.message);
    }
  };

  return (
    <div className="card" style={{ maxWidth: 400, margin: '40px auto' }}>
      <h2 style={{ color: 'var(--primary)' }}>Entrar</h2>
      <form onSubmit={handleSubmit}>
        <label>Email
          <input type="email" value={email} onChange={e => setEmail(e.target.value)} required />
        </label>
        <label>Senha
          <input type="password" value={senha} onChange={e => setSenha(e.target.value)} required />
        </label>
        {error && <div className="form-feedback">{error}</div>}
        <button className="btn-primary" type="submit">Entrar</button>
      </form>
      <div style={{ marginTop: 16 }}>
        <a href="/register" style={{ color: 'var(--secondary)' }}>Criar conta</a> | <a href="/forgot-password" style={{ color: 'var(--primary)' }}>Esqueci minha senha</a>
      </div>
    </div>
  );
}
