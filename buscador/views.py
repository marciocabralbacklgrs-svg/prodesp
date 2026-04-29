"""
Proxy views para os Web Components do Buscador.

Rotas tratadas:
  POST /api/buscadorAgentforce/  →  Salesforce /services/apexrest/buscadorAgentforce/
  GET  /api/services/search      →  Orquestrador API

Credenciais lidas exclusivamente de variáveis de ambiente via settings/.env.

Dependência: pip install requests
"""

import time
import threading

import requests
from django.conf import settings
from django.http import JsonResponse
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator


# ─── Cache de token Salesforce (em memória, por processo) ────────────────────
# Tokens SF duram 2h por padrão; renovamos 10 min antes para evitar uso de token expirado.

_SF_TOKEN_TTL   = 6600  # segundos (110 min)
_sf_token_lock  = threading.Lock()
_sf_token_cache = {}   # {(instance_url, client_id): (access_token, expires_at)}


def _get_sf_token(instance_url, client_id, client_secret):
    key = (instance_url, client_id)
    now = time.monotonic()
    with _sf_token_lock:
        cached = _sf_token_cache.get(key)
        if cached:
            token, expires_at = cached
            if now < expires_at:
                return token

        resp = requests.post(
            f"{instance_url}/services/oauth2/token",
            data={
                "grant_type":    "client_credentials",
                "client_id":     client_id,
                "client_secret": client_secret,
            },
            timeout=10,
        )

        if not resp.ok:
            raise RuntimeError(
                f"Falha na autenticação Salesforce ({resp.status_code}): {resp.text}"
            )

        token = resp.json()["access_token"]
        _sf_token_cache[key] = (token, now + _SF_TOKEN_TTL)
        return token


def _invalidate_sf_token(instance_url, client_id):
    key = (instance_url, client_id)
    with _sf_token_lock:
        _sf_token_cache.pop(key, None)


# ─── Proxy Salesforce ─────────────────────────────────────────────────────────

@method_decorator(csrf_exempt, name="dispatch")
class BuscadorAgentforceView(View):
    """POST /api/buscadorAgentforce/ → SF /services/apexrest/buscadorAgentforce/"""

    SF_APEX_PATH = "/services/apexrest/buscadorAgentforce/"

    def post(self, request):
        sf_instance_url  = settings.SF_INSTANCE_URL
        sf_client_id     = settings.SF_CLIENT_ID
        sf_client_secret = settings.SF_CLIENT_SECRET
        sf_url = f"{sf_instance_url}{self.SF_APEX_PATH}"

        for attempt in range(2):
            try:
                token = _get_sf_token(sf_instance_url, sf_client_id, sf_client_secret)
            except RuntimeError as exc:
                return JsonResponse(
                    {"success": False, "errorMessage": str(exc)}, status=502
                )

            try:
                sf_resp = requests.post(
                    sf_url,
                    data=request.body,
                    headers={
                        "Content-Type":  "application/json",
                        "Authorization": f"Bearer {token}",
                    },
                    timeout=60,
                )
            except requests.RequestException as exc:
                return JsonResponse(
                    {"success": False, "errorMessage": str(exc)}, status=502
                )

            if sf_resp.status_code == 401 and attempt == 0:
                _invalidate_sf_token(sf_instance_url, sf_client_id)
                continue

            try:
                return JsonResponse(sf_resp.json(), status=sf_resp.status_code, safe=False)
            except Exception:
                return JsonResponse(
                    {"success": False, "errorMessage": f"Resposta inválida do Salesforce ({sf_resp.status_code})"},
                    status=502,
                )

        return JsonResponse(
            {"success": False, "errorMessage": "Token inválido após renovação."}, status=502
        )


# ─── Proxy Orquestrador ───────────────────────────────────────────────────────

@method_decorator(csrf_exempt, name="dispatch")
class BuscadorSearchView(View):
    """GET /api/services/search → Orquestrador"""

    def get(self, request):
        api_url       = settings.ORQUESTRADOR_API_URL
        client_id     = getattr(settings, "ORQUESTRADOR_CLIENT_ID",     "")
        client_secret = getattr(settings, "ORQUESTRADOR_CLIENT_SECRET", "")

        query_string = request.GET.urlencode()
        url = f"{api_url}?{query_string}" if query_string else api_url

        try:
            resp = requests.get(
                url,
                headers={
                    "Content-Type":  "application/json",
                    "client_id":     client_id,
                    "client_secret": client_secret,
                },
                timeout=15,
            )
        except requests.RequestException as exc:
            return JsonResponse({"error": str(exc)}, status=502)

        try:
            return JsonResponse(resp.json(), status=resp.status_code, safe=False)
        except Exception:
            return JsonResponse({"error": f"Resposta inválida do Orquestrador ({resp.status_code})"}, status=502)


# ─── View da página ──────────────────────────────────────────────────────────

from django.shortcuts import render

def buscador_page(request):
    return render(request, "buscador/index.html", {
        "enable_vlibras":        getattr(settings, "ENABLE_VLIBRAS",        False),
        "enable_acessibilidade": getattr(settings, "ENABLE_ACESSIBILIDADE", False),
    })
