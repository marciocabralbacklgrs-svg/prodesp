"""
Proxy views para os Web Components do Buscador.

Rotas tratadas:
  POST /api/buscadorAgentforce/  →  Salesforce /services/apexrest/buscadorAgentforce/
  GET  /api/services/search      →  Orquestrador API

Dependência: pip install requests
"""

import threading

import requests
from django.conf import settings
from django.http import JsonResponse
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator


# ─── Cache de token Salesforce (em memória, por processo) ────────────────────

_sf_token_lock   = threading.Lock()
_sf_access_token = None


def _get_sf_token():
    global _sf_access_token

    with _sf_token_lock:
        if _sf_access_token:
            return _sf_access_token

        resp = requests.post(
            f"{settings.SF_INSTANCE_URL}/services/oauth2/token",
            data={
                "grant_type":    "client_credentials",
                "client_id":     settings.SF_CLIENT_ID,
                "client_secret": settings.SF_CLIENT_SECRET,
            },
            timeout=10,
        )

        if not resp.ok:
            raise RuntimeError(
                f"Falha na autenticação Salesforce ({resp.status_code}): {resp.text}"
            )

        _sf_access_token = resp.json()["access_token"]
        return _sf_access_token


def _invalidate_sf_token():
    global _sf_access_token
    with _sf_token_lock:
        _sf_access_token = None


# ─── Proxy Salesforce ─────────────────────────────────────────────────────────

@method_decorator(csrf_exempt, name="dispatch")
class BuscadorAgentforceView(View):
    """POST /api/buscadorAgentforce/ → SF /services/apexrest/buscadorAgentforce/"""

    SF_APEX_PATH = "/services/apexrest/buscadorAgentforce/"

    def post(self, request):
        sf_url = f"{settings.SF_INSTANCE_URL}{self.SF_APEX_PATH}"

        for attempt in range(2):
            try:
                token = _get_sf_token()
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
                    timeout=30,
                )
            except requests.RequestException as exc:
                return JsonResponse(
                    {"success": False, "errorMessage": str(exc)}, status=502
                )

            if sf_resp.status_code == 401 and attempt == 0:
                _invalidate_sf_token()
                continue

            return JsonResponse(sf_resp.json(), status=sf_resp.status_code, safe=False)

        return JsonResponse(
            {"success": False, "errorMessage": "Token inválido após renovação."}, status=502
        )


# ─── Proxy Orquestrador ───────────────────────────────────────────────────────

@method_decorator(csrf_exempt, name="dispatch")
class BuscadorSearchView(View):
    """GET /api/services/search → Orquestrador

    Prioridade das credenciais: headers da requisição (embutidos no JS) > settings/.env
    """

    def get(self, request):
        # Credenciais: JS envia nos headers; fallback para settings
        client_id     = request.headers.get("client_id")     or getattr(settings, "ORQUESTRADOR_CLIENT_ID",     "")
        client_secret = request.headers.get("client_secret") or getattr(settings, "ORQUESTRADOR_CLIENT_SECRET", "")

        query_string = request.GET.urlencode()
        url = f"{settings.ORQUESTRADOR_API_URL}?{query_string}" if query_string else settings.ORQUESTRADOR_API_URL

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

        return JsonResponse(resp.json(), status=resp.status_code, safe=False)


# ─── View da página ──────────────────────────────────────────────────────────

from django.shortcuts import render

def buscador_page(request):
    return render(request, "buscador/index.html")
