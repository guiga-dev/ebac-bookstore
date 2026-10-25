import hashlib
import hmac
import json
from pathlib import Path

from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_POST

from .deployment import schedule_deployment


@require_GET
def hello(request):
    return render(request, "hello_world.html")


@csrf_exempt
@require_POST
def update_server(request):
    secret = settings.GITHUB_WEBHOOK_SECRET
    if not secret:
        return JsonResponse({"error": "Webhook indisponível."}, status=503)
    if len(request.body) > 1024 * 1024:
        return JsonResponse({"error": "Payload excede o limite."}, status=413)
    signature = request.headers.get("X-Hub-Signature-256", "")
    expected = "sha256=" + hmac.new(
        secret.encode("utf-8"), request.body, hashlib.sha256,
    ).hexdigest()
    if not signature.isascii() or not hmac.compare_digest(signature, expected):
        return JsonResponse({"error": "Assinatura inválida."}, status=403)
    event = request.headers.get("X-GitHub-Event", "")
    if event == "ping":
        return JsonResponse({"message": "Webhook autenticado."})
    if event != "push":
        return JsonResponse({"error": "Evento não autorizado."}, status=400)
    try:
        payload = json.loads(request.body)
    except (ValueError, UnicodeDecodeError):
        return JsonResponse({"error": "JSON inválido."}, status=400)
    if not isinstance(payload, dict):
        return JsonResponse({"error": "Payload inválido."}, status=400)
    repository = payload.get("repository")
    if (
        payload.get("ref") != "refs/heads/main"
        or payload.get("deleted", False) is not False
        or not isinstance(repository, dict)
        or repository.get("full_name") != "guiga-dev/ebac-bookstore"
    ):
        return JsonResponse({"error": "Repositório ou ref não autorizados."}, status=403)
    wsgi_file = settings.PYTHONANYWHERE_WSGI_FILE
    if not wsgi_file or not Path(wsgi_file).is_absolute() or not Path(wsgi_file).is_file():
        return JsonResponse({"error": "Deploy indisponível."}, status=503)
    schedule_deployment()
    return JsonResponse({"message": "Deploy agendado."}, status=202)
