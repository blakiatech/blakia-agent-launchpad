# src/infrastructure/server.py
from fastapi import FastAPI
from starlette.responses import Response, JSONResponse

# Routers de adapters (APIRouter), NO aplicaciones
from adapters.generic_webhook.handler import router as generic_router
from adapters.whatsapp_business.handler import router as wab_router
# Para telegram necesitamos revisar si hay token antes de montar
from adapters.telegram import handler as tg_handler

# Prometheus: si no está instalado, exponemos texto básico para no romper
try:
    from prometheus_client import CONTENT_TYPE_LATEST, generate_latest
    def metrics_response() -> Response:
        return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)
except Exception:
    def metrics_response() -> Response:
        # Fallback mínimo: no métricas reales, pero no rompe el /metrics
        return Response("# prometheus_client no instalado\n", media_type="text/plain")

def build_app() -> FastAPI:
    app = FastAPI(title="BlakIA Agent", version="0.1.0")

    # ---------- Rutas de negocio (webhooks) ----------
    # Genérico y WhatsApp siempre montados
    app.include_router(generic_router, prefix="/webhooks/generic", tags=["generic"])
    app.include_router(wab_router,     prefix="/webhooks/whatsapp", tags=["whatsapp"])

    # Telegram solo si hay token (handler hace NO-OP si no, pero mejor no montar rutas)
    if getattr(tg_handler, "TELEGRAM_BOT_TOKEN", None):
        app.include_router(tg_handler.router, prefix="/webhooks/telegram", tags=["telegram"])
    else:
        # Log ligero por consola para desarrollo
        print("⚠️ Telegram router NOT loaded: no TELEGRAM_BOT_TOKEN configured")

    # ---------- Operacional ----------
    @app.get("/", tags=["ops"])
    def index():
        return JSONResponse({"status": "ok", "docs": "/docs", "health": "/health", "metrics": "/metrics"})

    @app.get("/health", tags=["ops"])
    def health():
        # Si más adelante tienes settings, puedes incluir env aquí
        return JSONResponse({"ok": True})

    @app.get("/metrics", tags=["ops"])
    def metrics():
        return metrics_response()

    return app

# Opción cómoda: permitir arrancar sin --factory
app = build_app()
