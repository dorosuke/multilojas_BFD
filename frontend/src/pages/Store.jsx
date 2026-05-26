import { useEffect, useMemo, useState } from 'react'
import { Link, useParams, useSearchParams } from 'react-router-dom'

import ProductCarousel from '../components/ProductCarousel.jsx'
import { getStoreProducts } from '../services/stores'

function clampPage(value) {
  const n = Number(value || 1)
  if (!Number.isFinite(n) || n < 1) return 1
  return Math.floor(n)
}

export default function Store() {
  const { id } = useParams()
  const [searchParams, setSearchParams] = useSearchParams()
  const page = useMemo(() => clampPage(searchParams.get('page')), [searchParams])
  const category = searchParams.get('category') || ''
  const sort = searchParams.get('sort') || ''

  const [payload, setPayload] = useState(null)
  const [error, setError] = useState(null)

  useEffect(() => {
    let alive = true
    getStoreProducts(id, { page, pageSize: 12, category: category || undefined, sort: sort || undefined })
      .then((data) => {
        if (alive) setPayload(data)
      })
      .catch((err) => {
        if (alive) setError(err)
      })
    return () => {
      alive = false
    }
  }, [id, page, category, sort])

  const loja = payload?.data?.loja
  const produtos = payload?.data?.produtos || []
  const pagination = payload?.data?.pagination
  const categories = payload?.data?.categories || []

  const canPrev = page > 1
  const canNext = pagination ? page * pagination.page_size < pagination.total : false

  const hasLogo = Boolean(loja?.logo_url)

  return (
    <div className="space-y-6">
      <Link to="/" className="text-sm text-slate-600 hover:text-slate-900">
        ← Voltar
      </Link>

      {error ? (
        <div className="rounded-lg border border-rose-200 bg-rose-50 p-4 text-sm text-rose-900">
          Não foi possível carregar a loja.
        </div>
      ) : null}

      {!payload && !error ? (
        <div className="rounded-lg border bg-white p-4 text-sm text-slate-600">Carregando…</div>
      ) : null}

      {loja ? (
        <section className="rounded-2xl border bg-white p-5 shadow-sm">
          <div className="flex items-start gap-4">
            <div className="flex h-16 w-16 items-center justify-center overflow-hidden rounded-xl bg-slate-100 text-sm font-semibold text-slate-700">
              {loja.logo_url ? (
                <img
                  src={loja.logo_url}
                  alt={loja.nome_loja}
                  className="h-full w-full object-cover"
                  loading="lazy"
                />
              ) : (
                <span>Logo</span>
              )}
            </div>
            <div className="min-w-0">
              <h1 className="truncate text-xl font-semibold tracking-tight">{loja.nome_loja}</h1>
              {loja.descricao_loja ? (
                <p className="mt-1 text-sm text-slate-600">{loja.descricao_loja}</p>
              ) : null}
              {!hasLogo ? (
                <div className="mt-2 text-xs text-slate-500">
                  Dica: preencha o campo <span className="font-medium">logo_url</span> na sua loja para exibir a logo.
                </div>
              ) : null}
            </div>
          </div>
        </section>
      ) : null}

      {produtos.length ? (
        <section className="space-y-3">
          <div className="flex items-end justify-between">
            <h2 className="text-base font-semibold">Carrossel de produtos</h2>
            <div className="text-xs text-slate-600">Clique para abrir o produto</div>
          </div>
          <ProductCarousel products={produtos} />
        </section>
      ) : null}

      <section className="space-y-3">
        <div className="flex items-end justify-between">
          <h2 className="text-base font-semibold">Produtos disponíveis</h2>
          {pagination ? (
            <div className="text-xs text-slate-600">
              {pagination.total} no total
            </div>
          ) : null}
        </div>

        <div className="flex flex-wrap items-center gap-3">
          <select
            value={category}
            onChange={(e) => setSearchParams({ page: '1', category: e.target.value, sort })}
            className="rounded-lg border bg-white px-3 py-2 text-sm"
          >
            <option value="">Todas as categorias</option>
            {categories.map((c) => (
              <option key={c.id} value={String(c.id)}>
                {c.nome} ({c.total})
              </option>
            ))}
          </select>

          <select
            value={sort}
            onChange={(e) => setSearchParams({ page: '1', category, sort: e.target.value })}
            className="rounded-lg border bg-white px-3 py-2 text-sm"
          >
            <option value="">Destaques</option>
            <option value="price_asc">Menor preço</option>
            <option value="price_desc">Maior preço</option>
          </select>
        </div>

        <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-3">
          {produtos.map((p) => (
            <div key={p.id} className="rounded-xl border bg-white p-4 shadow-sm">
              <div className="flex items-start justify-between gap-3">
                <div className="min-w-0">
                  <div className="truncate font-medium">{p.nome}</div>
                  <div className="mt-1 text-sm text-slate-600">R$ {Number(p.preco).toFixed(2)}</div>
                </div>
                <div
                  className={
                    'rounded-full px-2 py-1 text-xs ' +
                    (p.status_estoque === 'baixo'
                      ? 'bg-amber-50 text-amber-800'
                      : 'bg-emerald-50 text-emerald-800')
                  }
                  title={`Estoque: ${p.estoque}`}
                >
                  {p.status_estoque === 'baixo' ? 'Estoque baixo' : 'Disponível'}
                </div>
              </div>
              {p.categoria?.nome ? (
                <div className="mt-3 text-xs text-slate-600">Categoria: {p.categoria.nome}</div>
              ) : null}
              {Array.isArray(p.variacoes) && p.variacoes.length ? (
                <div className="mt-2 text-xs text-slate-600">
                  Variações: {p.variacoes.slice(0, 2).map((v) => `${v.tipo} ${v.valor}`).join(' · ')}
                  {p.variacoes.length > 2 ? '…' : ''}
                </div>
              ) : null}
              <div className="mt-3">
                <Link className="text-sm underline" to={`/produto/${p.id}`}>
                  Abrir produto
                </Link>
              </div>
            </div>
          ))}
        </div>

        {pagination ? (
          <div className="flex items-center justify-between pt-2">
            <button
              disabled={!canPrev}
              onClick={() => setSearchParams({ page: String(page - 1), category, sort })}
              className="rounded-lg border bg-white px-3 py-2 text-sm disabled:opacity-50"
            >
              Anterior
            </button>
            <div className="text-sm text-slate-600">Página {page}</div>
            <button
              disabled={!canNext}
              onClick={() => setSearchParams({ page: String(page + 1), category, sort })}
              className="rounded-lg border bg-white px-3 py-2 text-sm disabled:opacity-50"
            >
              Próxima
            </button>
          </div>
        ) : null}
      </section>
    </div>
  )
}
