import React, { useEffect, useState } from 'react';
import { useAuth } from '../contexts/AuthContext';
import '../styles/theme.css';

export default function MyProducts() {
  const { token } = useAuth();
  const [products, setProducts] = useState([]);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(true);

  // form state
  const initialForm = { nome: '', descricao: '', preco: '', ativo: true };
  const [form, setForm] = useState(initialForm);
  const [files, setFiles] = useState([]);
  const [editingId, setEditingId] = useState(null);
  const [msg, setMsg] = useState('');

  const loadProducts = () => {
    setLoading(true);
    fetch('http://localhost:8000/api/seller/products/', {
      headers: { Authorization: `Bearer ${token}` }
    })
      .then(r => r.json())
      .then(data => setProducts(data.data || []))
      .catch(() => setError('Erro ao carregar produtos.'))
      .finally(() => setLoading(false));
  };

  useEffect(() => { if (token) loadProducts(); }, [token]);

  const handleChange = e => setForm(f => ({ ...f, [e.target.name]: e.target.type === 'checkbox' ? e.target.checked : e.target.value }));

  const handleFiles = e => {
    const selected = Array.from(e.target.files).slice(0, 5);
    setFiles(selected);
  };

  const resetForm = () => { setForm(initialForm); setFiles([]); setEditingId(null); }

  const handleSubmit = async e => {
    e.preventDefault();
    setMsg(''); setError('');
    try {
      const payload = { nome: form.nome, descricao: form.descricao, preco: form.preco, ativo: form.ativo };
      let res;
      if (editingId) {
        res = await fetch(`http://localhost:8000/api/seller/products/${editingId}/`, {
          method: 'PUT',
          headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
          body: JSON.stringify(payload)
        });
      } else {
        res = await fetch('http://localhost:8000/api/seller/products/', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
          body: JSON.stringify(payload)
        });
      }
      const data = await res.json();
      if (!res.ok || data.success === false) throw new Error(data.message || 'Erro ao salvar produto');
      const prodId = editingId || data.data.id;

      // upload photos if any
      if (files.length > 0) {
        for (const f of files) {
          const fd = new FormData();
          fd.append('photo', f);
          await fetch(`http://localhost:8000/api/seller/products/${prodId}/photos/`, {
            method: 'POST',
            headers: { Authorization: `Bearer ${token}` },
            body: fd
          });
        }
      }

      setMsg('Produto salvo com sucesso.');
      resetForm();
      loadProducts();
    } catch (err) {
      setError(err.message);
    }
  };

  const handleEdit = prod => {
    setEditingId(prod.id);
    setForm({ nome: prod.nome, descricao: prod.descricao, preco: prod.preco, ativo: !!prod.ativo });
    setMsg(''); setError('');
  };

  const handleDelete = async id => {
    if (!confirm('Confirmar exclusão do produto?')) return;
    try {
      const res = await fetch(`http://localhost:8000/api/seller/products/${id}/`, {
        method: 'DELETE',
        headers: { Authorization: `Bearer ${token}` }
      });
      if (!res.ok) throw new Error('Erro ao excluir produto');
      setMsg('Produto excluído.');
      loadProducts();
    } catch (err) {
      setError(err.message);
    }
  };

  const toggleActive = async prod => {
    try {
      const res = await fetch(`http://localhost:8000/api/seller/products/${prod.id}/`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
        body: JSON.stringify({ ...prod, ativo: !prod.ativo })
      });
      if (!res.ok) throw new Error('Erro ao atualizar status');
      loadProducts();
    } catch (err) { setError(err.message); }
  };

  if (error) return <div className="card" style={{ maxWidth: 600, margin: '40px auto' }}>{error}</div>;
  if (loading) return <div className="card" style={{ maxWidth: 600, margin: '40px auto' }}>Carregando...</div>;

  return (
    <div className="card" style={{ maxWidth: 900, margin: '40px auto' }}>
      <h2 style={{ color: 'var(--primary)' }}>Meus Produtos</h2>
      {msg && <div className="form-feedback">{msg}</div>}
      <form onSubmit={handleSubmit} style={{ marginBottom: 20 }}>
        <h3>{editingId ? 'Editar Produto' : 'Novo Produto'}</h3>
        <label>Nome
          <input name="nome" value={form.nome} onChange={handleChange} required />
        </label>
        <label>Descrição
          <textarea name="descricao" value={form.descricao} onChange={handleChange} />
        </label>
        <label>Preço
          <input name="preco" type="number" step="0.01" value={form.preco} onChange={handleChange} required />
        </label>
        <label>
          <input name="ativo" type="checkbox" checked={form.ativo} onChange={handleChange} /> Ativo
        </label>
        <label>Fotos (até 5)
          <input type="file" accept="image/*" multiple onChange={handleFiles} />
        </label>
        {files.length > 0 && <div>{files.length} arquivo(s) selecionado(s)</div>}
        {error && <div className="form-feedback">{error}</div>}
        <div style={{ marginTop: 8 }}>
          <button className="btn-primary" type="submit">{editingId ? 'Salvar' : 'Criar'}</button>
          <button className="btn-secondary" type="button" onClick={resetForm} style={{ marginLeft: 8 }}>Limpar</button>
        </div>
      </form>

      {products.length === 0 ? (
        <div>Nenhum produto cadastrado.</div>
      ) : (
        <ul style={{ padding: 0, listStyle: 'none' }}>
          {products.map(prod => (
            <li key={prod.id} style={{ borderBottom: '1px solid #eee', padding: 12, display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
              <div>
                <b>{prod.nome}</b> <span style={{ color: 'var(--secondary)' }}>R$ {prod.preco}</span>
                <div style={{ marginTop: 6 }}>{prod.descricao}</div>
                <div style={{ marginTop: 6, color: prod.ativo ? 'green' : 'red' }}>{prod.ativo ? 'Ativo' : 'Inativo'}</div>
              </div>
              <div>
                <button className="btn-primary" onClick={() => handleEdit(prod)} style={{ marginRight: 8 }}>Editar</button>
                <button className="btn-secondary" onClick={() => toggleActive(prod)} style={{ marginRight: 8 }}>{prod.ativo ? 'Desativar' : 'Ativar'}</button>
                <button className="btn-danger" onClick={() => handleDelete(prod.id)}>Excluir</button>
              </div>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
