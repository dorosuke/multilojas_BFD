import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';

export default function SearchBar() {
  const [q, setQ] = useState('');
  const navigate = useNavigate();

  function submit(e) {
    e.preventDefault();
    navigate(`/busca?q=${encodeURIComponent(q)}`);
  }

  return (
    <form onSubmit={submit} className="search-bar">
      <input value={q} onChange={e => setQ(e.target.value)} placeholder="Buscar produtos ou lojas" />
      <button type="submit">Buscar</button>
    </form>
  );
}
