# MCP Agent Setup & Structure

**Location:** `C:\Users\Durga Vishalini\mcp_onprem\mcp_agent`

**Pulled from:** https://github.com/algowizzzz/mcp-intelligence-agent  
**Last updated:** 2026-06-02

---

## 📁 Folder Structure

```
mcp_agent/
├── agent/                          # LangGraph agent core
│   ├── agent.py                    # Agent factory (create_agent_for_worker)
│   ├── prompt.py                   # System prompts + Python/multi-agent addenda
│   ├── tools.py                    # 5 static tools + dynamic SAJHA tool discovery
│   ├── llm_factory.py              # Multi-provider LLM selection
│   ├── sub_agent_tool.py           # task() tool for multi-agent orchestration
│   ├── sub_agent_executor.py       # Sub-agent lifecycle management
│   ├── workflow_parser.py          # YAML frontmatter parser for workflows
│   ├── summariser.py               # Context compression middleware (180k token trigger)
│   ├── middlewares/                # 9 middleware classes
│   │   ├── audit.py                # Event logging to JSONL
│   │   ├── dangling_tool_call.py   # Repairs orphaned tool_calls after summarisation
│   │   ├── hitl.py                 # Human-in-the-loop approval gates
│   │   ├── loop_detection.py       # Warns at 3 repeats, stops at 5
│   │   ├── memory.py               # Cross-session memory (SQLite, 90-day TTL)
│   │   ├── retry.py                # Exponential backoff for 429/503/502
│   │   ├── subagent_limit.py       # Caps parallel sub-agents (default 3)
│   │   ├── token_budget.py         # Per-query token budget with 80% warning
│   │   ├── tool_error_handling.py  # Exception handling for tool failures
│   │   └── __init__.py
│   └── __init__.py
├── agent_server.py                 # FastAPI entrypoint (~85 endpoints)
├── sajhamcpserver/                 # Embedded SAJHA MCP server (Flask on :3002)
│   ├── run_server.py               # Flask server entry
│   ├── config/
│   │   ├── application.properties  # Data paths, feature flags, external APIs
│   │   ├── server.properties       # Server config (port, hot-reload)
│   │   ├── tools/                  # 121 JSON tool configs
│   │   ├── workers.json            # Worker definitions
│   │   ├── users.json              # User accounts with bcrypt hashes
│   │   ├── apikeys.json            # API key definitions with rate limits
│   │   └── llm_config.json         # LLM provider settings
│   ├── sajha/                      # SAJHA implementation
│   │   ├── tools/impl/             # 41 tool implementation modules
│   │   ├── worker_repository.py    # Worker CRUD
│   │   ├── storage.py              # File storage backend
│   │   └── ...
│   └── data/                       # Runtime data (worker-scoped)
│
├── config/                         # Agent-level configuration
│   └── (agent-specific configs if any)
├── public/                         # Frontend HTML/JS
│   ├── login.html                  # Auth + 3-step onboarding wizard
│   ├── index.html                  # Basic chat UI (87KB)
│   ├── mcp-agent.html              # Market risk chat UI with canvas (273KB)
│   ├── admin.html                  # Admin panel (138KB)
│   ├── js/                         # JavaScript (including file-tree component)
│   └── css/
├── scripts/                        # Utility scripts
├── tests/                          # Unit and integration tests
├── .env                            # **SECRETS** - LLM keys, SAJHA URL, database paths
├── .env.example                    # Template (use as reference, don't commit .env)
├── requirements.txt                # Python dependencies
├── docker-compose.local.yml        # Local dev setup
├── docker-compose.prod.yml         # Production setup
├── Dockerfile                      # Container image definition
├── nginx.conf                      # Reverse proxy config
├── supervisord.conf                # Process manager config (SAJHA + Agent + nginx)
├── CLAUDE.md                       # Developer reference (from original repo)
├── AGENT_SETUP.md                  # THIS FILE
└── README.md                       # (Original from repo)
```

---

## 🔑 Key Components

### 1. **Agent Core** (`agent/`)
- **agent.py**: Initializes LangGraph agent with:
  - 9-middleware stack for safety, compression, audit
  - Worker-scoped configuration
  - Multi-provider LLM support (Anthropic, xAI, Huggingface, Bedrock)
  
- **tools.py**: Discovers tools from SAJHA via POST /api/mcp
  - 5 static tools (read_file, list_files, python_execute, call_code_tool, task)
  - Dynamic discovery of 121+ SAJHA tools
  - Tool timeout + output truncation handling

- **summariser.py**: Context compression
  - Triggers at 180k tokens (90% of 200k context window)
  - Compresses to ~36k tokens (18% of window)
  - Uses LLM to summarize earlier exchanges
  - **CRITICAL**: Uses RemoveMessage to delete head messages before appending summary

- **Middleware Stack** (`middlewares/`):
  1. DanglingToolCall - fixes orphaned calls after summarisation
  2. Summarisation - context compression
  3. MessageTrimmer - hard fallback at 800k chars
  4. SubagentLimit - caps parallel agents (default 3)
  5. LoopDetection - warns at 3 repeats, stops at 5
  6. ToolErrorHandling - catches exceptions
  7. Retry - exponential backoff
  8. TokenBudget - per-query limits
  9. Audit - logs to JSONL

### 2. **Agent Server** (`agent_server.py`)
FastAPI application with ~85 endpoints:
- **Chat API**: `POST /api/agent/run` (SSE streaming)
- **Worker Management**: CRUD for workers
- **User Management**: CRUD for users
- **File System**: Upload, download, search across worker data
- **Admin**: LLM config, connector management, audit logs
- **Health**: `GET /health`

Returns Server-Sent Events (SSE):
- `session`, `text`, `tool_start`, `tool_end`, `canvas`, `hitl`, `usage`, `context_gauge`, `summary_occurred`, etc.

### 3. **Embedded SAJHA Server** (`sajhamcpserver/`)
Flask-based MCP server on port 3002:
- **121 Domain-Specific Tools**:
  - IRIS CCR, DuckDB, SQL queries, MS Docs
  - Outlook, Teams, SharePoint, Confluence, Jira
  - Power BI, Python execution, PDF reading
  - Workflow discovery and execution
  - File operations (read, write, search, templates)

- **Tool Discovery**: `POST /api/mcp` returns all tool definitions
- **Tool Execution**: `POST /api/tools/execute` with body `{tool: "name", arguments: {...}}`
- **Authentication**: Header `Authorization: key` with API key
- **Hot-Reload**: 5-second interval for tool discovery updates

---

## 🚀 Running the Agent

### Prerequisites
- Python 3.10+
- PostgreSQL 13+ (optional, default is SQLite)
- External API keys (see `.env.example`)

### Local Development (Two Terminals)

**Terminal 1 — SAJHA MCP Server:**
```bash
cd sajhamcpserver
# Create venv if needed
python -m venv venv
# On Windows:
venv\Scripts\activate
# On Linux/Mac:
source venv/bin/activate

# Install dependencies (embedded SAJHA)
pip install flask flask-socketio python-socketio flask-cors werkzeug pydantic

# Run server
python run_server.py
# Listens on http://127.0.0.1:3002
```

**Terminal 2 — Agent Server:**
```bash
# From mcp_agent root
# Create venv if needed
python -m venv venv
# Activate as above

# Install dependencies
pip install -r requirements.txt

# Set environment (copy from .env.example, add your keys)
cp .env.example .env
# Edit .env with your API keys and configuration

# Run agent
uvicorn agent_server:app --port 8000 --reload
# Listens on http://127.0.0.1:8000
```

### Or Use Docker

```bash
# Local development (both servers in one container)
docker-compose -f docker-compose.local.yml up

# Production (with supervisord + nginx)
docker-compose -f docker-compose.prod.yml up
```

---

## ⚙️ Configuration

### Key Environment Variables (`.env`)

```bash
# LLM Provider
LLM_PROVIDER=anthropic                    # or xai, huggingface, bedrock
ANTHROPIC_API_KEY=sk-ant-...              # Your Anthropic key
ANTHROPIC_MODEL=claude-haiku-4-5-20251001

# SAJHA Server (internal)
SAJHA_BASE_URL=http://127.0.0.1:3002
SAJHA_API_KEY=sja_full_access_admin       # From sajhamcpserver/config/apikeys.json
SAJHA_AUTH_MODE=jwt

# Context Compression (Testing Values - CHANGE FOR PRODUCTION)
CONTEXT_TRIGGER_TOKENS=5200               # When to compress (testing, use 120000-150000 for prod)
CONTEXT_TARGET_PCT=0.009375               # Target 18% after compression
CONTEXT_TAIL_MESSAGES=2                   # Keep last N messages (testing, use 6 for prod)
CONTEXT_MIN_EXCHANGES_BETWEEN_SUMMARIES=1 # Min exchanges before next compress (testing, use 5-10 for prod)
CONTEXT_MAX_TOKENS=128000                 # Hard limit

# Database (Checkpoints)
CHECKPOINT_DB_PATH=./sajhamcpserver/data/checkpoints.db

# JWT & Auth
JWT_SECRET=sajha-dev-secret-change-in-prod
CORS_ORIGINS=http://localhost:8080

# Storage
STORAGE_BACKEND=local                     # or s3
```

### SAJHA Configuration

**Workers** (`sajhamcpserver/config/workers.json`):
- Worker-scoped system prompts, data paths, tool allowlists
- Example: `w-market-risk` for Market Risk analysis

**Users** (`sajhamcpserver/config/users.json`):
- User accounts with bcrypt password hashes
- Roles: super_admin, admin, user
- Example: `risk_agent` / `RiskAgent2025!`

**API Keys** (`sajhamcpserver/config/apikeys.json`):
- Rate limits, tool access (allowlist/regex/all)
- Example: `sja_full_access_admin` (all tools, 120 req/min)

**LLM Config** (`sajhamcpserver/config/llm_config.json`):
- Hot-swappable LLM provider settings
- Can be updated via `/api/super/llm-config` without restart

---

## 🔗 Next Steps: Cloud Decoupling & v5.0.0 Compatibility

### Phase 1: Disable Cloud Tools
The 45 cloud tools (Microsoft 365, Atlassian, Tavily) can be disabled by setting `"enabled": false` in:
- `sajhamcpserver/config/tools/outlook_tools.json`
- `sajhamcpserver/config/tools/teams_tools.json`
- `sajhamcpserver/config/tools/sharepoint_tools.json`
- `sajhamcpserver/config/tools/confluence_tools.json`
- `sajhamcpserver/config/tools/jira_tools.json`
- `sajhamcpserver/config/tools/power_bi_tools.json`
- `sajhamcpserver/config/tools/tavily_*.json`

**Agent code needs NO changes** — just disable in config, they'll be excluded from discovery.

### Phase 2: PostgreSQL Migration
1. Create schema for users, workers, apikeys, audit logs
2. Update `sajha/worker_repository.py` to use PostgreSQL instead of JSON files
3. Add migration script to convert JSON → SQL

### Phase 3: v5.0.0 Compatibility
Replace embedded SAJHA with https://github.com/ajsinha/sajhamcpserver (v5.0.0):

**Key Changes Required** (7 gaps identified):
1. **Auth Header**: Change from `Authorization: key` to `X-API-Key: key`
2. **Tool Execution**: Endpoint stays same, body format same (POST /api/tools/execute)
3. **Tools Lost**: v5.0.0 has 0 of the 121 domain tools
   - Option A: Accept loss (52 cloud tools disabled anyway, losing 69 domain tools)
   - Option B: Add 121 tools as v5.0.0 plugins (doesn't modify core v5.0.0)
4. **Worker Concept**: v5.0.0 has "tenants" (similar but different schema)
   - Need migration from workers.json → tenants POST /api/tenants
5. **Config Format**: Minimal changes (YAML vs properties)
6. **Storage**: v5.0.0 uses PostgreSQL/SQLite with 19-table schema
7. **Imports**: Remove 3 direct imports from embedded SAJHA

---

## 📋 What Was Pulled vs. What Wasn't

### ✅ Copied to mcp_onprem/mcp_agent:
- `agent/` — Full LangGraph agent with 9 middlewares
- `agent_server.py` — FastAPI app with 85 endpoints
- `sajhamcpserver/` — Embedded SAJHA v2.9.8 (all 121 tools, configs, data)
- `public/` — Frontend HTML/JS (login, chat, admin)
- `config/` — Agent-level configurations
- `scripts/` — Utility scripts
- `tests/` — Unit and integration tests
- `requirements.txt` — Python dependencies
- `.env` — **SECRETS** (keep safe, don't commit)
- `.env.example` — Template for new environments
- Docker & deployment configs

### ❌ NOT Copied (Available in Original Repo):
- `.github/workflows/` — GitHub Actions CI/CD
- `Documentation/` — Word docs (can be added if needed)
- `handover/` — Structured handover package (can be added if needed)
- `requirements/` — Requirements documents
- `UAT_RESULTS/` — Test results
- `fixes/` — Analysis documents

---

## 🔐 Security Notes

1. **.env contains secrets** — Do NOT commit to version control
2. **Password hashes** — SAJHA uses bcrypt (salted, non-reversible)
3. **API keys** — Keep `SAJHA_API_KEY` and `ANTHROPIC_API_KEY` safe
4. **Audit logs** — All tool calls logged to `data/audit/tool_calls.jsonl` with sensitive field redaction
5. **Path traversal protection** — File paths validated via `startswith()` against root
6. **JWT expiry** — 7 days by default, configurable

---

## 📊 Data Isolation (Worker-Scoped)

All data follows per-worker isolation: `./data/workers/{worker_id}/`

Example for `w-market-risk`:
```
./data/workers/w-market-risk/
├── domain_data/
│   ├── iris/iris_combined.csv           # IRIS counterparty data
│   ├── duckdb/                          # DuckDB data files
│   ├── sqlselect/                       # SQL Select data
│   ├── msdocs/                          # Uploaded Word/Excel docs
│   ├── counterparties/                  # Counterparty data
│   └── osfi/                            # Regulatory documents
├── workflows/verified/                  # Approved multi-agent workflows
├── templates/                           # Document templates
├── my_data/
│   └── risk_agent/                      # Per-user uploaded files
└── (user-specific folders per user_id)
```

---

## 📞 Support & Documentation

- **Original Repo**: https://github.com/algowizzzz/mcp-intelligence-agent
- **CLAUDE.md**: Detailed architecture & API reference (in this folder)
- **v5.0.0 Repo**: https://github.com/ajsinha/sajhamcpserver (upstream for comparison)
- **Gap Analysis**: See fixes/gap_analysis_v2.docx (corrected analysis)

---

## 🎯 Production Checklist

Before deploying to production:

- [ ] Reset CONTEXT_TRIGGER_TOKENS to 120000-150000 (from 5200)
- [ ] Reset CONTEXT_TAIL_MESSAGES to 6 (from 2)
- [ ] Reset CONTEXT_MIN_EXCHANGES_BETWEEN_SUMMARIES to 5-10 (from 1)
- [ ] Change JWT_SECRET to a secure random string
- [ ] Set CORS_ORIGINS to production domain(s)
- [ ] Configure PostgreSQL (remove SQLite for production)
- [ ] Enable HTTPS (SSL certificate in docker-compose.prod.yml)
- [ ] Rotate all API keys (ANTHROPIC_API_KEY, SAJHA_API_KEY, etc.)
- [ ] Test summarisation with production token values
- [ ] Run full UAT with multi-worker scenarios
- [ ] Configure backup and recovery procedures

---

**Pulled on:** 2026-06-02  
**Status:** Ready for cloud decoupling & v5.0.0 compatibility work
