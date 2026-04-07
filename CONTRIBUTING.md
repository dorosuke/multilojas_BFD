# Convenções do Projeto

## Sprint 1

Itens já implementados no projeto:

- configuração do backend com Django e Django REST Framework
- conexão preparada por `.env`
- suporte a PostgreSQL com fallback local em SQLite
- migrations iniciais do Django
- configuração de CORS
- criação da app `core`
- rota `GET /api/`
- rota `GET /api/health/`
- frontend simples em templates Django para demonstração
- páginas iniciais de home, busca, login, cadastro, loja, produto, painel do vendedor e área do comprador

Observações da Sprint 1:

- a parte de GitHub e branches remotas depende da criação e configuração do repositório fora do código
- as páginas do frontend foram mantidas simples, como rascunho inicial

## Sprint 2

Itens iniciados visualmente:

- tela de recuperação de senha
- tela de perfil do usuário

Observações da Sprint 2:

- a autenticação real no backend ainda não foi implementada
- os models de usuário, vendedor e comprador ainda não foram criados
- JWT e fluxo real de login ainda não foram conectados

## Branches

- `main`: produção
- `dev`: integração contínua do time

## Commits

Seguimos **Conventional Commits**:

- `feat:` nova funcionalidade
- `fix:` correção de bug
- `chore:` tarefa de manutenção
- `refactor:` refatoração sem mudança funcional
- `test:` criação ou ajuste de testes
- `docs:` documentação

Exemplo:

```text
feat: configura conexão inicial com PostgreSQL
```

## Contrato base da API

Formato padrão combinado entre os backends:

```json
{
  "success": true,
  "data": {},
  "message": ""
}
```
