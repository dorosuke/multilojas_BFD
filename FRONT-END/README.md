# React + Vite

This template provides a minimal setup to get React working in Vite with HMR and some ESLint rules.

Currently, two official plugins are available:

- [@vitejs/plugin-react](https://github.com/vitejs/vite-plugin-react/blob/main/packages/plugin-react) uses [Oxc](https://oxc.rs)
- [@vitejs/plugin-react-swc](https://github.com/vitejs/vite-plugin-react/blob/main/packages/plugin-react-swc) uses [SWC](https://swc.rs/)

## React Compiler

The React Compiler is not enabled on this template because of its impact on dev & build performances. To add it, see [this documentation](https://react.dev/learn/react-compiler/installation).

## Expanding the ESLint configuration

If you are developing a production application, we recommend using TypeScript with type-aware lint rules enabled. Check out the [TS template](https://github.com/vitejs/vite/tree/main/packages/create-vite/template-react-ts) for information on how to integrate TypeScript and [`typescript-eslint`](https://typescript-eslint.io) in your project.
Front-end — o que está funcionando agora

Dev server: Vite rodando em http://localhost:5173/.
Autenticação / sessão: AuthContext persiste JWT no localStorage; fluxo de login implementado em Login.jsx.
Cadastro: tela com alternância vendedor/comprador em Register.jsx (chama /api/auth/register/vendor/ e /api/auth/register/buyer/).
Recuperação de senha: formulário e chamada para /api/auth/password-reset/request/ em ForgotPassword.jsx.
Perfil protegido: consulta e atualização de perfil via /api/auth/profile/ em Profile.jsx.
Painel do vendedor: SellerDashboard.jsx com links para loja e produtos.
Minha Loja: leitura e formulário de edição (GET/PUT /api/seller/store/) em MyStore.jsx.
Meus Produtos: lista + CRUD e upload (até 5 fotos) em MyProducts.jsx (usa /api/seller/products/ e /api/seller/products/<id>/photos/).
Busca e páginas públicas: rota de busca em Search.jsx, páginas públicas de loja/produto em PublicStore.jsx e PublicProduct.jsx.
Carrossel de lojas: componente em StoreCarousel.jsx, usado na home.
Rotas: atualizadas em App.jsx.
Observação rápida: o front consome as rotas públicas/privadas do backend; se nomes de campo (ex.: slug, fotos, preco) diferirem do JSON real, faço ajuste pontual.
