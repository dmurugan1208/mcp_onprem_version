# MCP Agent - File Index & Dependency Map

**Location:** `C:\Users\Durga Vishalini\mcp_onprem\mcp_agent`  
**Pulled from:** https://github.com/algowizzzz/mcp-intelligence-agent  
**Status:** Ready for Cloud Decoupling (Phase 1) & v5.0.0 Compatibility (Phase 2)

---

## 📋 Agent Core Files

### Main Application Entry

| File | Size | Purpose | Dependencies |
|------|------|---------|--------------|
| `agent_server.py` | 170 KB | FastAPI app with 85 endpoints | `fastapi`, `uvicorn`, `langchain`, `agent/`, `sajhamcpserver/` |

### Agent Factory & Core Logic

| File | Size | Purpose | Dependencies |
|------|------|---------|--------------|
| `agent/agent.py` | 5 KB | LangGraph agent factory | `langchain`, `langchain_core`, `pydantic`, `middlewares/` |
| `agent/prompt.py` | 7 KB | System prompts + addenda | `langchain` |
| `agent/tools.py` | 18 KB | Tool discovery & execution | `langchain`, `httpx`, `sajhamcpserver/` |
| `agent/llm_factory.py` | 6 KB | Multi-provider LLM selection | `anthropic`, `groq`, `huggingface`, `bedrock` |
| `agent/summariser.py` | 14 KB | Context compression (180k trigger) | `langchain`, `anthropic`, `pydantic` |
| `agent/sub_agent_tool.py` | 9 KB | `task()` tool for multi-agent orchestration | `langchain`, `concurrent.futures` |
| `agent/sub_agent_executor.py` | 11 KB | Sub-agent lifecycle (2-pool threading) | `threading`, `langchain` |
| `agent/workflow_parser.py` | 7 KB | YAML frontmatter parser for workflows | `yaml`, `pydantic` |
| `agent/__init__.py` | 0 KB | Package marker | — |

### Middleware Stack (9 Classes)

| File | Size | Purpose | Execution Order |
|------|------|---------|-----------------|
| `agent/middlewares/dangling_tool_call.py` | 4 KB | Repairs orphaned tool_calls after summarisation | 1st |
| `agent/middlewares/__init__.py` | 3 KB | Middleware exports | — |
| `agent/middlewares/audit.py` | 16 KB | Event logging to JSONL | 9th (last) |
| `agent/middlewares/hitl.py` | 9 KB | Human-in-the-loop approval gates | Optional |
| `agent/middlewares/loop_detection.py` | 10 KB | MD5 fingerprint detection (warn at 3, stop at 5) | 5th |
| `agent/middlewares/memory.py` | 16 KB | Cross-session memory (SQLite, 90-day TTL) | Optional |
| `agent/middlewares/retry.py` | 5 KB | Exponential backoff for 429/503/502 | 7th |
| `agent/middlewares/subagent_limit.py` | 4 KB | Caps parallel sub-agents (default 3) | 4th |
| `agent/middlewares/token_budget.py` | 9 KB | Per-query token budget with 80% warning | 8th |
| `agent/middlewares/tool_error_handling.py` | 3 KB | Exception handling for tool failures | 6th |

---

## 📦 Embedded SAJHA Server (Flask MCP)

### Server Core

| File | Size | Purpose | Dependencies |
|------|------|---------|--------------|
| `sajhamcpserver/run_server.py` | 11 KB | Flask server entry point | `flask`, `flask_socketio`, `config/` |

### Configuration Files (CRITICAL)

| File | Size | Purpose | Cloud Decoupling Impact |
|------|------|---------|------------------------|
| `sajhamcpserver/config/users.json` | 10 KB | User accounts (17 users with bcrypt hashes) | ✅ No cloud deps |
| `sajhamcpserver/config/workers.json` | Large | Worker definitions with system prompts, data paths, tool allowlists | ✅ No cloud deps |
| `sajhamcpserver/config/apikeys.json` | 5 KB | API keys with rate limits & tool access control | ✅ No cloud deps |
| `sajhamcpserver/config/llm_config.json` | 2 KB | LLM provider settings (hot-swappable) | ✅ No cloud deps |
| `sajhamcpserver/config/application.properties` | 5 KB | Data paths, feature flags, external API URLs | ⚠️ Some cloud API configs |
| `sajhamcpserver/config/server.properties` | 2 KB | Port (3002), hot-reload (5s), rate limits | ✅ No cloud deps |

### Tool Configurations (121 Tools)

**Location:** `sajhamcpserver/config/tools/`

**CLOUD TOOLS (45 total - can be disabled):**

| Tool Group | Count | Tool Files | Cloud Service | Phase 1 Action |
|-----------|-------|-----------|---------------|---------------|
| Outlook | 6 | `outlook_tools.json` | Microsoft 365 | Disable (set `"enabled": false`) |
| Teams | 6 | `teams_tools.json` | Microsoft 365 | Disable |
| SharePoint | 6 | `sharepoint_tools.json` | Microsoft 365 | Disable |
| Confluence | 5 | `confluence_tools.json` | Atlassian Cloud | Disable |
| Jira | 7 | `jira_tools.json` | Atlassian Cloud | Disable |
| Power BI | 6 | `powerbi_tools.json` | Microsoft Cloud | Disable |
| Tavily Search | 3+ | `tavily_*.json` | Tavily API | Disable |
| **SUBTOTAL** | **45** | — | External | **DISABLE ALL** |

**DOMAIN TOOLS (76 total - on-premises capable):**

| Tool Group | Count | Tool Files | Infrastructure | Phase 1 Action |
|-----------|-------|-----------|-----------------|---------------|
| IRIS CCR | 9 | `iris_ccr_tools.json` | CSV + pandas | ✅ Keep enabled |
| DuckDB OLAP | 10 | `duckdb_*.json` (2 files) | SQLite/Parquet | ✅ Keep enabled |
| SQL Select | 6 | `sqlselect_tool.json` | Database | ✅ Keep enabled |
| MS Docs | 10 | `msdoc_tools.json` | Local files | ✅ Keep enabled |
| Python Execution | 2 | `python_executor.json` | Sandboxed env | ✅ Keep enabled |
| Operational Tools | 7 | `operational_tools.json` | File system | ✅ Keep enabled |
| SEC EDGAR | 10 | `edgar_*.json` (2 files) | SEC API (public) | ✅ Keep enabled |
| Yahoo Finance | 3 | `tavily_yahoo_finance_tool.json` | Public API | ✅ Keep enabled |
| Visualization | 1 | `visualisation_tools.json` | Plotly HTML | ✅ Keep enabled |
| Data Transform | 3 | `data_transform_tools.json` | In-memory | ✅ Keep enabled |
| Workflow Tools | 2 | `workflow_tools.json` | File system | ✅ Keep enabled |
| Search (BM25) | 1 | `bm25_search_tool.json` | In-memory index | ✅ Keep enabled |
| **SUBTOTAL** | **76** | — | On-premises | **KEEP ALL** |

### Tool Implementation Modules

**Location:** `sajhamcpserver/sajha/tools/impl/`

Contains 41 Python modules implementing the 121 tools above (example: `iris_ccr_tools.py`, `duckdb_olap_tools_refactored.py`, etc.)

### SAJHA Core Libraries

| File | Size | Purpose |
|------|------|---------|
| `sajhamcpserver/sajha/worker_repository.py` | — | Worker CRUD (JSON-based, will migrate to PostgreSQL) |
| `sajhamcpserver/sajha/storage.py` | — | File storage backend (local or S3) |
| `sajhamcpserver/sajha/tools/` | — | Tool registry and discovery |
| `sajhamcpserver/data/` | — | Runtime data (worker-scoped: checkpoints, IRIS CSVs, DuckDB files, etc.) |

---

## 🌐 Frontend Files

| File | Size | Purpose | Libraries |
|------|------|---------|-----------|
| `public/login.html` | — | Auth + 3-step onboarding | HTML/CSS/JS |
| `public/index.html` | 87 KB | Basic chat UI | HTML/CSS/JS/fetch API |
| `public/mcp-agent.html` | 273 KB | Market risk chat with canvas & file browser | HTML/CSS/JS/WebSocket |
| `public/admin.html` | 138 KB | Admin panel (workers, users, tools, audit, LLM config) | HTML/CSS/JS |
| `public/js/file-tree.js` | — | Reusable file tree component (1,200 lines) | Vanilla JS |
| `public/js/` | — | Additional JS utilities | — |
| `public/css/` | — | Stylesheets | CSS |

---

## ⚙️ Configuration & Deployment

| File | Size | Purpose |
|------|------|---------|
| `.env` | 3 KB | **SECRETS** — API keys, SAJHA URL, token values (DO NOT COMMIT) |
| `.env.example` | 3 KB | Template for `.env` (commit this, not `.env`) |
| `requirements.txt` | 709 B | Python dependencies |
| `conftest.py` | 1.5 KB | Pytest configuration |
| `Dockerfile` | 5 KB | Docker image definition |
| `docker-compose.local.yml` | 2 KB | Local dev setup (SAJHA + Agent) |
| `docker-compose.prod.yml` | 5 KB | Production setup (supervisord + nginx) |
| `nginx.conf` | 4 KB | Reverse proxy config |
| `supervisord.conf` | 2 KB | Process manager (manages SAJHA, Agent, nginx) |
| `.gitignore` | — | Git exclusions |
| `.dockerignore` | — | Docker build exclusions |

---

## 📖 Documentation

| File | Size | Purpose |
|------|------|---------|
| `CLAUDE.md` | 18 KB | Original developer reference (architecture, APIs, middleware stack) |
| `AGENT_SETUP.md` | — | Setup instructions for cloud decoupling & v5.0.0 compatibility |
| `INDEX.md` | THIS FILE | Complete file inventory & dependency map |

---

## 🧪 Testing & Scripts

| File | Size | Purpose |
|------|------|---------|
| `scripts/` | — | Utility scripts (data download, deployment, etc.) |
| `tests/` | — | Unit and integration tests |
| `test_admin_api.py` | 14 KB | Admin API tests |
| `test_platform_complete.py` | 48 KB | Comprehensive platform tests |
| `test_uat_*.py` | — | UAT test suites |

---

## 🔗 Dependency Graph

```
┌─────────────────────────────────────────────────────────────┐
│ agent_server.py (FastAPI)                                  │
│ - Authenticates users (JWT)                                │
│ - Routes chat requests → agent/agent.py                    │
│ - Manages workers, users, files                            │
│ - Returns SSE events (text, tools, summary, etc.)         │
└──────────────┬──────────────────────────────────────────────┘
               │
       ┌───────▼──────────────────────────────┐
       │ agent/agent.py (LangGraph)           │
       │ - Creates agent for worker           │
       │ - Configures middleware stack        │
       │ - Runs inference loop                │
       └───────┬──────────────────────────────┘
               │
       ┌───────┴────────────────────────────────────────────────┐
       │                                                       │
   ┌───▼─────────┐  ┌─────────────────────┐  ┌──────────────┐
   │ agent/tools │  │ agent/llm_factory   │  │ agent/       │
   │ .py         │  │ (Anthropic/xAI/HF)  │  │ summariser   │
   └───┬─────────┘  └─────────────────────┘  └──────────────┘
       │                                      (at 180k tokens)
       │ discover tools via                   │
       │ POST /api/mcp                        │ RemoveMessage
       │                                      │ + LLM summary
       └─────────────┬────────────────────────┘
                     │
                     │ calls tools via
                     │ POST /api/tools/execute
                     │
            ┌────────▼─────────────────────┐
            │ sajhamcpserver/ (Flask)      │
            │ Port :3002                   │
            │ - Authentication (apikeys)   │
            │ - Tool registry (121 tools)  │
            │ - Tool execution             │
            │ - Hot-reload (5s interval)   │
            └────────┬─────────────────────┘
                     │
       ┌─────────────┼─────────────────────┐
       │             │                     │
   ┌───▼──────┐  ┌──▼──────┐  ┌──────────▼─┐
   │ Domain   │  │ Cloud    │  │ Data       │
   │ Tools    │  │ Tools    │  │ Storage    │
   │ (76)     │  │ (45)     │  │            │
   │ ✅ Keep  │  │ 🔴 Disable  │ CSV, DB  │
   │          │  │ Phase 1  │  │            │
   └──────────┘  └──────────┘  └────────────┘
```

---

## 🚀 Phase 1: Cloud Decoupling (Disable 45 Tools)

**Files to modify:**
1. `sajhamcpserver/config/tools/outlook_tools.json` → Set `"enabled": false`
2. `sajhamcpserver/config/tools/teams_tools.json` → Set `"enabled": false`
3. `sajhamcpserver/config/tools/sharepoint_tools.json` → Set `"enabled": false`
4. `sajhamcpserver/config/tools/confluence_tools.json` → Set `"enabled": false`
5. `sajhamcpserver/config/tools/jira_tools.json` → Set `"enabled": false`
6. `sajhamcpserver/config/tools/powerbi_tools.json` → Set `"enabled": false`
7. `sajhamcpserver/config/tools/tavily_*.json` (3+ files) → Set `"enabled": false`

**Agent impact:** NONE — Tool discovery will automatically exclude disabled tools

**Estimated effort:** 30 minutes (scripted PowerShell can do all 7 files at once)

---

## 🔄 Phase 2: v5.0.0 Compatibility (7 Gaps)

### Gap 1: Auth Header
- **Current:** `Authorization: key` (embedded SAJHA v2.9.8)
- **v5.0.0:** `X-API-Key: key`
- **Fix location:** `agent/tools.py` line ~150 (in `_call_sajha()` function)

### Gap 2: Tools Lost
- **Current:** 121 domain tools (IRIS, DuckDB, Outlook, Jira, Power BI, Python exec, etc.)
- **v5.0.0:** 497 generic market data tools (ZERO overlap with current 121)
- **Options:**
  - A: Accept loss (52 cloud tools gone anyway)
  - B: Add 121 as v5.0.0 plugins (extends v5.0.0, doesn't modify core)

### Gap 3: Config Format
- **Current:** `.properties` + JSON configs
- **v5.0.0:** YAML `application.yml` + JSON plugin manifests
- **Fix:** Minor updates in `sajhamcpserver/config/` loading

### Gap 4: Worker Concept
- **Current:** `workers.json` with worker definitions, tool allowlists, data paths
- **v5.0.0:** "Tenants" with fnmatch tool patterns
- **Fix:** Migrate workers → tenants via POST /api/tenants

### Gap 5: Tool Execution Endpoint
- **Current:** POST /api/tools/execute with body `{tool: "name", arguments: {...}}`
- **v5.0.0:** POST /api/tools/{name}/execute with args directly
- **Fix:** `agent/tools.py` line ~160

### Gap 6: Storage Backend
- **Current:** JSON files (users.json, workers.json, apikeys.json)
- **v5.0.0:** PostgreSQL/SQLite with 19-table schema
- **Fix:** Migrate `sajha/worker_repository.py` to SQL

### Gap 7: Direct Imports
- **Current:** 3 direct imports from embedded SAJHA in agent_server.py:
  ```python
  from sajha.tools.impl.fs_index import build_index, get_index
  from sajha.worker_repository import WorkerRepository, PostgresWorkerRepository
  from sajha.storage import storage as _storage
  ```
- **v5.0.0:** Different module structure
- **Fix:** Replace with HTTP API calls or plugin system

**Estimated effort:** 4-5 days (Gap 2 is biggest if choosing Option B)

---

## 📊 Summary of What Was Pulled

| Category | Files | Status | Cloud Deps |
|----------|-------|--------|-----------|
| **Agent Core** | 8 core + 9 middleware | ✅ Complete | None |
| **SAJHA Server** | run_server.py + 6 config files + 41 tool modules | ✅ Complete | 45 tools |
| **Frontend** | 4 HTML + JS/CSS | ✅ Complete | None |
| **Config** | .env, requirements.txt, Docker files | ✅ Complete | None |
| **Tests** | Unit + integration + UAT | ✅ Complete | None |
| **Docs** | CLAUDE.md, AGENT_SETUP.md, INDEX.md | ✅ Complete | None |

**Total:** 120+ files, ~500 KB of code + configs, ~1 GB with data (IRIS CSVs, checkpoints DB, etc.)

---

## 🎯 Next Actions

1. **Review this INDEX.md** to understand file structure
2. **Read AGENT_SETUP.md** for cloud decoupling & v5.0.0 steps
3. **Phase 1:** Disable 45 cloud tools (30 min, safe, reversible)
4. **Phase 2:** v5.0.0 compatibility work (4-5 days, bigger changes)

---

**Generated:** 2026-06-02  
**Status:** Ready for implementation
