import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import '../styles/theme.css';

export default function Register() {
  const { login } = useAuth();
  const navigate = useNavigate();
  const [tab, setTab] = useState('vendedor');
  const [form, setForm] = useState({
    nome: '', email: '', senha: '', telefone: '',
    nome_loja: '', descricao_loja: '', logo_url: '', endereco_completo_vendedor: '', cnpj: '', chave_pix: '',
    cpf: '', endereco_completo_comprador: ''
  });
  const [error, setError] = useState('');

  const handleChange = e => setForm(f => ({ ...f, [e.target.name]: e.target.value }));

  const handleSubmit = async e => {
    e.preventDefault();
    setError('');
    const isVendor = tab === 'vendedor';
    const endpoint = isVendor ? 'http://localhost:8000/api/auth/register/vendor/' : 'http://localhost:8000/api/auth/register/buyer/';
    const payload = isVendor ? {
      nome: form.nome, email: form.email, senha: form.senha, telefone: form.telefone,
      nome_loja: form.nome_loja, descricao_loja: form.descricao_loja, logo_url: form.logo_url,
      endereco_completo: form.endereco_completo_vendedor, cnpj: form.cnpj, chave_pix: form.chave_pix
    } : {
      nome: form.nome, email: form.email, senha: form.senha, telefone: form.telefone,
      cpf: form.cpf, endereco_completo: form.endereco_completo_comprador
    };
    try {
      const res = await fetch(endpoint, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });
      const data = await res.json();
      if (!res.ok || data.success === false) throw new Error(data.message || 'Erro ao cadastrar');
      login(data.data.user, data.data.access);
      navigate('/profile');
    } catch (err) {
      setError(err.message);
    }
  };

  return (
    <div className="card" style={{ maxWidth: 500, margin: '40px auto' }}>
      <h2 style={{ color: 'var(--primary)' }}>Criar Conta</h2>
      <div className="tabs">
        <button className={`tab${tab === 'vendedor' ? ' active' : ''}`} onClick={() => setTab('vendedor')}>Sou vendedor</button>
        <button className={`tab${tab === 'comprador' ? ' active' : ''}`} onClick={() => setTab('comprador')}>Sou comprador</button>
      </div>
      <form onSubmit={handleSubmit}>
        <label>Nome completo
          <input name="nome" value={form.nome} onChange={handleChange} required />
        </label>
        <label>Telefone
          <input name="telefone" value={form.telefone} onChange={handleChange} required />
        </label>
        <label>Email
          <input name="email" type="email" value={form.email} onChange={handleChange} required />
        </label>
        <label>Senha
          <input name="senha" type="password" value={form.senha} onChange={handleChange} required minLength={8} />
        </label>
        {tab === 'vendedor' && <>
          <label>Nome da loja
            <input name="nome_loja" value={form.nome_loja} onChange={handleChange} required />
          </label>
          <label>Chave PIX
            <input name="chave_pix" value={form.chave_pix} onChange={handleChange} required />
          </label>
          <label>Logo da loja
            <input name="logo_url" value={form.logo_url} onChange={handleChange} />
          </label>
          <label>CNPJ ou CPF
            <input name="cnpj" value={form.cnpj} onChange={handleChange} />
          </label>
          <label>Endereço completo da loja
            <textarea name="endereco_completo_vendedor" value={form.endereco_completo_vendedor} onChange={handleChange} required />
          </label>
          <label>Descrição da loja
            <textarea name="descricao_loja" value={form.descricao_loja} onChange={handleChange} />
          </label>
        </>}
        {tab === 'comprador' && <>
          <label>CPF
            <input name="cpf" value={form.cpf} onChange={handleChange} required />
          </label>
          <label>Endereço completo para entrega
            <textarea name="endereco_completo_comprador" value={form.endereco_completo_comprador} onChange={handleChange} required />
          </label>
        </>}
        {error && <div className="form-feedback">{error}</div>}
        <button className="btn-primary" type="submit">Criar conta</button>
      </form>
      <div style={{ marginTop: 16 }}>
        <a href="/login" style={{ color: 'var(--secondary)' }}>Já tenho conta</a>
      </div>
    </div>
  );
}
