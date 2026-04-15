from django.urls import path
from .views import BuscadorAgentforceView, BuscadorSearchView, buscador_page

urlpatterns = [
    # Página principal
    path("buscador/", buscador_page, name="buscador-page"),

    # Proxies de API (chamados pelo JavaScript do componente)
    path("api/buscadorAgentforce/", BuscadorAgentforceView.as_view(), name="buscador-agentforce"),
    path("api/services/search",     BuscadorSearchView.as_view(),      name="buscador-search"),
]
