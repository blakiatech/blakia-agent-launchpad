# 🚀 Blakia Agent Launchpad

[![CI](https://github.com/tu-org/blakia-agent-launchpad/actions/workflows/test.yml/badge.svg)](https://github.com/tu-org/blakia-agent-launchpad/actions/workflows/test.yml)
[![Coverage](https://tu-org.github.io/blakia-agent-launchpad/badges/coverage.svg)](https://tu-org.github.io/blakia-agent-launchpad/htmlcov/index.html)

**Blakia Agent Launchpad** es un **boilerplate industrial** para construir agentes de IA modernos con **[Pydantic-AI](https://github.com/pydantic/pydantic-ai)** y **[LangGraph](https://www.langchain.com/langgraph)**.  

Incluye todo lo necesario para arrancar un proyecto en minutos:  
- Arquitectura hexagonal (`core/`, `adapters/`, `ports/`).  
- CI/CD de calidad industrial (lint, type-check, tests con coverage).  
- Observabilidad integrada (Langfuse + OpenTelemetry).  
- Ejemplo de adapters listos (WhatsApp, Telegram, Webhooks).  
- Memoria en Redis + soporte para RAG (Qdrant/pgvector).  
- Tests de humo, unitarios, E2E y opcionales con LLM-as-Judge.  

---

## ✨ Características principales

- **⚙️ Arquitectura limpia** → separa lógica (`core/`) de conectores (`adapters/`).
- **✅ Calidad asegurada** → Ruff (lint), Mypy (tipado), Pytest + Coverage.
- **📊 Observabilidad real** → traces Langfuse/OTEL en tests E2E.
- **🤖 Multi-adapter** → ejemplos para WhatsApp Business, Telegram y Webhooks.
- **🧠 RAG ready** → integración de memoria semántica con Redis y vector DBs.
- **🧪 Evaluación semántica** → tests opcionales con LLM-as-Judge.
- **🚀 Boilerplate replicable** → lanza MVPs en días, no semanas.

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
````

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
pytest -q
```

### 4. Levantar FastAPI (ejemplo)

```bash
uvicorn app.api:app --reload
```

---

## 🔒 Disclaimer importante

Este repo **NO es Blakbot**.
Blakbot es un producto comercial cerrado de **BlakIA**, valorado en 4.500 €.

**Blakia Agent Launchpad** es solo un **boilerplate educativo y open-source**, pensado como:

* Portfolio técnico (Plan B).
* Base para experimentos y side-projects.
* Inspiración para crear tus propios agentes.

---

## 📜 Licencia

MIT / Apache 2.0 (elige la que prefieras).
Esto significa que cualquiera puede usar este boilerplate libremente.

⚠️ **Blakbot y otros productos comerciales de BlakIA son cerrados y no forman parte de esta licencia.**

---

## 🧭 Roadmap

* [ ] Añadir ejemplo de integración con Qdrant.
* [ ] Extender adapters (Email, Slack).
* [ ] Script `blak-init` para clonar + renombrar proyectos automáticamente.
* [ ] Ejemplos de despliegue en Dokploy/Vercel.

---

© 2025 [BlakIA](https://blakia.es) · *Automatización e Inteligencia Artificial*






