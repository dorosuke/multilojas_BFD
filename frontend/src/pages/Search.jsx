import { useEffect, useMemo, useState } from 'react'
import { Link, useSearchParams } from 'react-router-dom'

import { getSearchFilters, searchProducts } from '../services/stores'

function toIntList(value) {
  if (!value) return []
  return String(value)
    .split(',')
    .map((x) => Number(x.trim()))
    .filter((n) => Number.isInteger(n) && n > 0)
}

function clampPage(value) {
  const n = Number(value || 1)
  if (!Number.isFinite(n) || n < 1) return 1
  return Math.floor(n)
}

export default function Search() {
  const [searchParams, setSearchParams] = useSearchParams()
  const q = searchParams.get('q') || ''
  const sort = searchParams.get('sort') || 'relevance'
  const page = useMemo(() => clampPage(searchParams.get('page')), [searchParams])
  const selectedCategories = useMemo(() => toIntList(searchParams.get('categories')), [searchParams])
  const selectedStores = useMemo(() => toIntList(searchParams.get('stores')), [searchParams])
  const minPrice = searchParams.get('min_price') || ''
  const maxPrice = searchParams.get('max_price') || ''

  const [filtersPayload, setFiltersPayload] = useState(null)
  const [resultsPayload, setResultsPayload] = useState(null)
  const [error, setError] = useState(null)

  useEffect(() => {
    let alive = true
    getSearchFilters({ q })
      .then((data) => {
        if (alive) setFiltersPayload(data)
      })
      .catch((err) => {
        if (alive) setError(err)
      })
    return () => {
      alive = false
    }
  }, [q])

  useEffect(() => {
    let alive = true
    searchProducts({
      q,
      categories: selectedCategories,
      stores: selectedStores,
      minPrice: minPrice ? Number(minPrice) : undefined,
      maxPrice: maxPrice ? Number(maxPrice) : undefined,
      sort,
      page,
      pageSize: 24
    })
      .then((data) => {
        if (alive) setResultsPayload(data)
      })
      .catch((err) => {
        if (alive) setError(err)
      })
    return () => {
      alive = false
    }
  }, [q, selectedCategories, selectedStores, minPrice, maxPrice, sort, page])

  const categories = filtersPayload?.data?.categories || []
  const stores = filtersPayload?.data?.stores || []
  const results = resultsPayload?.data?.results || []
  const pagination = resultsPayload?.data?.pagination

  function updateParam(name, value) {
    const next = new URLSearchParams(searchParams)
    if (value === null || value === undefined || value === '') next.delete(name)
    else next.set(name, value)
    if (name !== 'page') next.delete('page')
    setSearchParams(next)
  }

  function toggleListParam(name, id) {
    const current = new Set(toIntList(searchParams.get(name)))
    if (current.has(id)) current.delete(id)
    else current.add(id)
    updateParam(name, Array.from(current).join(','))
  }

  const canPrev = page > 1
  const canNext = pagination ? page * pagination.page_size < pagination.total : false

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-xl font-semibold tracking-tight">Busca</h1>
        <Link to="/" className="text-sm text-slate-600 hover:text-slate-900">
          Voltar
        </Link>
      </div>

      <section className="rounded-2xl border bg-white p-5 shadow-sm">
        <label className="text-sm font-medium text-slate-700">Buscar (produto, loja, categoria)</label>
        <input
          value={q}
          onChange={(e) => updateParam('q', e.target.value)}
          placeholder="Ex: vestido, moda, decoração…"
          className="mt-1 w-full rounded-lg border px-3 py-2 text-sm outline-none ring-slate-200 focus:ring"
        />

        <div className="mt-3 flex flex-wrap gap-2">
          <select
            value={sort}
            onChange={(e) => updateParam('sort', e.target.value)}
            className="rounded-lg border bg-white px-3 py-2 text-sm"
          >
            <option value="relevance">Relevância</option>
            <option value="price_asc">Menor preço</option>
            <option value="price_desc">Maior preço</option>
          </select>

          <input
            value={minPrice}
            onChange={(e) => updateParam('min_price', e.target.value)}
            placeholder="Preço mín."
            className="w-32 rounded-lg border px-3 py-2 text-sm"
            inputMode="decimal"
          />
          <input
            value={maxPrice}
            onChange={(e) => updateParam('max_price', e.target.value)}
            placeholder="Preço máx."
            className="w-32 rounded-lg border px-3 py-2 text-sm"
            inputMode="decimal"
          />
        </div>
      </section>

      {error ? (
        <div className="rounded-lg border border-rose-200 bg-rose-50 p-4 text-sm text-rose-900">
          Não foi possível carregar a busca.
        </div>
      ) : null}

      <div className="grid grid-cols-1 gap-4 lg:grid-cols-4">
        <aside className="space-y-4 lg:col-span-1">
          <div className="rounded-2xl border bg-white p-4 shadow-sm">
            <div className="text-sm font-semibold">Categorias</div>
            <div className="mt-3 space-y-2">
              {categories.length ? (
                categories.slice(0, 20).map((c) => (
                  <label key={c.id} className="flex items-center gap-2 text-sm text-slate-700">
                    <input
                      type="checkbox"
                      checked={selectedCategories.includes(c.id)}
                      onChange={() => toggleListParam('categories', c.id)}
                    />
                    <span className="truncate">{c.nome}</span>
                    <span className="ml-auto text-xs text-slate-500">{c.total}</span>
                  </label>
                ))
              ) : (
                <div className="text-sm text-slate-500">Sem categorias.</div>
              )}
            </div>
          </div>

          <div className="rounded-2xl border bg-white p-4 shadow-sm">
            <div className="text-sm font-semibold">Lojas</div>
            <div className="mt-3 space-y-2">
              {stores.length ? (
                stores.slice(0, 20).map((s) => (
                  <label key={s.id} className="flex items-center gap-2 text-sm text-slate-700">
                    <input
                      type="checkbox"
                      checked={selectedStores.includes(s.id)}
                      onChange={() => toggleListParam('stores', s.id)}
                    />
                    <span className="truncate">{s.nome_loja}</span>
                    <span className="ml-auto text-xs text-slate-500">{s.total}</span>
                  </label>
                ))
              ) : (
                <div className="text-sm text-slate-500">Sem lojas.</div>
              )}
            </div>
          </div>
        </aside>

        <section className="space-y-3 lg:col-span-3">
          <div className="flex items-end justify-between">
            <h2 className="text-base font-semibold">Resultados</h2>
            {pagination ? (
              <div className="text-xs text-slate-600">{pagination.total} encontrados</div>
            ) : null}
          </div>

          {!resultsPayload && !error ? (
            <div className="rounded-lg border bg-white p-4 text-sm text-slate-600">Carregando…</div>
          ) : null}

          <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-3">
            {results.map((p) => (
              <Link key={p.id} to={`/produto/${p.id}`} className="rounded-xl border bg-white p-4 shadow-sm hover:shadow">
                <div className="aspect-[4/3] overflow-hidden rounded-lg bg-slate-100">
                  {p.imagem_url ? (
                    <img src={p.imagem_url} alt={p.nome} className="h-full w-full object-cover" loading="lazy" />
                  ) : (
                    <div className="flex h-full w-full items-center justify-center text-xs text-slate-500">
                      Sem foto
                    </div>
                  )}
                </div>
                <div className="mt-3">
                  <div className="truncate text-sm font-medium">{p.nome}</div>
                  <div className="mt-1 text-xs text-slate-600">{p.loja?.nome_loja}</div>
                  <div className="mt-2 flex items-center justify-between">
                    <div className="text-sm font-semibold">R$ {Number(p.preco).toFixed(2)}</div>
                    <div className="text-xs text-slate-600" title={`Estoque: ${p.estoque}`}>
                      {p.status_estoque === 'baixo' ? 'Baixo' : 'OK'}
                    </div>
                  </div>
                </div>
              </Link>
            ))}
          </div>

          {pagination ? (
            <div className="flex items-center justify-between pt-2">
              <button
                disabled={!canPrev}
                onClick={() => updateParam('page', String(page - 1))}
                className="rounded-lg border bg-white px-3 py-2 text-sm disabled:opacity-50"
              >
                Anterior
              </button>
              <div className="text-sm text-slate-600">Página {page}</div>
              <button
                disabled={!canNext}
                onClick={() => updateParam('page', String(page + 1))}
                className="rounded-lg border bg-white px-3 py-2 text-sm disabled:opacity-50"
              >
                Próxima
              </button>
            </div>
          ) : null}
        </section>
      </div>
    </div>
  )
}
