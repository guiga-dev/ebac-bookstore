"""Atualização fixa do Bookstore; nenhum argumento vem do corpo do webhook."""
import logging
import os
from pathlib import Path
import subprocess
import threading

from django.conf import settings

LOGGER = logging.getLogger(__name__)
REPOSITORY_URL = "https://github.com/guiga-dev/ebac-bookstore.git"
DEPLOY_BRANCH = "main"
DEPLOY_LOCK = threading.Lock()


def update_checkout_and_reload():
    """Somente fast-forward de main; alterações locais nunca são descartadas."""
    with DEPLOY_LOCK:
        root = Path(settings.BASE_DIR).resolve()
        wsgi_file = Path(settings.PYTHONANYWHERE_WSGI_FILE).resolve(strict=True)

        def git(*arguments):
            return subprocess.run(
                ["git", "-C", str(root), *arguments],
                check=True, capture_output=True, text=True, timeout=20,
                shell=False,
            )

        if git("symbolic-ref", "--short", "HEAD").stdout.strip() != DEPLOY_BRANCH:
            raise RuntimeError("O checkout de publicação deve estar na branch main.")
        git("diff", "--quiet", "HEAD", "--")
        git("fetch", "--no-tags", REPOSITORY_URL, DEPLOY_BRANCH)
        git("merge", "--ff-only", "FETCH_HEAD")
        os.utime(wsgi_file, None)
        LOGGER.info("Bookstore main atualizado; reload WSGI solicitado.")


def _run_deployment():
    try:
        update_checkout_and_reload()
    except Exception:
        LOGGER.exception("Falha no deploy Bookstore; conferir o error log do PythonAnywhere.")


def schedule_deployment():
    # Retorna HTTP antes de alterar o arquivo WSGI que recarrega o worker.
    worker = threading.Timer(1.0, _run_deployment)
    worker.daemon = True
    worker.start()
