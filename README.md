# Generador de Contraseñas — CRYPT_TYPE

Generador de contraseñas seguras con arquitectura **doble**:
- **Cliente** — JS con `crypto.getRandomValues` (rechazo-muestreo sin sesgo).
- **Servidor** — Django REST con `secrets.SystemRandom`.

El historial vive **solo en el navegador** (IndexedDB). El servidor no persiste
contraseñas en ningún momento.

## Stack

- Python 3.13 · Django 6 · Django REST Framework 3.17
- `uv` para gestión de entornos y bloqueo (`uv.lock`)
- Pytest + coverage (≥ 85%), ruff, mypy + stubs, bandit, pip-audit, djlint, gitleaks
- Docker multi-stage · Gunicorn · WhiteNoise
- GitHub Actions: lint · typecheck · security · tests · docker+Trivy

## Setup local

```bash
uv sync --all-groups
cp .env.example .env
uv run python manage.py migrate
uv run python manage.py runserver
# http://127.0.0.1:8000/
```

## Ejecutar la API

```bash
curl -X POST http://127.0.0.1:8000/api/v1/generate \
    -H "Content-Type: application/json" \
    -d '{"length":20,"uppercase":true,"lowercase":true,"numbers":true,"symbols":true}'
```

Respuesta:
```json
{
    "password": "…",
    "strength": "excellent",
    "entropy_bits": 131.14,
    "alphabet_size": 89
}
```

Rate-limit: `30/min` por IP (anónimo). Respuesta incluye `Cache-Control: no-store`.

## Tests

```bash
uv run pytest --cov=core --cov-report=term-missing --cov-fail-under=85
```

## Calidad y seguridad (paridad con CI)

```bash
uv run ruff check .
uv run ruff format --check .
uv run mypy core settings
uv run bandit -r core settings -c pyproject.toml
uv run pip-audit --strict --ignore-vuln CVE-2026-3219  # pip self; runtime uses uv
uv run djlint --check templates

# Pre-commit local
uv run pre-commit install
uv run pre-commit run --all-files
```

## Django deploy check

```bash
DJANGO_SETTINGS_MODULE=settings.production \
DJANGO_SECRET_KEY="$(python -c 'import secrets; print(secrets.token_urlsafe(50))')" \
DJANGO_ALLOWED_HOSTS=example.com \
DJANGO_CSRF_TRUSTED_ORIGINS=https://example.com \
uv run python manage.py check --deploy
```

## Docker

```bash
docker compose build
docker compose up -d
curl http://localhost:8000/healthz/
docker compose down
```

## Hardening incluido

| Medida | Detalle |
|---|---|
| CSP estricta | `default-src 'self'`; sin inline, sin CDN |
| HSTS | 1 año, includeSubDomains, preload |
| Cookies | `Secure`, `HttpOnly`, `SameSite=Lax` |
| Headers | `X-Frame-Options: DENY`, `Referrer-Policy: same-origin`, `X-Content-Type-Options: nosniff`, `Cross-Origin-Opener-Policy: same-origin` |
| CSRF | Tokens DRF + cookie segura |
| Rate-limit | `30/min` anónimo en `/api/v1/generate` |
| Entropía | `secrets.SystemRandom` (servidor), `crypto.getRandomValues` + rejection sampling (cliente) |
| Secretos | `django-environ`, `SECRET_KEY` sólo por entorno |
| Imagen | `python:3.13-slim`, usuario no-root (uid 1000), FS read-only, `cap_drop: ALL`, `no-new-privileges` |
| Supply chain | `pip-audit` y Trivy en CI |

## Estructura

```
core/
    services/        # Lógica pura de generación y strength (testeada 98%)
    api/             # DRF: serializer, view, throttling
    tests/           # pytest TDD
settings/
    base.py development.py production.py test.py
static/js/           # Módulos ES: generator, strength, history, app
static/css/main.css  # Tema brutalista/typewriter sin dependencias
docker/              # Dockerfile + entrypoint
.github/workflows/   # ci.yml (lint·type·security·test·docker), docker.yml (release)
```

## TDD workflow

1. Escribe test rojo → `uv run pytest core/tests/test_X.py::test_y`.
2. Implementa mínimo para verde.
3. Refactoriza con tests pasando.

El servicio de generación (`core/services/password.py`) está cubierto por 16 tests
incluyendo verificación explícita de uso de `secrets.SystemRandom`, distribución
chi-cuadrado sobre 400 × 64 = 25 600 muestras, y garantía de presencia de al menos
un carácter de cada clase activa.
