# Especificação Simplificada — Front-end Multi-Lojas

## Contextos (State Management)
- **AuthContext**: autenticação JWT, persistência de sessão
- **CartContext**: carrinho restrito a uma loja, variações, localStorage
- **StoreContext**: gerenciamento de lojas e produtos
- **NotificationContext**: notificações em tempo real (toasts)

## Componentes Reutilizáveis
- **Header**: navegação, busca, carrinho
- **SearchBar**: busca unificada
- **ProductCard**: exibe produto, compartilhamento
- **ProductList**: filtros e ordenação
- **StoreCarousel**: carrossel de lojas
- **CartItem**: itens do carrinho
- **RatingComponent**: avaliações 5 estrelas
- **ShareComponent**: compartilhamento social
- **Notification**: toasts/alertas

## Páginas Principais
- **Home**: página inicial com lojas e busca
- **Login** / **Register**: autenticação
- **Store**: detalhe da loja
- **Product**: detalhe do produto (variações, avaliações)
- **Search**: resultados unificados
- **Profile**: perfil do usuário
- **MyStore** / **MyProducts**: área do vendedor
- **ForgotPassword**: recuperação de senha

## Serviços
- **api.js**: endpoints para autenticação, lojas, produtos, pedidos, PIX, Correios
- **social.js**: compartilhamento em redes sociais
- **storage.js**: helpers para localStorage

## Funcionalidades Principais
- Carrinho restrito a uma loja
- Cálculo de frete (Correios)
- Pagamento via PIX com QR Code
- Avaliações de produtos (5 estrelas)
- Compartilhamento social
- Rastreamento de pedidos
- Rotas protegidas
- Persistência de dados (sessão/carrinho)

## Design & UI
- Design responsivo (mobile/tablet/desktop)
- Sistema de cores via CSS variables
- Ícones com react-icons
- Dark mode ready
- CSS modularizado

## Integração & Dev
- Endpoints definidos em `src/services/api.js`
- `.env.example` para variáveis de ambiente
- Scripts padrão: `npm install`, `npm run dev`
- Guia de integração: `INTEGRACAO.md`, documentação: `README_COMPLETO.md`

## Observações
- Pronto para integração com backend seguindo `INTEGRACAO.md`
- Forneça base URL da API e chaves PIX/CORREIOS via `.env`
