import { Link } from 'react-router-dom'
import { useMemo, useRef } from 'react'

function firstImageUrl(product) {
  const direct = product?.imagem_url
  if (direct) return direct
  const url = product?.fotos?.[0]?.imagem_url
  return url || null
}

export default function ProductCarousel({ products, storeId }) {
  if (!products?.length) return null

  const containerRef = useRef(null)
  const scrollByAmount = useMemo(() => 320, [])

  const scrollLeft = () => containerRef.current?.scrollBy({ left: -scrollByAmount, behavior: 'smooth' })
  const scrollRight = () => containerRef.current?.scrollBy({ left: scrollByAmount, behavior: 'smooth' })

  return (
    <div className="relative -mx-4 px-4">
      <button
        type="button"
        onClick={scrollLeft}
        className="absolute left-2 top-1/2 z-10 -translate-y-1/2 rounded-full border bg-white/90 px-3 py-2 text-sm shadow-sm hover:bg-white"
        aria-label="Anterior"
      >
        ‹
      </button>
      <button
        type="button"
        onClick={scrollRight}
        className="absolute right-2 top-1/2 z-10 -translate-y-1/2 rounded-full border bg-white/90 px-3 py-2 text-sm shadow-sm hover:bg-white"
        aria-label="Próximo"
      >
        ›
      </button>

      <div ref={containerRef} className="overflow-x-auto">
        <div className="flex gap-3 py-2">
        {products.map((p) => {
          const img = firstImageUrl(p)
          return (
            <Link
              key={p.id}
              to={`/produto/${p.id}`}
              className="w-56 shrink-0 rounded-xl border bg-white p-3 shadow-sm hover:shadow"
            >
              <div className="aspect-[4/3] overflow-hidden rounded-lg bg-slate-100">
                {img ? (
                  <img
                    src={img}
                    alt={p.nome}
                    className="h-full w-full object-cover"
                    loading="lazy"
                  />
                ) : (
                  <div className="flex h-full w-full items-center justify-center text-xs text-slate-500">
                    Sem foto
                  </div>
                )}
              </div>
              <div className="mt-3 min-w-0">
                <div className="truncate text-sm font-medium">{p.nome}</div>
                <div className="mt-1 text-xs text-slate-600">
                  {p.categoria?.nome ? `Categoria: ${p.categoria.nome}` : 'Sem categoria'}
                </div>
              </div>

              <div className="mt-2 flex items-center justify-between gap-2">
                <div className="text-sm font-semibold text-slate-900">
                  R$ {Number(p.preco).toFixed(2)}
                </div>
                <div
                  className={
                    'rounded-full px-2 py-1 text-[11px] ' +
                    (p.status_estoque === 'baixo'
                      ? 'bg-amber-50 text-amber-800'
                      : 'bg-emerald-50 text-emerald-800')
                  }
                  title={`Estoque: ${p.estoque}`}
                >
                  {p.status_estoque === 'baixo' ? 'Baixo' : 'OK'}
                </div>
              </div>

              {Array.isArray(p.variacoes) && p.variacoes.length ? (
                <div className="mt-2 text-[11px] text-slate-600">
                  Variações: {p.variacoes.slice(0, 2).map((v) => `${v.tipo} ${v.valor}`).join(' · ')}
                  {p.variacoes.length > 2 ? '…' : ''}
                </div>
              ) : null}

              {storeId ? (
                <div className="mt-2 text-[11px] text-slate-500">Loja #{storeId}</div>
              ) : null}
            </Link>
          )
        })}
        </div>
      </div>
    </div>
  )
}
