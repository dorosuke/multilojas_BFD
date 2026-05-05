import React, { useState } from 'react';
import '../styles/theme.css';

export default function ForgotPassword() {
  const [email, setEmail] = useState('');
  const [msg, setMsg] = useState('');
  const [error, setError] = useState('');

  const handleSubmit = async e => {
    e.preventDefault();
    setMsg(''); setError('');
    try {
      const res = await fetch('http://localhost:8000/api/auth/password-reset/request/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email })
      });
      const data = await res.json();
      if (!res.ok || data.success === false) throw new Error(data.message || 'Erro ao solicitar recuperação');
      setMsg('Se o e-mail existir, um link de recuperação foi enviado.');
    } catch (err) {
      setError(err.message);
    }
  };

  return (
    <div className="card" style={{ maxWidth: 400, margin: '40px auto' }}>
      <h2 style={{ color: 'var(--primary)' }}>Recuperar Senha</h2>
      <form onSubmit={handleSubmit}>
        <label>Email
          <input type="email" value={email} onChange={e => setEmail(e.target.value)} required />
        </label>
        {msg && <div className="form-feedback">{msg}</div>}
        {error && <div className="form-feedback">{error}</div>}
        <button className="btn-primary" type="submit">Enviar</button>
      </form>
      <div style={{ marginTop: 16 }}>
        <a href="/login" style={{ color: 'var(--secondary)' }}>Voltar ao login</a>
      </div>
    </div>
  );
}
