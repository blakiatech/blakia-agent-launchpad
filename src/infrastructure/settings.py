# src/infrastructure/settings.py
from __future__ import annotations
import os
from typing import Optional, Literal
from pydantic import Field, AliasChoices, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

# Opcional: permite .env en raíz del repo (ajusta si lo mueves)
ENV_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env")

class Settings(BaseSettings):
    # --- Core / APIs ---
    openai_api_key: str = Field(
        default="",
        # Acepta BLAKIA_OPENAI_API_KEY o OPENAI_API_KEY
        validation_alias=AliasChoices("BLAKIA_OPENAI_API_KEY", "OPENAI_API_KEY"),
    )
    telegram_bot_token: Optional[str] = Field(
        default=None,
        validation_alias=AliasChoices("BLAKIA_TELEGRAM_BOT_TOKEN", "TELEGRAM_BOT_TOKEN"),
    )
    empresas_api_token: Optional[str] = Field(
        default=None,
        validation_alias=AliasChoices("BLAKIA_EMPRESAS_API_TOKEN", "EMPRESAS_API_TOKEN"),
    )
    generic_webhook_api_key: Optional[str] = Field(
        default=None,
        validation_alias=AliasChoices("BLAKIA_GENERIC_WEBHOOK_API_KEY", "GENERIC_WEBHOOK_API_KEY"),
    )

    # --- WhatsApp / Meta ---
    whatsapp_token: Optional[str] = Field(
        default=None,
        validation_alias=AliasChoices("BLAKIA_WHATSAPP_TOKEN", "WHATSAPP_TOKEN"),
    )
    whatsapp_phone_id: Optional[str] = Field(
        default=None,
        validation_alias=AliasChoices("BLAKIA_WHATSAPP_PHONE_ID", "WHATSAPP_PHONE_ID"),
    )
    whatsapp_verify_token: Optional[str] = Field(
        default=None,
        validation_alias=AliasChoices("BLAKIA_WHATSAPP_VERIFY_TOKEN", "WHATSAPP_VERIFY_TOKEN"),
    )
    whatsapp_api_version: str = Field(
        default="v19.0",
        validation_alias=AliasChoices("BLAKIA_WHATSAPP_API_VERSION", "WHATSAPP_API_VERSION"),
    )
    meta_app_secret: Optional[str] = Field(
        default=None,
        validation_alias=AliasChoices("BLAKIA_META_APP_SECRET", "META_APP_SECRET"),
    )

    # --- Memory / Redis ---
    memory_backend: str = Field(
        default="in_memory",
        validation_alias=AliasChoices("BLAKIA_MEMORY_BACKEND", "MEMORY_BACKEND"),
    )
    redis_url: Optional[str] = Field(
        default=None,
        validation_alias=AliasChoices("BLAKIA_REDIS_URL", "REDIS_URL"),
    )
    redis_host: str = Field(
        default="localhost",
        validation_alias=AliasChoices("BLAKIA_REDIS_HOST", "REDIS_HOST"),
    )
    redis_port: int = Field(
        default=6379,
        validation_alias=AliasChoices("BLAKIA_REDIS_PORT", "REDIS_PORT"),
    )
    redis_db: int = Field(
        default=0,
        validation_alias=AliasChoices("BLAKIA_REDIS_DB", "REDIS_DB"),
    )
    redis_password: Optional[str] = Field(
        default=None,
        validation_alias=AliasChoices("BLAKIA_REDIS_PASSWORD", "REDIS_PASSWORD"),
    )

    # --- Langfuse ---
    langfuse_public_key: Optional[str] = Field(
        default=None,
        validation_alias=AliasChoices("BLAKIA_LANGFUSE_PUBLIC_KEY", "LANGFUSE_PUBLIC_KEY"),
    )
    langfuse_secret_key: Optional[str] = Field(
        default=None,
        validation_alias=AliasChoices("BLAKIA_LANGFUSE_SECRET_KEY", "LANGFUSE_SECRET_KEY"),
    )
    langfuse_host: str = Field(
        default="https://cloud.langfuse.com",
        validation_alias=AliasChoices("BLAKIA_LANGFUSE_HOST", "LANGFUSE_HOST"),
    )

    # --- OpenTelemetry ---
    otel_traces_exporter: Optional[Literal["otlp", "none"]] = Field(
        default="otlp",
        validation_alias=AliasChoices("BLAKIA_OTEL_TRACES_EXPORTER", "OTEL_TRACES_EXPORTER"),
    )
    otel_exporter_otlp_protocol: Optional[Literal["http/protobuf", "grpc"]] = Field(
        default="http/protobuf",
        validation_alias=AliasChoices("BLAKIA_OTEL_EXPORTER_OTLP_PROTOCOL", "OTEL_EXPORTER_OTLP_PROTOCOL"),
    )
    otel_service_name: str = Field(
        default="cordobai-agent",
        validation_alias=AliasChoices("BLAKIA_OTEL_SERVICE_NAME", "OTEL_SERVICE_NAME"),
    )
    otel_resource_attributes: Optional[str] = Field(
        default=None,
        validation_alias=AliasChoices("BLAKIA_OTEL_RESOURCE_ATTRIBUTES", "OTEL_RESOURCE_ATTRIBUTES"),
    )

    # --- Meta ---
    env: str = Field(default="dev", validation_alias=AliasChoices("BLAKIA_ENV", "ENV"))

    model_config = SettingsConfigDict(
        env_file=ENV_PATH,
        case_sensitive=False,
        extra="ignore",          # ↔ en tu antiguo usabas "forbid": relajamos para transición
        env_prefix="BLAKIA_",    # prefijo por defecto (seguimos aceptando legacy via AliasChoices)
    )

    @model_validator(mode="after")
    def _validate_meta_whatsapp(self):
        # Si se configura cualquier credencial WAB, exige meta_app_secret
        if any([self.whatsapp_token, self.whatsapp_phone_id, self.whatsapp_verify_token]):
            if not self.meta_app_secret:
                raise ValueError("META_APP_SECRET/BLAKIA_META_APP_SECRET es obligatorio para verificar X-Hub-Signature-256")
        return self

settings = Settings()

