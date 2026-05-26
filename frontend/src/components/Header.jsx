import { Link, NavLink } from 'react-router-dom'

export default function Header() {
  return (
    <header className="border-b bg-white">
      <div className="mx-auto flex max-w-6xl items-center justify-between px-4 py-4">
        <Link to="/" className="text-lg font-semibold tracking-tight">
          MultiLojas
        </Link>
        <nav className="flex items-center gap-4 text-sm">
          <NavLink
            to="/"
            className={({ isActive }) =>
              isActive ? 'font-medium text-slate-900' : 'text-slate-600 hover:text-slate-900'
            }
          >
            Início
          </NavLink>
          <NavLink
            to="/busca"
            className={({ isActive }) =>
              isActive ? 'font-medium text-slate-900' : 'text-slate-600 hover:text-slate-900'
            }
          >
            Busca
          </NavLink>
        </nav>
      </div>
    </header>
  )
}
