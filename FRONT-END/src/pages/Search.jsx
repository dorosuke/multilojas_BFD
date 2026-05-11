import React, { useState } from 'react';
import '../styles/theme.css';

export default function Search() {
  const [q, setQ] = useState('');
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [filters, setFilters] = useState({ categoria: '', preco_min: '', preco_max: '', loja: '' });

  const doSearch = async e => {
    e && e.preventDefault();
    setLoading(true);
    try {
      const params = new URLSearchParams();
      if (q) params.append('q', q);
      if (filters.categoria) params.append('categoria', filters.categoria);
      if (filters.preco_min) params.append('preco_min', filters.preco_min);
      if (filters.preco_max) params.append('preco_max', filters.preco_max);
      //if (filters.loja) params.append('loja', filters.loja);
      const res = await fetch(`http://127.0.0.1:8000/api/front/busca-global/?${params.toString()}`);
      const data = await res.json();
      setResults(Array.isArray(data) ? data : data.data || []);
    } catch (err) {
      setResults([]);
    } finally { setLoading(false); }
  };

  const handleFilter = e => setFilters(f => ({ ...f, [e.target.name]: e.target.value }));

  return (
    <div className="card" style={{ maxWidth: 1000, margin: '24px auto' }}>
      <h2 style={{ color: 'var(--primary)' }}>Busca</h2>
      <form onSubmit={doSearch} style={{ display: 'flex', gap: 8, marginBottom: 12 }}>
        <input placeholder="Pesquisar por produto, loja ou categoria" value={q} onChange={e => setQ(e.target.value)} style={{ flex: 1 }} />
        <button className="btn-primary" type="submit">Buscar</button>
      </form>
      <div style={{ display: 'flex', gap: 8, marginBottom: 12 }}>
        <input name="categoria" placeholder="Categoria" value={filters.categoria} onChange={handleFilter} />
        <input name="preco_min" placeholder="Preço min" type="number" value={filters.preco_min} onChange={handleFilter} />
        <input name="preco_max" placeholder="Preço max" type="number" value={filters.preco_max} onChange={handleFilter} />
        <input name="loja" placeholder="Loja (slug)" value={filters.loja} onChange={handleFilter} />
      </div>
      {loading ? <div>Carregando...</div> : (
        <div>
          {results.length === 0 ? <div>Nenhum resultado.</div> : (
            <ul style={{ listStyle: 'none', padding: 0 }}>
              {results.map(r => (
                <li key={r.id} style={{ borderBottom: '1px solid #eee', padding: 12 }}>
                  <a href={`/produto/${r.slug || r.id}`} style={{ fontWeight: 'bold', color: 'inherit' }}>{r.nome || r.title || r.nome_loja}</a>
                  <div style={{ color: 'var(--secondary)' }}>{r.descricao || r.resumo || ''}</div>
                  <div style={{ marginTop: 6 }}>{r.preco ? `R$ ${r.preco}` : ''} <a href={`/loja/${r.loja_slug || r.slug_loja || r.loja}`} style={{ marginLeft: 8, color: 'var(--secondary)' }}>{r.nome_loja || ''}</a></div>
                </li>
              ))}
            </ul>
          )}
        </div>
      )}
    </div>
  );
}
