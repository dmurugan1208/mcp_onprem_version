# Phase 1: Cloud Tools Decoupling Reference

**Status:** Ready to execute (30 minutes, safe, reversible)  
**Location:** `C:\Users\Durga Vishalini\mcp_onprem\mcp_agent`  
**Last Updated:** 2026-06-02

---

## 📋 Executive Summary

**Goal:** Disable 45 cloud-dependent tools, leaving 76 on-premises tools operational.

**What changes:**
- 7 tool configuration files → set `"enabled": false`
- `.env` → remove cloud service credentials
- Agent code → NO CHANGES (tool discovery auto-filters)

**Time:** 30 minutes  
**Risk:** LOW (100% reversible)  
**Effort:** 1 PowerShell script or manual JSON editing

---

## 🔴 45 Cloud Tools to Disable

### by Service Provider

| Service | Count | Tools | Config File |
|---------|-------|-------|-------------|
| **Microsoft 365** | 18 | Outlook (6) + Teams (6) + SharePoint (6) | 3 files |
| **Atlassian Cloud** | 12 | Confluence (5) + Jira (7) | 2 files |
| **Tavily API** | 3+ | Web/news/domain search (Tavily-native) | 1+ files |
| **Microsoft Cloud** | 6 | Power BI (6 tools) | 1 file |
| **Other APIs** | 6+ | Various integrations | Various |
| **TOTAL** | **45+** | — | **7+ files** |

---

## 📁 Files to Modify (7 Total)

### 1. **outlook_tools.json** (6 tools)

**Location:** `sajhamcpserver/config/tools/outlook_tools.json`

**Current tools (disable all):**
- outlook_read_emails
- outlook_read_email_details
- outlook_send_email
- outlook_search_emails
- outlook_create_event
- outlook_get_calendar

**Change:** Find the tool definition JSON and set:
```json
{
  "name": "outlook_read_emails",
  "enabled": false,    // ← CHANGE THIS
  "description": "...",
  ...
}
```

**Reason:** Requires Microsoft 365 credentials (AZURE_TENANT_ID, AZURE_CLIENT_ID, etc.)

---

### 2. **teams_tools.json** (6 tools)

**Location:** `sajhamcpserver/config/tools/teams_tools.json`

**Current tools (disable all):**
- teams_list_channels
- teams_read_messages
- teams_send_message
- teams_list_files
- teams_get_meeting_details
- teams_create_meeting

**Change:** Set `"enabled": false` for each tool

**Reason:** Requires Microsoft 365 credentials

---

### 3. **sharepoint_tools.json** (6 tools)

**Location:** `sajhamcpserver/config/tools/sharepoint_tools.json`

**Current tools (disable all):**
- sharepoint_list_sites
- sharepoint_list_documents
- sharepoint_search_documents
- sharepoint_upload_document
- sharepoint_download_document
- sharepoint_get_document_metadata

**Change:** Set `"enabled": false` for each tool

**Reason:** Requires Microsoft 365 credentials

---

### 4. **confluence_tools.json** (5 tools)

**Location:** `sajhamcpserver/config/tools/confluence_tools.json`

**Current tools (disable all):**
- confluence_list_spaces
- confluence_get_page_content
- confluence_search_pages
- confluence_create_page
- confluence_update_page

**Change:** Set `"enabled": false` for each tool

**Reason:** Requires Atlassian Cloud credentials (API token, host URL)

---

### 5. **jira_tools.json** (7 tools)

**Location:** `sajhamcpserver/config/tools/jira_tools.json`

**Current tools (disable all):**
- jira_list_projects
- jira_list_sprints
- jira_create_issue
- jira_update_issue
- jira_get_issue
- jira_search_issues
- jira_add_comment

**Change:** Set `"enabled": false` for each tool

**Reason:** Requires Atlassian Cloud credentials (API token, host URL)

---

### 6. **powerbi_tools.json** (6 tools)

**Location:** `sajhamcpserver/config/tools/powerbi_tools.json`

**Current tools (disable all):**
- powerbi_list_workspaces
- powerbi_list_datasets
- powerbi_list_reports
- powerbi_refresh_dataset
- powerbi_get_report_data
- powerbi_publish_report

**Change:** Set `"enabled": false` for each tool

**Reason:** Requires Microsoft Cloud credentials (Power BI tenant, service principal)

---

### 7. **tavily_*.json** (3+ files with multiple tools)

**Location:** `sajhamcpserver/config/tools/tavily*.json` (multiple files)

**Files to modify:**
- `tavily_tool_refactored.json` (4 tools: web, research, news, domain search)
- `tavily_ir_tool.json` (9 tools: IR data extraction)
- `tavily_yahoo_finance_tool.json` — **⚠️ NOTE: Don't disable this one yet**

**Current tools (disable tavily* but NOT yahoo):**
- tavily_web_search
- tavily_research_search
- tavily_news_search
- tavily_domain_search
- tavily_ir_* (9 tools)

**Change:** Set `"enabled": false` for tavily_* files only

**Reason:** Requires Tavily API key

**WARNING:** `tavily_yahoo_finance_tool.json` uses Yahoo Finance (PUBLIC API, NOT cloud-dependent), so we MAY want to keep it enabled if you need stock data. Decide based on your needs.

---

## ✅ Tools to KEEP Enabled (76 Domain)

### On-Premises Tools (No External Dependencies)

```
✅ Domain Tools (76 total) — KEEP ENABLED

Counterparty Risk (9 tools)
  ✅ iris_ccr_get_vcr
  ✅ iris_ccr_get_cva
  ✅ iris_ccr_get_ccr
  ✅ iris_ccr_get_netting_benefit
  ✅ iris_ccr_get_concentration_analysis
  ✅ iris_ccr_get_peer_comparison
  ✅ iris_ccr_search_counterparty
  ✅ iris_ccr_get_historical_rating_changes
  ✅ iris_ccr_export_analysis

Data Analytics (13 tools)
  ✅ duckdb_* (10 tools) — DuckDB SQL engine
  ✅ sqlselect_* (6 tools) — Database query

Document Processing (10 tools)
  ✅ msdoc_read_docx
  ✅ msdoc_read_xlsx
  ✅ msdoc_search_document
  ✅ msdoc_extract_text
  ✅ msdoc_* (6 more)

Python Execution (2 tools)
  ✅ python_execute — Sandboxed Python (pandas, numpy, plotly, etc.)
  ✅ python_execution — Alternative Python tool

SEC EDGAR (10 tools)
  ✅ edgar_get_10k
  ✅ edgar_get_10q
  ✅ edgar_get_20f
  ✅ edgar_search_filings
  ✅ edgar_* (6 more) — Public SEC data

Market Data (4 tools)
  ✅ yahoo_stock_quote
  ✅ yahoo_historical_prices
  ✅ yahoo_symbol_search
  (✅ yahoofinance_* if Tavily Yahoo still enabled)

Operations (7 tools)
  ✅ operational_read_file
  ✅ operational_write_file
  ✅ operational_search_files
  ✅ operational_pdf_read
  ✅ operational_markdown_to_docx
  ✅ operational_* (2 more)

Visualization (1 tool)
  ✅ generate_chart — Plotly HTML charts

Workflow (2 tools)
  ✅ workflow_discover
  ✅ workflow_execute

Search (1 tool)
  ✅ bm25_search — Full-text document search

Data Transform (3 tools)
  ✅ export_data
  ✅ transform_data
  ✅ read_parquet
```

**Total: 76 tools remain operational**

---

## 🛠️ How to Execute Phase 1

### Method 1: PowerShell Script (Automated, Recommended)

```powershell
# Run from C:\Users\Durga Vishalini\mcp_onprem\mcp_agent\

$cloud_tool_files = @(
    "sajhamcpserver/config/tools/outlook_tools.json",
    "sajhamcpserver/config/tools/teams_tools.json",
    "sajhamcpserver/config/tools/sharepoint_tools.json",
    "sajhamcpserver/config/tools/confluence_tools.json",
    "sajhamcpserver/config/tools/jira_tools.json",
    "sajhamcpserver/config/tools/powerbi_tools.json"
)

# Disable these exact 6 tools
foreach ($file in $cloud_tool_files) {
    if (Test-Path $file) {
        $json = Get-Content $file -Raw | ConvertFrom-Json
        
        # Iterate through each tool in the file
        for ($i = 0; $i -lt $json.tools.Count; $i++) {
            $json.tools[$i].enabled = $false
        }
        
        # Also handle if tools is directly in root
        if ($json.enabled) {
            $json.enabled = $false
        }
        
        # Write back to file
        $json | ConvertTo-Json -Depth 10 | Set-Content $file
        Write-Host "✅ Disabled: $file"
    } else {
        Write-Host "❌ Not found: $file"
    }
}

# Also disable tavily files
Get-ChildItem "sajhamcpserver/config/tools/tavily*.json" -Exclude "*yahoo*" | ForEach-Object {
    $json = Get-Content $_.FullName -Raw | ConvertFrom-Json
    
    for ($i = 0; $i -lt $json.tools.Count; $i++) {
        $json.tools[$i].enabled = $false
    }
    
    $json | ConvertTo-Json -Depth 10 | Set-Content $_.FullName
    Write-Host "✅ Disabled: $($_.Name)"
}

Write-Host ""
Write-Host "✨ Phase 1 Complete: 45 cloud tools disabled"
```

### Method 2: Manual JSON Editing

For each file above:
1. Open in VS Code or text editor
2. Search for `"enabled": true`
3. Replace with `"enabled": false`
4. Save file

**Example (outlook_tools.json):**
```json
{
  "tools": [
    {
      "name": "outlook_read_emails",
      "description": "Read recent emails",
      "enabled": true   // ← Change to false
      ...
    },
    {
      "name": "outlook_send_email",
      "enabled": true   // ← Change to false
      ...
    }
  ]
}
```

---

## 🔧 Environment Variable Cleanup

### Step 1: Update .env

Remove these lines (if they exist):

```bash
# Microsoft 365 / Azure
AZURE_TENANT_ID=...
AZURE_CLIENT_ID=...
AZURE_CLIENT_SECRET=...

# Atlassian
ATLASSIAN_API_TOKEN=...
JIRA_API_URL=...
CONFLUENCE_API_URL=...

# Tavily Search
TAVILY_API_KEY=...

# Power BI
POWERBI_TENANT_ID=...
POWERBI_CLIENT_ID=...
POWERBI_CLIENT_SECRET=...

# Outlook/Teams
O365_TENANT=...
SHAREPOINT_SITE_URL=...
```

### Step 2: Verify Required Vars Still Present

These should remain:
```bash
ANTHROPIC_API_KEY=...        # Still needed for LLM
SAJHA_BASE_URL=...           # Still needed for SAJHA communication
SAJHA_API_KEY=...            # Still needed for SAJHA auth
FRED_API_KEY=...             # Keep if using SEC EDGAR
CONTEXT_TRIGGER_TOKENS=...   # Still needed for summarisation
```

---

## ✅ Verification Checklist

After disabling cloud tools, verify they're gone:

### 1. Restart SAJHA
```bash
# Kill previous process
# Then restart:
cd sajhamcpserver
python run_server.py

# Wait 10 seconds for hot-reload
# (SAJHA checks config every 5s)
```

### 2. Check Tool Discovery
```bash
# Via curl:
curl http://127.0.0.1:3002/api/mcp | jq '.tools | length'
# Expected: ~76 (was 121)

# Check NO cloud tools:
curl http://127.0.0.1:3002/api/mcp | jq '.tools[] | select(.name | startswith("outlook_") or startswith("teams_") or startswith("jira_")) | .name'
# Expected: (no output = success)
```

### 3. Check Agent Discovery
```bash
# Restart agent:
# Kill previous
# Then:
uvicorn agent_server:app --port 8000 --reload

# Via API:
curl http://localhost:8000/api/mcp/tools | jq '.tools | length'
# Expected: ~76

# Verify no cloud tools:
curl http://localhost:8000/api/mcp/tools | grep -E "outlook|teams|jira|confluence|sharepoint|power_bi|tavily"
# Expected: (no output = success)
```

### 4. Manual Test in UI
```
1. Open http://localhost:8000/admin.html
2. Navigate to "Tools" section
3. Search for "outlook" → Should NOT appear
4. Search for "iris" → SHOULD appear
5. Count tools → Should be ~76
```

---

## 🔄 Rollback (If Needed)

To **re-enable** cloud tools:

### Option 1: Restore from Backup
```bash
# If you kept the original repo:
git checkout sajhamcpserver/config/tools/*.json
# Restart SAJHA
```

### Option 2: Manual Re-enable
```powershell
# In each cloud tool file, change:
# "enabled": false
# back to:
# "enabled": true

# Then restart SAJHA
```

**100% reversible** — no data loss, no schema changes

---

## 📊 Expected Results After Phase 1

| Metric | Before | After |
|--------|--------|-------|
| Total Tools | 121 | 76 |
| Cloud Tools | 45 | 0 |
| Domain Tools | 76 | 76 |
| Cloud Dependencies | 7 services | 0 |
| Credentials Needed | ~20 keys | ~2 keys (Anthropic + SAJHA) |
| Agent Code Changes | — | NONE |
| Configuration Changes | — | 7 JSON files |
| Frontend Changes | — | NONE |
| Database Changes | — | NONE |

---

## ⏱️ Timeline

| Step | Time | Action |
|------|------|--------|
| 1 | 2 min | Read this file |
| 2 | 3 min | Run PowerShell script OR manually edit 7 JSON files |
| 3 | 2 min | Update .env (remove cloud credentials) |
| 4 | 5 min | Restart SAJHA + Agent |
| 5 | 5 min | Verify via curl + admin UI |
| 6 | 2 min | Test one domain tool (e.g., IRIS) |
| 7 | 4 min | Document changes |
| **Total** | **~30 min** | **Phase 1 Complete** |

---

## 🎯 Success Criteria

✅ Phase 1 is successful when:

1. **Configuration Updated:** 7 JSON files have `"enabled": false` for cloud tools
2. **Environment Clean:** .env has no cloud service credentials
3. **Tool Count:** SAJHA reports 76 tools (down from 121)
4. **No Cloud Tools:** API /api/mcp returns NO tools starting with outlook_, teams_, jira_, etc.
5. **Domain Tools Work:** Can successfully call at least one domain tool (e.g., iris_ccr_get_vcr)
6. **Agent Runs:** Chat UI works, can query domain tools
7. **No Errors:** Logs show no "missing credential" or "service not found" errors for cloud tools

---

## 📝 Documentation

After completing Phase 1:
1. Document which tools were disabled
2. Document which credentials were removed from .env
3. Test date and results
4. Create rollback procedure (if needed)
5. Share results with team

---

## 🚀 Next Steps

**After Phase 1 succeeds:**

### Option A: Stop Here
- Keep using embedded SAJHA v2.9.8
- 76 on-premises tools fully functional
- No further migration needed
- **Status:** Production-ready (with token reset)

### Option B: Proceed to Phase 2
- Migrate to SAJHA v5.0.0
- Gain 497 generic market data tools
- Lose 121 domain tools (or add as plugins)
- **Estimated effort:** 4-5 days
- **See:** AGENT_SETUP.md for Phase 2 details

---

**Phase 1 Ready:** ✅  
**Estimated Time:** 30 minutes  
**Risk Level:** LOW  
**Reversibility:** 100%

Start when ready!
