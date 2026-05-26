import { Route, Routes } from 'react-router-dom'

import SidebarLayout from './components/SidebarLayout.jsx'
import Home from './pages/Home.jsx'
import Cart from './pages/Cart.jsx'
import Product from './pages/Product.jsx'
import Search from './pages/Search.jsx'
import Store from './pages/Store.jsx'

export default function App() {
  return (
    <SidebarLayout>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/loja/:id" element={<Store />} />
        <Route path="/produto/:id" element={<Product />} />
        <Route path="/busca" element={<Search />} />
        <Route path="/carrinho" element={<Cart />} />
      </Routes>
    </SidebarLayout>
  )
}
