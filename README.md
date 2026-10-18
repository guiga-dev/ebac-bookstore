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


## Network

Ambos os serviços usam a rede explícita `bookstore_net` com driver `bridge`. A aplicação resolve `db` pelo DNS do Compose e o PostgreSQL não publica porta no host.
Branch `codex/docker-network`, base `codex/docker-compose`.


## Integração contínua

GitHub Actions executa checks, consistência de migrations, testes e build Docker. Workflow separado analisa erros de sintaxe/nome com Ruff e produz anotações de revisão. Recurso equivalente implementado; a aula solicita CodeFactor, cuja ligação à conta GitHub está pendente. Não declarar execução de Actions até o workflow rodar remotamente.
Branch `codex/ci`, base `codex/docker-network`.


## Continuous Delivery · Heroku

Configurar no Heroku `DJANGO_SECRET_KEY` (valor privado aleatório), `DJANGO_ALLOWED_HOSTS=nome-do-app.herokuapp.com`, `DJANGO_DEBUG=false` e `DATABASE_URL` do PostgreSQL. O build instala `requirements.txt` e WhiteNoise serve estáticos. Procfile usa Gunicorn e migrações na fase release.

No GitHub, configurar secrets `HEROKU_API_KEY`, `HEROKU_EMAIL` e variable `HEROKU_APP_NAME`. Após teste, o workflow entrega pushes em main ao app configurado. Primeira publicação: `git push heroku main`. Não incluir tokens no repositório.

Local: `DJANGO_DEBUG=true python manage.py test`. Deploy público/URL e execução do pipeline aguardam conta/credenciais do provedor. Branch `codex/cd`, base `codex/ci`.

CodeFactor é a ferramenta de revisão solicitada; conexão à conta GitHub pendente. Nenhum resultado remoto é alegado.
