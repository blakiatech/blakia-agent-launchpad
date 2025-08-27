# 🚀 Blakia Agent Launchpad

**Blakia Agent Launchpad** es un **boilerplate industrial** para construir agentes de IA modernos con **[Pydantic-AI](https://github.com/pydantic/pydantic-ai)** y **[LangGraph](https://www.langchain.com/langgraph)**.

Incluye todo lo necesario para arrancar un proyecto en minutos:

* Arquitectura hexagonal (`core/`, `adapters/`, `ports/`).
* CI/CD de calidad industrial (lint, type-check, tests con coverage).
* Observabilidad integrada (Langfuse + OpenTelemetry).
* Ejemplo de adapters listos (WhatsApp, Telegram, Webhooks).
* Memoria en Redis + soporte para RAG (Qdrant/pgvector).
* Tests de humo, unitarios, E2E y opcionales con LLM-as-Judge (pronto).

---

## ✨ Características principales

* **⚙️ Arquitectura limpia** → lógica (`core/`) desacoplada de conectores (`adapters/`).
* **✅ Calidad asegurada** → Ruff (lint), Mypy (tipado), Pytest + Coverage.
* **📊 Observabilidad real** → traces Langfuse/OTEL en tests E2E.
* **🤖 Multi-adapter** → WhatsApp Business, Telegram y Webhooks incluidos.
* **🧠 RAG ready** → memoria semántica con Redis y vector DBs.
* **🧪 Evaluación semántica** → tests opcionales con LLM-as-Judge.
* **🚀 Boilerplate replicable** → lanza MVPs en días, no semanas.

---

## 📂 Estructura del proyecto

```txt
blakia-agent-launchpad/
├─ src/
│  ├─ core/            # lógica de negocio, graph, agentes
│  ├─ adapters/        # WhatsApp, Telegram, Webhooks, Storage
│  ├─ ports/           # interfaces (inbound/outbound)
│  ├─ observability/   # Langfuse + tracing
│  ├─ app/             # entrypoints (FastAPI, worker)
│  └─ configuration.py # settings
├─ tests/              # unit, e2e, judge
├─ .github/workflows/  # CI/CD (lint, tests, coverage)
├─ pyproject.toml
├─ .coveragerc
├─ mypy.ini
├─ pytest.ini
└─ README.md
```

---

## 🛠️ Uso

### 1. Clonar repo

```bash
git clone https://github.com/tu-org/blakia-agent-launchpad.git
cd blakia-agent-launchpad
```

### 2. Instalar en editable

```bash
pip install -e .
```

### 3. Ejecutar tests

```bash
pytest --cov=core
```

### 4. Levantar FastAPI (ejemplo)

```bash
uvicorn app.api:app --reload
```

---

## 📜 Licencia

Apache 2.0
Esto significa que cualquiera puede usar este boilerplate.

---

## 🧭 Roadmap

* [ ] Añadir ejemplo de integración con Qdrant.
* [ ] Extender adapters (Email, Slack).
* [ ] Ejemplos de Tests LLM as a Judge.

---

© 2025 [BlakIA](https://blakia.es) · *Automatización e Inteligencia Artificial*
