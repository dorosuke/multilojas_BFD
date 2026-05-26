import { useEffect, useState } from 'react'

import SidebarNav from './SidebarNav.jsx'

export default function SidebarLayout({ children }) {
  const [open, setOpen] = useState(false)

  useEffect(() => {
    const onKeyDown = (e) => {
      if (e.key === 'Escape') setOpen(false)
    }
    window.addEventListener('keydown', onKeyDown)
    return () => window.removeEventListener('keydown', onKeyDown)
  }, [])

  return (
    <div className="min-h-screen bg-slate-50">
      <div className="mx-auto flex max-w-6xl gap-4 px-4 py-4">
        <button
          type="button"
          className="inline-flex items-center gap-2 rounded-lg border bg-white px-3 py-2 text-sm shadow-sm lg:hidden"
          onClick={() => setOpen(true)}
          aria-label="Abrir menu"
        >
          ☰ <span className="text-slate-700">Menu</span>
        </button>
      </div>

      {open ? (
        <div
          className="fixed inset-0 z-40 bg-black/30 lg:hidden"
          role="button"
          tabIndex={-1}
          aria-label="Fechar menu"
          onClick={() => setOpen(false)}
          onKeyDown={() => {}}
        />
      ) : null}

      <div className="mx-auto flex max-w-6xl gap-6 px-4 pb-10">
        <aside className="hidden w-64 shrink-0 lg:block">
          <SidebarNav />
        </aside>

        <aside
          className={
            'fixed left-0 top-0 z-50 h-full w-72 overflow-y-auto border-r bg-white p-4 shadow-lg transition-transform lg:hidden ' +
            (open ? 'translate-x-0' : '-translate-x-full')
          }
          aria-hidden={!open}
        >
          <div className="flex items-center justify-between">
            <div className="text-base font-semibold">MultiLojas</div>
            <button
              type="button"
              className="rounded-lg border bg-white px-3 py-2 text-sm"
              onClick={() => setOpen(false)}
              aria-label="Fechar menu"
            >
              ✕
            </button>
          </div>
          <div className="mt-4" onClick={() => setOpen(false)}>
            <SidebarNav />
          </div>
        </aside>

        <main className="min-w-0 flex-1">
          <div className="rounded-2xl bg-transparent">{children}</div>
        </main>
      </div>
    </div>
  )
}

