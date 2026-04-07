# Decisoes Tecnicas - Sprint 1

## Stack escolhida

- Backend: Django + Django REST Framework
- Banco de dados: PostgreSQL em ambiente principal
- Banco local de contingencia: SQLite
- Configuracao por ambiente: `.env`
- Politica de CORS para dev: frontend em `localhost:5173`

## Motivos das escolhas

### Django

Foi escolhido por acelerar autenticacao, painel administrativo, ORM e organizacao inicial do backend.

### Django REST Framework

Foi adotado para padronizar respostas JSON e preparar a API para as proximas sprints.

### PostgreSQL

Foi definido como banco principal por ser mais adequado para producao e crescimento do projeto.

### SQLite como fallback local

Mantem o projeto executavel mesmo quando o PostgreSQL ainda nao estiver configurado no ambiente de desenvolvimento.

### App `core`

Centraliza configuracoes e endpoints iniciais da API, servindo de base para os proximos modulos.

## Contratos e alinhamentos

Formato padrao das respostas:

```json
{
  "success": true,
  "data": {},
  "message": ""
}
```

## Convencoes adotadas

- Branch principal: `main`
- Branch de integracao: `dev`
- Padrao de commits: Conventional Commits

## Pendencias fora do codigo

- Criacao efetiva do repositorio no GitHub
- Criacao das branches remotas
- Vinculacao com frontend para teste integrado
