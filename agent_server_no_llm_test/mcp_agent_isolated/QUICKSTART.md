# MCP Agent - Quick Start Guide

**Last Updated:** 2026-06-02  
**Status:** Ready for immediate use or Phase 1 cloud decoupling

---

## 🎯 Three Ways to Proceed

### Option A: Run Immediately (Default Setup)
Runs agent with ALL tools (76 domain + 45 cloud) using embedded SAJHA v2.9.8:

```bash
# Terminal 1: Start SAJHA server (port 3002)
cd sajhamcpserver
python -m venv venv
# Windows: venv\Scripts\activate
# Linux/Mac: source venv/bin/activate
pip install flask flask-socketio python-socketio flask-cors werkzeug pydantic
python run_server.py

# Terminal 2: Start Agent server (port 8000)
python -m venv venv
# Activate as above
pip install -r requirements.txt
cp .env.example .env
# Edit .env: Add your ANTHROPIC_API_KEY
uvicorn agent_server:app --port 8000 --reload

# Open browser
# Login: http://localhost:8000/login.html
# Chat: http://localhost:8000/mcp-agent.html
```

### Option B: Docker (Recommended for Consistency)
```bash
# Local development (auto-hot-reload)
docker-compose -f docker-compose.local.yml up

# Production (supervisord + nginx)
docker-compose -f docker-compose.prod.yml up -d
```

Both containers:
- SAJHA on http://127.0.0.1:3002
- Agent on http://127.0.0.1:8000
- nginx on http://localhost

### Option C: Phase 1 Cloud Decoupling (30 min, Safe)
Disable 45 cloud tools first, then run with 76 domain-only tools:

1. **Run the decoupling script** (see next section)
2. Restart servers
3. Verify cloud tools are gone from `/api/mcp/tools`
4. Proceed to Phase 2 if needed

---

## ⚡ Phase 1: Disable Cloud Tools (30 Minutes)

### Step 1: Run Decoupling Script

```powershell
# PowerShell (Windows)
$cloud_tools = @(
    "sajhamcpserver/config/tools/outlook_tools.json",
    "sajhamcpserver/config/tools/teams_tools.json",
    "sajhamcpserver/config/tools/sharepoint_tools.json",
    "sajhamcpserver/config/tools/confluence_tools.json",
    "sajhamcpserver/config/tools/jira_tools.json",
    "sajhamcpserver/config/tools/powerbi_tools.json"
)

foreach ($tool in $cloud_tools) {
    $json = Get-Content $tool -Raw | ConvertFrom-Json
    $json.enabled = $false
    $json | ConvertTo-Json -Depth 10 | Set-Content $tool
    Write-Host "Disabled: $tool"
}

# Also disable tavily tools (multiple files)
Get-ChildItem "sajhamcpserver/config/tools/tavily*.json" | ForEach-Object {
    $json = Get-Content $_.FullName -Raw | ConvertFrom-Json
    $json.enabled = $false
    $json | ConvertTo-Json -Depth 10 | Set-Content $_.FullName
    Write-Host "Disabled: $($_.Name)"
}
```

### Step 2: Verify Changes

```bash
# Restart SAJHA (hot-reload happens in 5 seconds)
# But explicit restart is safer:
# Kill previous process, then:
cd sajhamcpserver
python run_server.py

# Check API response (should NOT list cloud tools)
curl http://127.0.0.1:3002/api/mcp | jq '.tools[] | select(.name | startswith("outlook_") or startswith("teams_") or startswith("jira_")) | length'
# Should return: 0 (no cloud tools)
```

### Step 3: Test in Agent

```bash
# Restart agent
# Kill previous, then:
uvicorn agent_server:app --port 8000 --reload

# Query via API
curl http://localhost:8000/api/mcp/tools | grep -E "outlook|teams|jira|confluence|sharepoint|power_bi|tavily"
# Should return: nothing (empty)
```

### Step 4: Verify Remaining Tools (76 Domain)

Expected tools after Phase 1:
- ✅ iris_ccr_* (9 tools)
- ✅ duckdb_* (10 tools)
- ✅ sqlselect_* (6 tools)
- ✅ msdoc_* (10 tools) — LOCAL files only!
- ✅ python_execute, python_execution (2 tools)
- ✅ operational_* (7 tools)
- ✅ edgar_*, sec_* (10 tools)
- ✅ yahoo_* (3 tools)
- ✅ bm25_search (1 tool)
- ✅ visualisation (1 tool)
- ✅ workflow_* (2 tools)
- ✅ data_transform, export_* (3 tools)

**Total: 76 tools** ✅

---

## 🔧 Environment Setup (One-Time)

### .env Configuration

```bash
# Copy template
cp .env.example .env

# Edit .env and add your keys:

# 1. Anthropic API
ANTHROPIC_API_KEY=sk-ant-your-actual-key-here
ANTHROPIC_MODEL=claude-haiku-4-5-20251001

# 2. LLM Provider
LLM_PROVIDER=anthropic  # or xai, huggingface, bedrock

# 3. SAJHA Server (usually localhost)
SAJHA_BASE_URL=http://127.0.0.1:3002
SAJHA_API_KEY=sja_full_access_admin  # From sajhamcpserver/config/apikeys.json

# 4. Database
CHECKPOINT_DB_PATH=./sajhamcpserver/data/checkpoints.db

# 5. Testing Values (RESET FOR PRODUCTION)
CONTEXT_TRIGGER_TOKENS=5200          # Change to 120000-150000 for prod
CONTEXT_TAIL_MESSAGES=2              # Change to 6 for prod
CONTEXT_MIN_EXCHANGES_BETWEEN_SUMMARIES=1  # Change to 5-10 for prod
CONTEXT_TARGET_PCT=0.009375          # Change to 0.18 for prod
CONTEXT_MAX_TOKENS=128000
```

### Login Credentials

**Default users** (from `sajhamcpserver/config/users.json`):
- **User:** `risk_agent`
- **Password:** Check users.json for bcrypt hash (or set via admin API)
- **Role:** super_admin (full access)

Alternative admin user:
- **User:** `admin`
- **Role:** admin (worker-scoped access)

---

## 🧪 Testing Workflow

### 1. Basic Health Check
```bash
curl http://localhost:8000/health
# Expected: {"status":"ok"}
```

### 2. Tool Discovery
```bash
# List all available tools
curl http://localhost:8000/api/mcp/tools | jq '.tools | length'
# Expected (after Phase 1): 76 tools
```

### 3. Simple Chat
```bash
# Via frontend:
# 1. Login to http://localhost:8000/login.html
# 2. Navigate to http://localhost:8000/mcp-agent.html
# 3. Type: "What tools do you have?"
# 4. Check response for 76 domain tools only
```

### 4. Tool Execution (Manual)
```bash
curl -X POST http://localhost:8000/api/agent/run \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <JWT_TOKEN>" \
  -d '{
    "worker_id": "w-market-risk",
    "query": "Read file public/index.html",
    "thread_id": "test-thread-1"
  }' \
  --stream
```

### 5. Admin Panel
```
http://localhost:8000/admin.html
# View:
# - Workers
# - Users
# - Enabled tools
# - Audit logs
# - LLM configuration
```

---

## 📂 File Organization

After extraction, your folder looks like:

```
mcp_onprem/mcp_agent/
├── agent/                           ← Agent logic (LangGraph + middlewares)
├── sajhamcpserver/                  ← MCP server (Flask) + 121 tools
├── public/                          ← Frontend (HTML/JS)
├── config/                          ← Configuration templates
├── scripts/                         ← Utility scripts
├── tests/                           ← Test suite
├── agent_server.py                  ← FastAPI entrypoint
├── requirements.txt                 ← Dependencies
├── .env                             ← SECRETS (don't commit)
├── .env.example                     ← Template
├── docker-compose.local.yml         ← Dev setup
├── docker-compose.prod.yml          ← Prod setup
├── Dockerfile                       ← Container image
├── QUICKSTART.md                    ← THIS FILE
├── AGENT_SETUP.md                   ← Detailed setup guide
├── INDEX.md                         ← File inventory & gaps
├── MIGRATION_SUMMARY.md             ← What was pulled
└── CLAUDE.md                        ← Original documentation
```

---

## ⚠️ Common Issues & Solutions

### Issue: SAJHA server not found
```
Error: Failed to connect to SAJHA at http://127.0.0.1:3002
```
**Solution:**
1. Check SAJHA is running: `curl http://127.0.0.1:3002/health`
2. Verify `SAJHA_BASE_URL` in `.env` matches SAJHA's actual URL
3. Ensure SAJHA started before Agent

### Issue: Cloud tools still visible after Phase 1
```
Tools found: outlook_read_email, teams_send_message, ...
```
**Solution:**
1. Verify decoupling script ran successfully (check JSON "enabled": false)
2. SAJHA has 5-second hot-reload — wait 10s after changing config
3. If still present, manually kill SAJHA and restart

### Issue: Agent can't discover tools
```
Error: No tools discovered from SAJHA
```
**Solution:**
1. Check SAJHA is running and healthy: `curl http://127.0.0.1:3002/health`
2. Check SAJHA API key in `.env` matches `config/apikeys.json`
3. Check SAJHA logs for errors
4. Try restarting both servers

### Issue: Summarisation not triggering
```
Context tokens: 5400 → 5400 (should compress)
```
**Solution:**
1. This is expected with testing values (CONTEXT_TRIGGER_TOKENS=5200, only 4 exchanges)
2. For production, increase CONTEXT_TRIGGER_TOKENS to 120000-150000
3. Check middleware order in `agent/agent.py`

---

## 📈 Next Steps After Phase 1

**Checkpoint: All cloud tools disabled ✅**

Now choose:

### Option 1: Stop Here
- Keep using embedded SAJHA v2.9.8 with 76 domain tools
- Simple, stable, fully on-premises
- No further migration needed

### Option 2: Proceed to Phase 2 (v5.0.0 Compatibility)
- Migrate to upstream SAJHA v5.0.0
- Replace 121 domain tools with 497 generic market data tools
- Gain FastAPI (vs Flask), PostgreSQL support, plugin system
- Estimated: 4-5 days full-time
- See INDEX.md and AGENT_SETUP.md for detailed gap analysis

---

## 📞 Support

**Documentation Files** (in this folder):
1. **QUICKSTART.md** — THIS FILE (immediate start)
2. **AGENT_SETUP.md** — Detailed setup & phases
3. **INDEX.md** — File inventory & dependency graph
4. **MIGRATION_SUMMARY.md** — What was pulled & statistics
5. **CLAUDE.md** — Original developer reference

**Repository Links:**
- Source: https://github.com/algowizzzz/mcp-intelligence-agent
- v5.0.0: https://github.com/ajsinha/sajhamcpserver

---

## ✅ Your Next Action

**Choose one:**

1. **Start immediately** (keep all tools):
   ```bash
   # Follow "Option A: Run Immediately" above
   ```

2. **Run with Docker** (recommended):
   ```bash
   docker-compose -f docker-compose.local.yml up
   ```

3. **Disable cloud tools** (Phase 1):
   ```powershell
   # Follow "Phase 1" section above
   ```

**Time required:**
- Option 1-2: 5 minutes setup + 2 minutes startup
- Option 3: 30 minutes (includes testing)

---

**Generated:** 2026-06-02  
**Status:** Ready to go 🚀
