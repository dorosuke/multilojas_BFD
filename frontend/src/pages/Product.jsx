import { useEffect, useMemo, useState } from 'react'
import { Link, useParams } from 'react-router-dom'

import { getPublicProduct } from '../services/stores'

const CART_KEY = 'multilojas.cart.v1'

function loadCart() {
  try {
    const raw = localStorage.getItem(CART_KEY)
    if (!raw) return []
    const parsed = JSON.parse(raw)
    return Array.isArray(parsed) ? parsed : []
  } catch {
    return []
  }
}

function saveCart(items) {
  localStorage.setItem(CART_KEY, JSON.stringify(items))
}

function firstImageUrl(product) {
  const url = product?.fotos?.[0]?.imagem_url
  return url || null
}

export default function Product() {
  const { id } = useParams()
  const [payload, setPayload] = useState(null)
  const [error, setError] = useState(null)
  const [qty, setQty] = useState(1)
  const [justAdded, setJustAdded] = useState(false)

  useEffect(() => {
    let alive = true
    getPublicProduct(id)
      .then((data) => {
        if (alive) setPayload(data)
      })
      .catch((err) => {
        if (alive) setError(err)
      })
    return () => {
      alive = false
    }
  }, [id])

  const produto = payload?.data?.produto
  const loja = payload?.data?.loja
  const img = useMemo(() => firstImageUrl(produto), [produto])

  const addToCart = () => {
    if (!produto?.id || !loja?.id) return
    const cart = loadCart()
    const existing = cart.find((x) => x.product_id === produto.id)
    const safeQty = Math.max(1, Math.min(99, Number(qty) || 1))

    let next
    if (existing) {
      next = cart.map((x) =>
        x.product_id === produto.id ? { ...x, qty: Math.min(99, (Number(x.qty) || 0) + safeQty) } : x
      )
    } else {
      next = [...cart, { store_id: loja.id, product_id: produto.id, qty: safeQty }]
    }
    saveCart(next)
    setJustAdded(true)
    window.setTimeout(() => setJustAdded(false), 1200)
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <Link to="/" className="text-sm text-slate-600 hover:text-slate-900">
          ← Início
        </Link>
        {loja ? (
          <Link to={`/loja/${loja.id}`} className="text-sm text-slate-600 hover:text-slate-900">
            Ver loja
          </Link>
        ) : null}
      </div>

      {error ? (
        <div className="rounded-lg border border-rose-200 bg-rose-50 p-4 text-sm text-rose-900">
          Não foi possível carregar o produto.
        </div>
      ) : null}

      {!payload && !error ? (
        <div className="rounded-lg border bg-white p-4 text-sm text-slate-600">Carregando…</div>
      ) : null}

      {produto ? (
        <div className="grid grid-cols-1 gap-6 lg:grid-cols-5">
          <section className="lg:col-span-3">
            <div className="aspect-[4/3] overflow-hidden rounded-2xl border bg-white shadow-sm">
              {img ? (
                <img src={img} alt={produto.nome} className="h-full w-full object-cover" />
              ) : (
                <div className="flex h-full w-full items-center justify-center text-sm text-slate-500">
                  Sem foto
                </div>
              )}
            </div>
            {produto.fotos?.length > 1 ? (
              <div className="mt-3 -mx-2 flex gap-2 overflow-x-auto px-2">
                {produto.fotos.slice(0, 8).map((f) => (
                  <a
                    key={f.id}
                    href={f.imagem_url}
                    target="_blank"
                    rel="noreferrer"
                    className="h-16 w-20 shrink-0 overflow-hidden rounded-lg border bg-white"
                    title="Abrir imagem"
                  >
                    <img src={f.imagem_url} alt="Foto do produto" className="h-full w-full object-cover" />
                  </a>
                ))}
              </div>
            ) : null}
          </section>

	          <section className="lg:col-span-2">
	            <div className="rounded-2xl border bg-white p-5 shadow-sm">
	              <h1 className="text-xl font-semibold tracking-tight">{produto.nome}</h1>
	              <div className="mt-2 text-2xl font-semibold">R$ {Number(produto.preco).toFixed(2)}</div>

	              <div className="mt-4 flex items-center gap-2">
	                <input
	                  type="number"
	                  min={1}
	                  max={99}
	                  value={qty}
	                  onChange={(e) => setQty(e.target.value)}
	                  className="w-20 rounded-lg border px-3 py-2 text-sm"
	                />
	                <button
	                  type="button"
	                  onClick={addToCart}
	                  className="flex-1 rounded-lg bg-slate-900 px-4 py-2 text-sm font-medium text-white disabled:opacity-60"
	                  disabled={!loja}
	                >
	                  {justAdded ? 'Adicionado!' : 'Adicionar ao carrinho'}
	                </button>
	              </div>

	              <div className="mt-3 flex flex-wrap items-center gap-2 text-sm">
	                <span className="rounded-full bg-slate-100 px-3 py-1 text-slate-700">
	                  Estoque: {produto.estoque}
	                </span>
                {produto.categoria?.nome ? (
                  <span className="rounded-full bg-slate-100 px-3 py-1 text-slate-700">
                    Categoria: {produto.categoria.nome}
                  </span>
                ) : null}
              </div>

              {produto.descricao ? (
                <p className="mt-4 whitespace-pre-line text-sm text-slate-600">{produto.descricao}</p>
              ) : null}

              {Array.isArray(produto.variacoes) && produto.variacoes.length ? (
                <div className="mt-5">
                  <div className="text-sm font-semibold">Variações</div>
                  <div className="mt-2 flex flex-wrap gap-2">
                    {produto.variacoes.map((v) => (
                      <span
                        key={v.id}
                        className="rounded-lg border bg-white px-3 py-1 text-sm text-slate-700"
                        title={v.tipo}
                      >
                        {v.tipo}: {v.valor}
                      </span>
                    ))}
                  </div>
                </div>
              ) : null}

              {loja ? (
                <div className="mt-6 border-t pt-4 text-sm text-slate-600">
                  <div className="font-medium text-slate-900">Loja</div>
                  <div className="mt-1">{loja.nome_loja}</div>
                </div>
              ) : null}
            </div>
          </section>
        </div>
      ) : null}
    </div>
  )
}
