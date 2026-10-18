# Bookstore · configuração DRF

Projeto novo em Python3.12, Django5.2LTS e DRF. Instalar com `poetry install`, migrar com `poetry run python manage.py migrate` e executar `poetry run python manage.py runserver`.

O baseline original das aulas não estava nos repositórios do usuário. Este projeto reconstrói a livraria com Product(name,price,description,active) conforme exemplo do material de apoio, Category(name,description) e Order(user,products,created_at). Category é FK de Product; Order tem múltiplos produtos e um dono. Os campos e relacionamentos adicionais são decisões explícitas desta implementação.

Branch sugerida `codex/drf-setup`; PR base `main`. O marco preserva a página inicial Django e adiciona `rest_framework` a INSTALLED_APPS. Apenas desenvolvimento local.


## Marco codex/drf-viewsets

Testes: `python manage.py test`. Branch `codex/drf-viewsets` com PR base `codex/drf-serializers`.
