import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import '../styles/theme.css';

export default function Profile() {
  const { token, user, logout } = useAuth();
  const [profile, setProfile] = useState(null);
  const [msg, setMsg] = useState('');
  const [error, setError] = useState('');
  const [edit, setEdit] = useState(false);
  const [form, setForm] = useState({});

  useEffect(() => {
    fetch('http://localhost:8000/api/auth/profile/', {
      headers: { Authorization: `Bearer ${token}` }
    })
      .then(r => r.json())
      .then(data => setProfile(data.data))
      .catch(() => setError('Erro ao carregar perfil.'));
  }, [token]);

  const handleChange = e => setForm(f => ({ ...f, [e.target.name]: e.target.value }));

  const handleEdit = () => {
    setForm(profile);
    setEdit(true);
    setMsg(''); setError('');
  };

  const handleSave = async e => {
    e.preventDefault();
    setMsg(''); setError('');
    try {
      const res = await fetch('http://localhost:8000/api/auth/profile/', {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`
        },
        body: JSON.stringify(form)
      });
      const data = await res.json();
      if (!res.ok || data.success === false) throw new Error(data.message || 'Erro ao atualizar perfil');
      setProfile(data.data);
      setEdit(false);
      setMsg('Perfil atualizado com sucesso!');
    } catch (err) {
      setError(err.message);
    }
  };

  if (!profile) return <div className="card" style={{ maxWidth: 400, margin: '40px auto' }}>Carregando...</div>;

  return (
    <div className="card" style={{ maxWidth: 500, margin: '40px auto' }}>
      <h2 style={{ color: 'var(--primary)' }}>Meu Perfil</h2>
      {msg && <div className="form-feedback">{msg}</div>}
      {error && <div className="form-feedback">{error}</div>}
      {edit ? (
        <form onSubmit={handleSave}>
          <label>Nome
            <input name="nome" value={form.nome || ''} onChange={handleChange} required />
          </label>
          <label>Telefone
            <input name="telefone" value={form.telefone || ''} onChange={handleChange} required />
          </label>
          <button className="btn-primary" type="submit">Salvar</button>
          <button className="btn-secondary" type="button" onClick={() => setEdit(false)} style={{ marginLeft: 8 }}>Cancelar</button>
        </form>
      ) : (
        <>
          <div><b>Nome:</b> {profile.nome}</div>
          <div><b>Email:</b> {profile.email}</div>
          <div><b>Telefone:</b> {profile.telefone}</div>
          <button className="btn-primary" onClick={handleEdit} style={{ marginTop: 16 }}>Editar</button>
        </>
      )}
      <button className="btn-secondary" onClick={logout} style={{ marginTop: 24 }}>Sair</button>
    </div>
  );
}
