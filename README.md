# Bookstore — Continuous Delivery no PythonAnywhere

Implementação local para o PDF atualizado do módulo: publicar a API no PythonAnywhere e receber notificações GitHub em `/update_server/`. A API Bookstore e seus endpoints anteriores foram preservados; `/hello/` renderiza `bookstore/templates/hello_world.html`.

## Estado atual

**Publicado:** https://guigaprimebixo.pythonanywhere.com/hello/ e API em /api/products/. Conta exclusiva guigaprimebixo, com Python 3.12, WSGI, HTTPS, DEBUG=false e SQLite persistente. Migrações e collectstatic concluídos em 25/10/2026. Testes: 21 locais e CI GitHub Actions aprovados. Webhook ativo (push/JSON/HTTPS/HMAC SHA256). Teste real em 25/10/2026: commit 5b22dd389b8f428a067c772ca1a879a58524c989 recebeu HTTP 202 e a nova mensagem apareceu em /hello/ sem pull/reload manual. Atividade enviada à EBAC e recebida para avaliação.

## Preparação no provedor (somente quando houver conta separada)

1. Clonar `https://github.com/guiga-dev/ebac-bookstore.git` em diretório próprio e usar a branch fixa `main` após revisão/merge. O checkout deve estar limpo.
2. Criar virtualenv Python 3.12, instalar `requirements.txt`, executar migrações e `collectstatic`. Configurar um webapp Django manual, source directory e virtualenv na tela Web.
3. No WSGI privado do PythonAnywhere, definir `DJANGO_SETTINGS_MODULE=bookstore.settings`, `DJANGO_SECRET_KEY`, `DJANGO_DEBUG=false`, `DJANGO_ALLOWED_HOSTS` com o domínio exato e, se necessário, `DATABASE_URL`. Manter essas configurações fora do repositório.
4. Definir também `GITHUB_WEBHOOK_SECRET` com valor aleatório privado e `PYTHONANYWHERE_WSGI_FILE` com o caminho absoluto do arquivo WSGI existente, por exemplo `/var/www/CONTA_pythonanywhere_com_wsgi.py` (substituir pelo arquivo real da conta Bookstore). O exemplo não é uma conta criada.
5. Adicionar o diretório do checkout ao `sys.path` no WSGI e obter `application` com `django.core.wsgi.get_wsgi_application()`. Fazer o primeiro reload manual e conferir `/api/products/` e `/hello/`.
6. Só então configurar webhook GitHub para `https://DOMINIO_REAL/update_server/`, JSON, evento push e o mesmo segredo privado. Nenhuma chave SSH de escrita é necessária para buscar o repositório público por HTTPS.

## Contrato do webhook

- Apenas POST; HMAC SHA-256 obrigatório sobre o corpo original, validado em tempo constante pelo header `X-Hub-Signature-256`.
- Ausência de segredo falha com 503; assinatura inválida, ref/repositório incorretos ou exclusão de branch não acionam atualização.
- `ping` assinado retorna 200 sem deploy. Apenas `push` de `guiga-dev/ebac-bookstore`, ref exata `refs/heads/main`, é autorizado.
- O trabalho começa numa thread com atraso curto; a resposta 202 informa **agendamento**, não conclusão. Isso permite responder antes do reload WSGI. Falhas posteriores ficam no error log do provedor. A thread não é uma fila persistente.
- Comandos são listas fixas `subprocess.run(..., shell=False)`: verificar `main`, verificar checkout limpo, buscar o repositório fixo por HTTPS e aplicar somente fast-forward de `FETCH_HEAD`. Nenhum comando, caminho ou branch vem do payload.
- Após sucesso, `os.utime` toca o arquivo WSGI existente definido na configuração privada. Sem reset destrutivo, comandos shell do payload ou instalação automática de dependências/migrações. Mudanças de dependências/esquema precisam de etapa operacional revisada.

## Verificação local

Na raiz deste projeto, com `DJANGO_DEBUG=true`, executar `python manage.py test`. Os testes não acessam GitHub nem PythonAnywhere: mockam atualização, subprocessos, Timer e touch. Cobrem HMAC inválido, segredo ausente, ping, evento/ref/repositório incorretos, push autorizado, comandos fixos, branch local errada e template `/hello/`, além da suíte anterior do Bookstore.

O workflow Heroku foi removido. Os workflows existentes de CI/revisão continuam; nenhum secret, webhook, conta ou PR foi alterado remotamente nesta preparação. O PR existente é `https://github.com/guiga-dev/ebac-bookstore/pull/10`, branch `codex/cd`, base `codex/ci`; o agente principal decidirá a publicação da alteração.
