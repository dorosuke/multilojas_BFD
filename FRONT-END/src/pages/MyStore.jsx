import React, { useEffect, useState } from 'react';
import { useAuth } from '../contexts/AuthContext';
import '../styles/theme.css';

export default function MyStore() {
  const { token } = useAuth();
  const [store, setStore] = useState(null);
  const [error, setError] = useState('');
  const [edit, setEdit] = useState(false);
  const [form, setForm] = useState({});
  const [msg, setMsg] = useState('');

  const loadStore = () => {
    fetch('http://localhost:8000/api/seller/store/', {
      headers: { Authorization: `Bearer ${token}` }
    })
      .then(r => r.json())
      .then(data => setStore(data.data))
      .catch(() => setError('Erro ao carregar dados da loja.'));
  };

  useEffect(() => { if (token) loadStore(); }, [token]);

  const handleChange = e => setForm(f => ({ ...f, [e.target.name]: e.target.value }));

  const handleEdit = () => {
    setForm(store || {});
    setEdit(true);
    setMsg(''); setError('');
  };

  const handleSave = async e => {
    e.preventDefault();
    setMsg(''); setError('');
    try {
      const res = await fetch('http://localhost:8000/api/seller/store/', {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
        body: JSON.stringify(form)
      });
      const data = await res.json();
      if (!res.ok || data.success === false) throw new Error(data.message || 'Erro ao atualizar loja');
      setStore(data.data);
      setEdit(false);
      setMsg('Loja atualizada com sucesso');
    } catch (err) {
      setError(err.message);
    }
  };

  if (error) return <div className="card" style={{ maxWidth: 400, margin: '40px auto' }}>{error}</div>;
  if (!store) return <div className="card" style={{ maxWidth: 400, margin: '40px auto' }}>Carregando...</div>;

  return (
    <div className="card" style={{ maxWidth: 600, margin: '40px auto' }}>
      <h2 style={{ color: 'var(--primary)' }}>Minha Loja</h2>
      {msg && <div className="form-feedback">{msg}</div>}
      {edit ? (
        <form onSubmit={handleSave}>
          <label>Nome da loja
            <input name="nome_loja" value={form.nome_loja || ''} onChange={handleChange} required />
          </label>
          <label>Descrição
            <textarea name="descricao_loja" value={form.descricao_loja || ''} onChange={handleChange} />
          </label>
          <label>Chave PIX
            <input name="chave_pix" value={form.chave_pix || ''} onChange={handleChange} />
          </label>
          <label>Endereço completo
            <textarea name="endereco_completo" value={form.endereco_completo || ''} onChange={handleChange} />
          </label>
          <label>CNPJ
            <input name="cnpj" value={form.cnpj || ''} onChange={handleChange} />
          </label>
          <label>Logo URL
            <input name="logo_url" value={form.logo_url || ''} onChange={handleChange} />
          </label>
          <div style={{ marginTop: 8 }}>
            <button className="btn-primary" type="submit">Salvar</button>
            <button className="btn-secondary" type="button" onClick={() => setEdit(false)} style={{ marginLeft: 8 }}>Cancelar</button>
          </div>
        </form>
      ) : (
        <>
          <div><b>Nome:</b> {store.nome_loja}</div>
          <div><b>Descrição:</b> {store.descricao_loja}</div>
          <div><b>Chave PIX:</b> {store.chave_pix}</div>
          <div><b>Endereço:</b> {store.endereco_completo}</div>
          <div><b>CNPJ:</b> {store.cnpj}</div>
          <div><b>Logo:</b> <img src={store.logo_url} alt="Logo" style={{ maxHeight: 60, marginTop: 8 }} /></div>
          <div style={{ marginTop: 16 }}>
            <button className="btn-primary" onClick={handleEdit}>Editar Loja</button>
          </div>
        </>
      )}
    </div>
  );
}
