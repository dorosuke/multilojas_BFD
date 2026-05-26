import { useEffect, useMemo, useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'

import { createOrder } from '../services/orders.js'
import { getPublicProduct } from '../services/stores.js'

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

function groupByStore(items) {
  const groups = new Map()
  for (const it of items) {
    if (!it?.store_id) continue
    const list = groups.get(it.store_id) || []
    list.push(it)
    groups.set(it.store_id, list)
  }
  return Array.from(groups.entries()).map(([storeId, list]) => ({ storeId, items: list }))
}

export default function Cart() {
  const navigate = useNavigate()
  const [cart, setCart] = useState(() => loadCart())
  const [products, setProducts] = useState({})
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState(null)

  const groups = useMemo(() => groupByStore(cart), [cart])

  useEffect(() => {
    let alive = true
    const ids = Array.from(new Set(cart.map((x) => x.product_id).filter(Boolean)))
    if (!ids.length) return

    Promise.all(ids.map((id) => getPublicProduct(id).catch(() => null))).then((responses) => {
      if (!alive) return
      const next = {}
      for (const res of responses) {
        const p = res?.data?.produto
        if (p?.id) next[p.id] = p
      }
      setProducts(next)
    })

    return () => {
      alive = false
    }
  }, [cart])

  const updateQty = (productId, qty) => {
    const next = cart
      .map((it) => (it.product_id === productId ? { ...it, qty } : it))
      .filter((it) => (it.qty || 0) > 0)
    setCart(next)
    saveCart(next)
  }

  const removeItem = (productId) => {
    const next = cart.filter((it) => it.product_id !== productId)
    setCart(next)
    saveCart(next)
  }

  const totalItems = cart.reduce((acc, it) => acc + (Number(it.qty) || 0), 0)
  const subtotal = cart.reduce((acc, it) => {
    const p = products[it.product_id]
    const price = p ? Number(p.preco) : 0
    return acc + price * (Number(it.qty) || 0)
  }, 0)

  const [shippingAddress, setShippingAddress] = useState('')

  const checkoutStore = async (storeId) => {
    setBusy(true)
    setError(null)
    try {
      const items = cart
        .filter((it) => it.store_id === storeId)
        .map((it) => ({ product_id: it.product_id, quantity: Number(it.qty) || 0 }))
        .filter((it) => it.quantity > 0)

      const payload = await createOrder({
        store_id: storeId,
        shipping_address: shippingAddress,
        items,
      })

      const remaining = cart.filter((it) => it.store_id !== storeId)
      setCart(remaining)
      saveCart(remaining)

      navigate(`/busca?pedido=${payload?.data?.order?.id || ''}`)
    } catch (e) {
      setError(e)
    } finally {
      setBusy(false)
    }
  }

  return (
    <div className="space-y-6">
      <div className="rounded-2xl border bg-white p-5 shadow-sm">
        <h1 className="text-xl font-semibold tracking-tight">Carrinho</h1>
        <p className="mt-1 text-sm text-slate-600">Itens: {totalItems} · Subtotal aprox.: R$ {subtotal.toFixed(2)}</p>
      </div>

      {!cart.length ? (
        <div className="rounded-2xl border bg-white p-6 text-sm text-slate-600 shadow-sm">
          Carrinho vazio. <Link className="underline" to="/busca">Explorar produtos</Link>
        </div>
      ) : null}

      <div className="rounded-2xl border bg-white p-5 shadow-sm">
        <label className="text-sm font-medium text-slate-700">Endereço de entrega</label>
        <textarea
          value={shippingAddress}
          onChange={(e) => setShippingAddress(e.target.value)}
          className="mt-2 w-full rounded-lg border px-3 py-2 text-sm"
          rows={3}
          placeholder="Rua, número, bairro, cidade/UF, CEP"
        />
        <p className="mt-2 text-xs text-slate-500">
          Sprint 8: este endereço é enviado junto no pedido.
        </p>
      </div>

      {error ? (
        <div className="rounded-lg border border-rose-200 bg-rose-50 p-4 text-sm text-rose-900">
          Não foi possível finalizar o pedido.
        </div>
      ) : null}

      <div className="space-y-4">
        {groups.map((g) => (
          <section key={g.storeId} className="rounded-2xl border bg-white p-5 shadow-sm">
            <div className="flex items-center justify-between">
              <div className="text-sm font-semibold">Loja #{g.storeId}</div>
              <button
                type="button"
                className="rounded-lg border bg-slate-900 px-3 py-2 text-sm text-white disabled:opacity-60"
                disabled={busy || !shippingAddress.trim()}
                onClick={() => checkoutStore(g.storeId)}
              >
                Finalizar pedido desta loja
              </button>
            </div>

            <div className="mt-4 space-y-3">
              {g.items.map((it) => {
                const p = products[it.product_id]
                return (
                  <div key={it.product_id} className="flex items-center gap-3 rounded-xl border p-3">
                    <div className="min-w-0 flex-1">
                      <div className="truncate text-sm font-medium">
                        {p ? p.nome : `Produto #${it.product_id}`}
                      </div>
                      <div className="mt-1 text-xs text-slate-600">
                        {p ? `R$ ${Number(p.preco).toFixed(2)}` : 'Carregando preço…'}
                      </div>
                    </div>
                    <input
                      type="number"
                      min={1}
                      className="w-20 rounded-lg border px-3 py-2 text-sm"
                      value={it.qty}
                      onChange={(e) => updateQty(it.product_id, Number(e.target.value))}
                    />
                    <button
                      type="button"
                      className="rounded-lg border px-3 py-2 text-sm"
                      onClick={() => removeItem(it.product_id)}
                    >
                      Remover
                    </button>
                  </div>
                )
              })}
            </div>
          </section>
        ))}
      </div>
    </div>
  )
}

