# MCP Agent Architecture Overview

**Location:** `C:\Users\Durga Vishalini\mcp_onprem\mcp_agent`  
**Version:** Extracted 2026-06-02  
**Status:** Ready for cloud decoupling and v5.0.0 compatibility work

---

## 🏗️ System Architecture

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                        Web Browsers / HTTP Clients                           │
│                                                                              │
│  ┌─────────────────────────┐  ┌──────────────────┐  ┌──────────────────┐  │
│  │ Login UI                │  │ Chat UI          │  │ Admin Panel      │  │
│  │ (login.html)            │  │ (mcp-agent.html) │  │ (admin.html)     │  │
│  │ • 3-step onboarding     │  │ • SSE streaming  │  │ • Workers        │  │
│  │ • JWT auth              │  │ • Canvas charts  │  │ • Users          │  │
│  │ • Rate limiting         │  │ • File browser   │  │ • Tools list     │  │
│  └─────────────────────────┘  └──────────────────┘  └──────────────────┘  │
└────────────┬─────────────────────────────────────────────────────────────────┘
             │ HTTP/WebSocket
             │ (port 8000)
             ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│                    Agent Server (FastAPI, agent_server.py)                  │
│                                                                              │
│  • 85 REST endpoints (chat, workers, users, files, audit, etc.)           │
│  • JWT authentication & RBAC (super_admin, admin, user)                    │
│  • SSE streaming for real-time events                                      │
│  • Worker-scoped data isolation                                            │
│  • Rate limiting (10 login attempts/60s)                                   │
│  • Path traversal protection                                               │
│                                                                              │
│  POST /api/agent/run ──────┐                                               │
│  (SSE streaming)           │                                               │
│                            ▼                                               │
│  ┌──────────────────────────────────────────────────────────────────────┐ │
│  │              LangGraph Agent (agent/agent.py)                        │ │
│  │                                                                      │ │
│  │  Messages in ──┬──────────────────────────────────────┐──────────► │ │
│  │                │                                      │            │ │
│  │                ▼                    ┌─────────────────┘            │ │
│  │  ┌─────────────────────────────────────────────────────┐           │ │
│  │  │ 9-Middleware Stack (Execution Order)               │           │ │
│  │  │                                                    │           │ │
│  │  │  1. DanglingToolCall    — Fix orphaned calls     │           │ │
│  │  │  2. Summarisation       — Compress at 180k tokens │           │ │
│  │  │  3. MessageTrimmer      — Hard limit at 800k chars│           │ │
│  │  │  4. SubagentLimit       — Cap parallel (default 3)│           │ │
│  │  │  5. LoopDetection       — Warn 3x, stop at 5     │           │ │
│  │  │  6. ToolErrorHandling   — Exception handling     │           │ │
│  │  │  7. Retry              — Exponential backoff     │           │ │
│  │  │  8. TokenBudget        — Per-query limits       │           │ │
│  │  │  9. Audit              — Log to JSONL           │           │ │
│  │  │                                                    │           │ │
│  │  │  Optional:                                        │           │ │
│  │  │  • Memory              — Cross-session (90-day)  │           │ │
│  │  │  • HITL                — Human approval gates   │           │ │
│  │  └─────────────────────────────────────────────────────┘           │ │
│  │                                                                      │ │
│  │  ┌──────────────────────────────┐  ┌──────────────────────────┐   │ │
│  │  │ LLM Selection                │  │ Tool Discovery           │   │ │
│  │  │ (llm_factory.py)             │  │ (tools.py)               │   │ │
│  │  │                              │  │                          │   │ │
│  │  │ • Anthropic (default)        │  │ • 5 static tools         │   │ │
│  │  │ • xAI (Grok)                 │  │ • Dynamic SAJHA tools    │   │ │
│  │  │ • Huggingface                │  │ • Tool timeout handling  │   │ │
│  │  │ • AWS Bedrock                │  │ • Output truncation      │   │ │
│  │  │                              │  │                          │   │ │
│  │  │ Configurable via:            │  │ Discovery via:           │   │ │
│  │  │ • .env (dev)                 │  │ • POST /api/mcp          │   │ │
│  │  │ • /api/super/llm-config (API)│  │ • Hot-reload (5s)       │   │ │
│  │  └──────────────────────────────┘  └──────────────────────────┘   │ │
│  │                                                                      │ │
│  │  ┌──────────────────────────────────────────────────────┐          │ │
│  │  │ Contextual Awareness (summariser.py)                │          │ │
│  │  │                                                      │          │ │
│  │  │ Count Tokens (weighted heuristic)                  │          │ │
│  │  │ └─ Text: 4 chars/token                            │          │ │
│  │  │ └─ JSON: 2.5 chars/token                          │          │ │
│  │  │ └─ Optional: tiktoken if enabled                  │          │ │
│  │  │                                                      │          │ │
│  │  │ At 180k tokens (90% of 200k window):              │          │ │
│  │  │ └─ Group messages into exchanges                  │          │ │
│  │  │ └─ Compress head exchanges via LLM                │          │ │
│  │  │ └─ Delete head messages (RemoveMessage)           │          │ │
│  │  │ └─ Append summary HumanMessage                    │          │ │
│  │  │ └─ Target: 36k tokens (18% of window)            │          │ │
│  │  │                                                      │          │ │
│  │  │ Events: Emit 'summary_occurred' via SSE           │          │ │
│  │  └──────────────────────────────────────────────────────┘          │ │
│  └──────────────────────────────────────────────────────────────────────┘ │
│                                  │                                        │
│                        ┌─────────┴──────────┐                             │
│                        │                    │                             │
│                    Static Tools        Dynamic Tools                      │
│                    (5 tools)           (121 from SAJHA)                   │
│                                                                            │
│                    • read_file         • iris_ccr                         │
│                    • list_files        • duckdb                           │
│                    • python_execute    • sqlselect                        │
│                    • call_code_tool    • msdoc                           │
│                    • task() [sub-agent]• edgar                            │
│                                        • outlook (cloud)                  │
│                                        • teams (cloud)                    │
│                                        • jira (cloud)                     │
│                                        • ... 112 more                     │
└────────────────────────────────────────────┬────────────────────────────────┘
                                             │ HTTP POST
                                             │ /api/tools/execute
                                             │ (port 3002)
                                             ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│                 SAJHA MCP Server (Flask, sajhamcpserver/)                    │
│                                                                              │
│  • Hot-reload every 5 seconds                                              │
│  • Tool discovery endpoint: POST /api/mcp                                  │
│  • Tool execution endpoint: POST /api/tools/execute                        │
│  • Authentication: Header "Authorization: key"                             │
│  • Worker-scoped data isolation                                            │
│  • 121 domain-specific tools across 41 modules                             │
│                                                                              │
│  ┌────────────────────────────────────────────────────────────────────┐   │
│  │ Configuration Layer (sajhamcpserver/config/)                       │   │
│  │                                                                    │   │
│  │ • application.properties    — Data paths, feature flags          │   │
│  │ • server.properties         — Port (3002), hot-reload (5s)       │   │
│  │ • workers.json              — Worker definitions (13 workers)    │   │
│  │ • users.json                — User accounts (17 users)           │   │
│  │ • apikeys.json              — API keys with rate limits (4 keys) │   │
│  │ • llm_config.json           — LLM provider settings (hot-swap)   │   │
│  │ • tools/                    — 121 tool definitions (JSON)        │   │
│  │   ├── iris_ccr_tools.json (enables IRIS)                        │   │
│  │   ├── duckdb_olap_tools.json (enables DuckDB)                   │   │
│  │   ├── outlook_tools.json (enables Outlook)                      │   │
│  │   ├── teams_tools.json (enables Teams)                          │   │
│  │   ├── jira_tools.json (enables Jira)                            │   │
│  │   └── ... 116 more                                               │   │
│  └────────────────────────────────────────────────────────────────────┘   │
│                                                                              │
│  ┌────────────────────────────────────────────────────────────────────┐   │
│  │ Tool Implementation Layer (sajhamcpserver/sajha/tools/impl/)      │   │
│  │                                                                    │   │
│  │ 41 Python modules, each implementing 1-10 tools:                 │   │
│  │                                                                    │   │
│  │ Domain Tools (On-Premises, Keep All):                            │   │
│  │   ✅ iris_ccr_tools.py           — IRIS CCR analytics           │   │
│  │   ✅ duckdb_olap_tools.py        — DuckDB SQL engine            │   │
│  │   ✅ sqlselect_tool.py           — Database queries             │   │
│  │   ✅ msdoc_tools.py              — Word/Excel read             │   │
│  │   ✅ python_executor.py          — Sandboxed Python            │   │
│  │   ✅ operational_tools.py        — File operations             │   │
│  │   ✅ edgar_tools.py              — SEC EDGAR access            │   │
│  │   ✅ yahoo_finance_tool.py       — Stock data                  │   │
│  │   ✅ visualisation_tools.py      — Plotly charts               │   │
│  │   ✅ data_transform_tools.py     — Data export                 │   │
│  │   ✅ workflow_tools.py           — Workflow execution          │   │
│  │   ✅ bm25_search_tool.py         — Full-text search            │   │
│  │                                                                    │   │
│  │ Cloud Tools (External, Disable in Phase 1):                      │   │
│  │   🔴 outlook_tools.py           — Outlook email (requires 365)  │   │
│  │   🔴 teams_tools.py             — Teams messaging (requires 365)│   │
│  │   🔴 sharepoint_tools.py        — SharePoint (requires 365)     │   │
│  │   🔴 confluence_tools.py        — Confluence (requires Cloud)   │   │
│  │   🔴 jira_tools.py              — Jira (requires Cloud)         │   │
│  │   🔴 powerbi_tools.py           — Power BI (requires Cloud)     │   │
│  │   🔴 tavily_*.py                — Web search (requires API)     │   │
│  │                                                                    │   │
│  │ Total: 76 domain ✅ + 45 cloud 🔴 = 121 tools                  │   │
│  └────────────────────────────────────────────────────────────────────┘   │
│                                                                              │
│  ┌────────────────────────────────────────────────────────────────────┐   │
│  │ Data & Storage Layer (sajhamcpserver/data/)                       │   │
│  │                                                                    │   │
│  │ ./workers/w-market-risk/                  [Worker-Scoped]       │   │
│  │   ├── domain_data/                                               │   │
│  │   │   ├── iris/iris_combined.csv          (IRIS data)          │   │
│  │   │   ├── duckdb/                         (DuckDB files)        │   │
│  │   │   ├── sqlselect/                      (SQL data)            │   │
│  │   │   ├── msdocs/                         (Uploaded Word/Excel) │   │
│  │   │   ├── counterparties/                 (Counterparty data)   │   │
│  │   │   └── osfi/                           (Regulatory docs)     │   │
│  │   ├── workflows/verified/                 (Approved workflows)  │   │
│  │   ├── templates/                          (Document templates)  │   │
│  │   ├── my_data/                            (Per-user files)      │   │
│  │   └── (additional user-scoped folders)                         │   │
│  │                                                                    │   │
│  │ ./common/                                 [Shared Data]         │   │
│  │ ./checkpoints.db                          (LangGraph state)     │   │
│  │ ./audit/tool_calls.jsonl                  (Audit logs)         │   │
│  └────────────────────────────────────────────────────────────────────┘   │
└──────────────────────────────────────────────────────────────────────────────┘
                                   │
                    ┌──────────────┴──────────────┐
                    │                             │
                    ▼                             ▼
         ┌─────────────────────┐      ┌──────────────────────┐
         │ External Services   │      │ Local Data Sources   │
         │ (Cloud, if enabled) │      │ (Always Available)   │
         │                     │      │                      │
         │ • Outlook 365       │      │ • CSV files          │
         │ • Teams             │      │ • DuckDB/Parquet     │
         │ • Jira Cloud        │      │ • Database (SQL)     │
         │ • Confluence        │      │ • Word/Excel docs    │
         │ • Power BI          │      │ • Python env         │
         │ • Tavily Search     │      │ • SEC EDGAR (public) │
         │ • SharePoint Online │      │ • Yahoo Finance      │
         │                     │      │ • Local workflows    │
         └─────────────────────┘      └──────────────────────┘
```

---

## 🔄 Request Flow & Data Path

### Typical Chat Request

```
User Types: "What's the risk profile for ABC Corp?"
         │
         ▼
Browser: POST /api/agent/run
         ├─ Headers: Authorization: Bearer <JWT>
         ├─ Body: {worker_id, query, thread_id}
         └─ Response: Server-Sent Events (SSE)
         │
         ▼
agent_server.py (FastAPI)
         ├─ Validate JWT
         ├─ Load worker config (from workers.json)
         ├─ Look up thread (from checkpoints.db)
         └─ Create agent context
         │
         ▼
LangGraph Agent (agent/agent.py)
         ├─ Initialize with 9 middlewares
         ├─ Check context size (count_tokens)
         │   └─ If >= 180k: compress via summariser.py
         ├─ Invoke LLM with system prompt
         └─ LLM suggests tool: "Use IRIS CCR tool"
         │
         ▼
Tools Discovery (agent/tools.py)
         ├─ Tool not in cache → POST /api/mcp to SAJHA
         ├─ SAJHA returns 121 tool definitions
         ├─ Cache for 300s (or hot-reload finds new ones)
         └─ Select IRIS CCR tool from list
         │
         ▼
Tool Execution (agent/tools.py)
         ├─ Tool input: {counterparty: "ABC Corp"}
         ├─ POST /api/tools/execute to SAJHA
         │   └─ Headers: Authorization: sja_full_access_admin
         ├─ SAJHA routes to iris_ccr_tools.py module
         └─ Module executes: pandas.read_csv + analytics
         │
         ▼
SAJHA Tool Implementation (sajhamcpserver/)
         ├─ iris_ccr_tools.py (10 tools, 200 lines)
         │   ├─ Load: data/workers/w-market-risk/domain_data/iris/iris_combined.csv
         │   ├─ Query: Where counterparty == "ABC Corp"
         │   └─ Compute: VaR, CCR, concentration metrics
         └─ Return: {result: "...", duration_ms: 245}
         │
         ▼
Agent Processes Result
         ├─ Middleware 6 (ToolErrorHandling): No error
         ├─ Middleware 7 (Retry): No retry needed
         ├─ Add to message list (LangGraph)
         ├─ Send SSE event: {event: "tool_end", tool: "iris_ccr_..."}
         ├─ Check size again (still under 180k)
         └─ LLM generates response
         │
         ▼
Response Streaming (agent_server.py)
         ├─ SSE event: {event: "text", content: "Based on IRIS data..."}
         ├─ SSE event: {event: "usage", input_tokens: 1250, output_tokens: 340}
         ├─ SSE event: {event: "context_gauge", tokens_used: 3450, tokens_max: 200000}
         ├─ Middleware 9 (Audit): Log to data/audit/tool_calls.jsonl
         └─ Final: SSE "[DONE]"
         │
         ▼
Browser receives streaming response
         ├─ Render text as it arrives
         ├─ Update token gauge
         ├─ Display tool execution metadata
         └─ Save message to conversation thread
```

---

## 🔀 Context Compression Flow (At 180k Tokens)

```
Current State:
  Messages: [system, human_1, ai_1, tool_1, ai_2, human_2, ai_3, ...]
  Total: 5400 tokens → approaching 180k limit after next LLM call
                       
           │
           ▼
Summariser Middleware Detects Trigger (>180k)
           │
           ├─ Count tokens: text+JSON weighted heuristic
           ├─ Group messages into exchanges:
           │  ├─ Exchange 1: [human_1, ai_1, tool_1, ai_2]
           │  ├─ Exchange 2: [human_2, ai_3, tool_2, ai_4]
           │  ├─ ...
           │  └─ Tail (protected): [human_N-1, ai_N]  ← Keep last 2 exchanges
           │
           └─ Identify head messages for compression:
              └─ All except last CONTEXT_TAIL_MESSAGES (2) exchanges
                 
           │
           ▼
LLM Summarization (via Anthropic Claude)
           │
           ├─ Input: [system_prompt, 15 earlier exchanges truncated to ~15k tokens]
           ├─ Prompt: "Summarize this conversation efficiently in ~400 tokens"
           └─ Output: Summary HumanMessage (~400 tokens)
                     
           │
           ▼
Message Deletion & Replacement
           │
           ├─ Create RemoveMessage(id=msg_id) for each head message
           │  └─ LangGraph add_messages reducer deletes them
           ├─ Add new HumanMessage: "[CONTEXT SUMMARY — 15 exchanges]\n{summary}"
           └─ Final state: [system, summary_human, exchange_N-1, exchange_N]
                     
           │
           ▼
Token Count After Compression
           │
           Before: 5400 tokens
           After:  3671 tokens  ← Reduced by ~32%
           Status: Now have room for ~116k more tokens before next compression
                     
           │
           ▼
Resume LLM Inference
           └─ Agent continues with compressed context
              └─ User never knows compression happened
                 └─ But SSE emits: {event: "summary_occurred", ...}
```

---

## 🛠️ Tool Execution Sequence Diagram

```
Agent                        SAJHA (Flask)             Tool Module
  │                              │                          │
  ├──────────────────────────────>                          │
  │ POST /api/mcp               │                          │
  │ (discovery)                 │                          │
  │                             ├──────────────────────────>│
  │                             │ Load iris_ccr_tools.py   │
  │                             │                          │
  │<──────────────────────────────                         │
  │ [{name: "iris_ccr_get_...                              │
  │   schema: {...}, ...}]                                │
  │                                                        │
  ├──────────────────────────────>                         │
  │ POST /api/tools/execute      │                         │
  │ {                            │                         │
  │   "tool": "iris_ccr_...",   │                         │
  │   "arguments": {             │                         │
  │     "counterparty": "ABC"   │                         │
  │   }                          │                         │
  │ }                            │                         │
  │ [Auth: key]                  │                         │
  │                              ├──────────────────────────>
  │                              │ Validate API key (apikeys.json)
  │                              │
  │                              ├──────────────────────────>
  │                              │ Load IRIS CSV from
  │                              │ data/workers/w-market-risk/
  │                              │   domain_data/iris/
  │                              │
  │                              ├──────────────────────────>
  │                              │ Filter: counterparty="ABC"
  │                              │ Calculate: VaR, CCR, etc.
  │                              │
  │<──────────────────────────────
  │ {
  │   "result": "...metrics...",
  │   "duration_ms": 245,
  │   "metadata": {...}
  │ }
  │
  └─ Process in middleware stack
     ├─ ToolErrorHandling: OK
     ├─ Retry: OK
     ├─ Audit: Log event
     └─ Add to messages
```

---

## 📊 Data Flow: Worker-Scoped Isolation

```
Multiple Workers with Isolated Data:

┌─────────────────────────────────────────────────────────────────┐
│ Agent Server (agent_server.py)                                  │
│                                                                 │
│ Request: POST /api/agent/run                                  │
│ Headers: Authorization: Bearer <JWT with worker_id>           │
│ Body: {worker_id: "w-market-risk", query: "..."}             │
└──────────────────────┬──────────────────────────────────────────┘
                       │
              ┌────────┴────────┐
              │                 │
              ▼                 ▼
    ┌─────────────────┐  ┌──────────────────┐
    │ w-market-risk   │  │ w-treasury       │
    │                 │  │                  │
    │ System Prompt:  │  │ System Prompt:   │
    │ "You analyze    │  │ "You analyze     │
    │  credit risk"   │  │  treasury bonds" │
    │                 │  │                  │
    │ Enabled Tools:  │  │ Enabled Tools:   │
    │ • IRIS CCR      │  │ • DuckDB OLAP    │
    │ • Python        │  │ • Python         │
    │ • Outlook       │  │ • SEC EDGAR      │
    │ • Jira          │  │ • Yahoo Finance  │
    │                 │  │                  │
    │ Data Root:      │  │ Data Root:       │
    │ ./workers/      │  │ ./workers/       │
    │  w-market-risk/ │  │  w-treasury/     │
    │  domain_data/   │  │  domain_data/    │
    │  ├── iris/      │  │  ├── duckdb/     │
    │  ├── duckdb/    │  │  └── ...         │
    │  └── msdocs/    │  │                  │
    │                 │  │ My Data:         │
    │ My Data:        │  │ ./workers/       │
    │ ./workers/      │  │  w-treasury/     │
    │  w-market-risk/ │  │  my_data/        │
    │  my_data/       │  │  {user_id}/      │
    │  {user_id}/     │  │                  │
    │                 │  │ Checkpoints:     │
    │ Checkpoints:    │  │ Separate thread  │
    │ Conversation    │  │ state per worker │
    │ state in        │  │                  │
    │ sqlite DB       │  │                  │
    │ (per thread)    │  │                  │
    └─────────────────┘  └──────────────────┘
    
User "john@risk" can only:
  ✅ See w-market-risk data
  ❌ See w-treasury data
  
User "alice@treasury" can only:
  ❌ See w-market-risk data
  ✅ See w-treasury data
```

---

## 🔐 Security Layers

```
Request                          │  Security Check
──────────────────────────────────┼─────────────────────────────────
HTTP POST /api/agent/run          │  ✅ TLS/HTTPS (in production)
  ├─ Authorization: Bearer JWT    │  ✅ JWT signature verification
  ├─ worker_id: "w-market-risk"  │  ✅ User has access to worker?
  └─ query: "..."                │  ✅ Rate limit (10 req/min per user)
                                  │
                                  ▼
LangGraph Agent                    │  ✅ Tool allowlist (per worker)
  ├─ Tool: iris_ccr_get_vcr       │  ✅ Tool timeout (30s default)
  └─ Args: {counterparty: "ABC"}  │  ✅ Output truncation (12k chars)
                                  │
                                  ▼
SAJHA Tool Execution              │  ✅ API key validation
POST /api/tools/execute           │  ✅ Tool rate limit (per key)
  ├─ Authorization: key           │  ✅ Worker data path verification
  └─ {tool, arguments}            │     (startswith() check)
                                  │
                                  ▼
Tool Implementation               │  ✅ File path whitelist
(iris_ccr_tools.py)              │  ✅ SQL injection prevention
  └─ Access:                      │  ✅ Sensitive field redaction
     domain_data/iris/            │     (in audit logs)
                                  │
                                  ▼
Audit Logging                     │  ✅ All events logged to JSONL
data/audit/tool_calls.jsonl      │  ✅ PII & secrets redacted
```

---

## 🚀 Phase Progression Path

```
Current State (Phase 0: Extraction Complete)
│
├─ Code is isolated in mcp_onprem/mcp_agent/
├─ 121 tools available (76 domain + 45 cloud)
├─ Cloud tools identified & ready to disable
├─ All documentation complete
└─ Status: READY FOR NEXT PHASE

             │
             ▼

Phase 1: Cloud Decoupling (30 min, Safe)
│
├─ Disable 45 cloud tools in config/tools/
│   ├─ outlook_tools.json → "enabled": false
│   ├─ teams_tools.json → "enabled": false
│   ├─ jira_tools.json → "enabled": false
│   └─ ... 4 more files
├─ Verify 76 domain tools remain
├─ Remove cloud credentials from .env
├─ Test agent with domain tools only
└─ Status: CLOUD-FREE, READY FOR PHASE 2

             │
             ▼

Phase 2: v5.0.0 Compatibility (4-5 days, Major)
│
├─ Fix 7 gaps between v2.9.8 and v5.0.0:
│   ├─ Gap 1: Auth header (Authorization → X-API-Key)
│   ├─ Gap 2: Tools (121 → 497, different tools)
│   ├─ Gap 3: Config format (properties → YAML)
│   ├─ Gap 4: Workers → Tenants
│   ├─ Gap 5: Tool endpoint format
│   ├─ Gap 6: Storage (JSON → PostgreSQL)
│   └─ Gap 7: Remove direct imports
├─ Comprehensive testing
├─ Performance validation
└─ Status: COMPATIBLE WITH v5.0.0

             │
             ▼

Production Deployment
│
├─ Reset testing token values to production
├─ Enable HTTPS
├─ Configure PostgreSQL
├─ Load testing
├─ Backup & recovery procedures
└─ Status: PRODUCTION-READY
```

---

## 📖 Documentation Map

| Document | Focus | Audience |
|----------|-------|----------|
| **QUICKSTART.md** | Get running in 5 minutes | New users, developers |
| **AGENT_SETUP.md** | Detailed setup + phases | DevOps, engineers |
| **INDEX.md** | File inventory + gaps | Architects, project managers |
| **ARCHITECTURE.md** | System design overview | Architects, reviewers |
| **MIGRATION_SUMMARY.md** | Extraction statistics | Project tracking |
| **CLAUDE.md** | Original developer ref | Advanced developers |

---

**Extracted:** 2026-06-02  
**Status:** Architecture documented, ready for execution
