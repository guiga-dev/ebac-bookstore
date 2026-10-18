# Bookstore · configuração DRF

Projeto novo em Python3.12, Django5.2LTS e DRF. Instalar com `poetry install`, migrar com `poetry run python manage.py migrate` e executar `poetry run python manage.py runserver`.

O baseline original das aulas não estava nos repositórios do usuário. Este projeto reconstrói a livraria com Product(name,price,description,active) conforme exemplo do material de apoio, Category(name,description) e Order(user,products,created_at). Category é FK de Product; Order tem múltiplos produtos e um dono. Os campos e relacionamentos adicionais são decisões explícitas desta implementação.

Branch sugerida `codex/drf-setup`; PR base `main`. O marco preserva a página inicial Django e adiciona `rest_framework` a INSTALLED_APPS. Apenas desenvolvimento local.


## Marco codex/drf-auth

Testes: `python manage.py test`. Branch `codex/drf-auth` com PR base `codex/drf-paginacao`.


## Docker Images

`docker build -t ebac-bookstore:images .`
`docker run --rm -p 127.0.0.1:8000:8000 ebac-bookstore:images`
Consultar `/api/products/`. SQLite é descartável neste marco. Branch `codex/docker-image` base `codex/drf-auth`.
Execução real da imagem depende de Docker Desktop e ainda precisa ser registrada.


## Containers e PostgreSQL

Copie `.env.example` para `.env`, escolha uma senha local e rode `docker compose up --build`. PostgreSQL é acessível apenas dentro da rede Compose. Os dados ficam em volume nomeado. O healthcheck aguarda o banco antes das migrações.
Branch `codex/docker-compose`, base `codex/docker-image`.
