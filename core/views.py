from __future__ import annotations

from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import render
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_GET


@require_GET
def home(request: HttpRequest) -> HttpResponse:
    return render(request, "core/home.html")


@require_GET
@never_cache
def healthz(request: HttpRequest) -> JsonResponse:
    return JsonResponse({"status": "ok"})
