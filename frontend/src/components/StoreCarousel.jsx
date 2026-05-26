import { Link } from 'react-router-dom'
import { useMemo, useRef } from 'react'

function initials(name) {
  const parts = String(name || '').trim().split(/\s+/).filter(Boolean)
  const first = parts[0]?.[0] || 'L'
  const second = parts[1]?.[0] || parts[0]?.[1] || ''
  return (first + second).toUpperCase()
}

export default function StoreCarousel({ stores }) {
  if (!stores?.length) return null

  const containerRef = useRef(null)
  const scrollByAmount = useMemo(() => 360, [])
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
        {stores.map((store) => (
          <Link
            key={store.id}
            to={`/loja/${store.id}`}
            className="w-64 shrink-0 rounded-xl border bg-white p-4 shadow-sm hover:shadow"
          >
            <div className="flex items-center gap-3">
              <div className="flex h-12 w-12 items-center justify-center overflow-hidden rounded-lg bg-slate-100 text-xs font-semibold text-slate-700">
                {store.logo_url ? (
                  <img
                    src={store.logo_url}
                    alt={store.nome_loja}
                    className="h-full w-full object-cover"
                    loading="lazy"
                  />
                ) : (
                  <span>{initials(store.nome_loja)}</span>
                )}
              </div>
              <div className="min-w-0">
                <div className="truncate font-medium">{store.nome_loja}</div>
                <div className="text-xs text-slate-600">
                  {store.total_produtos_ativos} produtos
                </div>
              </div>
            </div>
            {store.descricao_resumida ? (
              <p className="mt-3 max-h-10 overflow-hidden text-sm text-slate-600">
                {store.descricao_resumida}
              </p>
            ) : null}
          </Link>
        ))}
        </div>
      </div>
    </div>
  )
}
