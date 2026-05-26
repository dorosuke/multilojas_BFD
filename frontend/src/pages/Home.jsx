import { useEffect, useMemo, useState } from 'react'

import ProductCarousel from '../components/ProductCarousel.jsx'
import StoreCarousel from '../components/StoreCarousel.jsx'
import { getShowcase, listStores } from '../services/stores'

export default function Home() {
  const [query, setQuery] = useState('')
  const [payload, setPayload] = useState(null)
  const [showcasePayload, setShowcasePayload] = useState(null)
  const [error, setError] = useState(null)

  useEffect(() => {
    let alive = true
    listStores()
      .then((data) => {
        if (alive) setPayload(data)
      })
      .catch((err) => {
        if (alive) setError(err)
      })
    return () => {
      alive = false
    }
  }, [])

  useEffect(() => {
    let alive = true
    getShowcase({ perStore: 8 })
      .then((data) => {
        if (alive) setShowcasePayload(data)
      })
      .catch((err) => {
        if (alive) setError(err)
      })
    return () => {
      alive = false
    }
  }, [])

  const stores = payload?.data || []
  const filtered = useMemo(() => {
    const q = query.trim().toLowerCase()
    if (!q) return stores
    return stores.filter((s) => (s.nome_loja || '').toLowerCase().includes(q))
  }, [query, stores])

  return (
    <div className="space-y-6">
      <section className="rounded-2xl border bg-white p-5 shadow-sm">
        <h1 className="text-xl font-semibold tracking-tight">Vitrine de lojas</h1>
        <p className="mt-1 text-sm text-slate-600">
          Busque uma loja e navegue pelos produtos disponíveis.
        </p>

        <div className="mt-4">
          <label className="text-sm font-medium text-slate-700">Buscar loja</label>
          <input
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Ex: Moda Solar"
            className="mt-1 w-full rounded-lg border px-3 py-2 text-sm outline-none ring-slate-200 focus:ring"
          />
        </div>
      </section>

      <section className="space-y-3">
        <div className="flex items-end justify-between">
          <h2 className="text-base font-semibold">Lojas</h2>
          <div className="text-xs text-slate-600">{filtered.length} encontradas</div>
        </div>

        {error ? (
          <div className="rounded-lg border border-rose-200 bg-rose-50 p-4 text-sm text-rose-900">
            Não foi possível carregar as lojas.
          </div>
        ) : null}

        {!payload && !error ? (
          <div className="rounded-lg border bg-white p-4 text-sm text-slate-600">Carregando…</div>
        ) : null}

        <StoreCarousel stores={filtered} />
      </section>

      <section className="space-y-3">
        <div className="flex items-end justify-between">
          <h2 className="text-base font-semibold">Produtos por loja</h2>
          <div className="text-xs text-slate-600">Carrossel por loja</div>
        </div>

        {!showcasePayload && !error ? (
          <div className="rounded-lg border bg-white p-4 text-sm text-slate-600">Carregando…</div>
        ) : null}

        {(showcasePayload?.data || []).map((block) => (
          <div key={block.loja.id} className="rounded-2xl border bg-white p-4 shadow-sm">
            <div className="flex items-center justify-between gap-3">
              <div className="flex min-w-0 items-center gap-3">
                <div className="flex h-10 w-10 items-center justify-center overflow-hidden rounded-lg bg-slate-100 text-xs font-semibold text-slate-700">
                  {block.loja.logo_url ? (
                    <img
                      src={block.loja.logo_url}
                      alt={block.loja.nome_loja}
                      className="h-full w-full object-cover"
                      loading="lazy"
                    />
                  ) : (
                    <span>Logo</span>
                  )}
                </div>
                <div className="min-w-0">
                  <div className="truncate text-sm font-semibold">{block.loja.nome_loja}</div>
                {block.loja.descricao_resumida ? (
                  <div className="mt-1 text-xs text-slate-600">{block.loja.descricao_resumida}</div>
                ) : null}
              </div>
            </div>
            <div className="mt-3">
              <ProductCarousel products={block.produtos} storeId={block.loja.id} />
            </div>
          </div>
        ))}
      </section>
    </div>
  )
}
