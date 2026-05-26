import { NavLink } from 'react-router-dom'

function linkClass({ isActive }) {
  return (
    'flex items-center justify-between rounded-lg px-3 py-2 text-sm ' +
    (isActive ? 'bg-slate-900 text-white' : 'text-slate-700 hover:bg-slate-100')
  )
}

export default function SidebarNav() {
  return (
    <nav className="space-y-1">
      <NavLink to="/" className={linkClass}>
        <span>Início</span>
      </NavLink>
      <NavLink to="/busca" className={linkClass}>
        <span>Busca</span>
      </NavLink>
      <NavLink to="/carrinho" className={linkClass}>
        <span>Carrinho</span>
      </NavLink>

      <div className="pt-3">
        <div className="px-3 text-xs font-semibold uppercase tracking-wide text-slate-500">Atalhos</div>
        <div className="mt-2 space-y-1">
          <a
            href="/api/front/login/"
            className="flex items-center justify-between rounded-lg px-3 py-2 text-sm text-slate-700 hover:bg-slate-100"
          >
            Login (templates)
          </a>
          <a
            href="/api/front/perfil/"
            className="flex items-center justify-between rounded-lg px-3 py-2 text-sm text-slate-700 hover:bg-slate-100"
          >
            Perfil (templates)
          </a>
        </div>
      </div>
    </nav>
  )
}

