# WorkerRepository Migration Plan

**Status:** Planning  
**Scope:** Move WorkerRepository from sajhamcpserver/ to agent/  
**Impact:** Make agent independent of sajha.worker_repository  
**Effort:** 2-3 hours  
**Risk:** LOW (well-isolated changes, drop-in replacement)

---

## 📋 Current State

### Location of WorkerRepository
```
sajhamcpserver/sajha/worker_repository.py
├── WorkerRepository (JSON-based, 50 lines)
│   ├── __init__(config_path)
│   ├── reload()
│   ├── find(worker_id)
│   ├── list()
│   └── find_by_user(user_id)
└── PostgresWorkerRepository (Postgres-backed, 180 lines)
    ├── __init__()
    ├── _connect()
    ├── _ensure_table_and_seed()
    ├── _seed_from_json(cur)
    ├── _row_to_dict(row)
    ├── find(worker_id)
    ├── list()
    ├── find_by_user(user_id)
    └── reload()
```

### Current Usage in agent_server.py

**Lines 42-61:** Imports and singleton initialization
```python
from sajha.worker_repository import WorkerRepository as _WorkerRepository, PostgresWorkerRepository as _PGWorkerRepository

# Singleton
if os.getenv('DATABASE_URL'):
    _worker_repo = _PGWorkerRepository()
else:
    _worker_repo = _WorkerRepository(config_path=str(_SAJHA_WORKERS_FILE))
```

**Lines 183-191:** Usage in get_workers()
```python
def get_workers():
    """Return all workers via WorkerRepository"""
    workers = _worker_repo.list()
    return workers
```

**Line 255+:** Usage in find_worker(worker_id)
```python
def find_worker(worker_id):
    """Find a worker by ID via WorkerRepository"""
    return _worker_repo.find(worker_id)
```

---

## 🎯 What We're Moving

### Core Repository Logic
- ✅ WorkerRepository class (JSON-based, for now)
- ✅ PostgresWorkerRepository class (for future)
- ✅ Path resolution logic
- ✅ Thread-safe caching with locks
- ✅ Fallback error handling

### Data Source
- ✅ `sajhamcpserver/config/workers.json` (stays where it is)
- ✅ Path will be resolved relative to agent location

---

## 🏗️ Architecture: Before vs After

### BEFORE (Current)
```
agent_server.py (FastAPI)
    ↓ imports
sajhamcpserver/sajha/worker_repository.py
    ↓ reads
sajhamcpserver/config/workers.json
```

### AFTER (Proposed)
```
agent_server.py (FastAPI)
    ↓ imports
agent/repository.py  ← NEW
    ↓ reads
sajhamcpserver/config/workers.json
```

**Benefits:**
- ✅ Agent is independent of SAJHA internals
- ✅ Easier to migrate to database later (just change one file)
- ✅ No circular dependencies
- ✅ Cleaner separation of concerns

---

## 📝 Implementation Steps

### Step 1: Create agent/repository.py
Copy WorkerRepository + PostgresWorkerRepository classes to `agent/repository.py`

**Changes needed:**
1. Path resolution: Update to find workers.json relative to agent location
   ```python
   # OLD (in sajha):
   base = os.path.dirname(os.path.abspath(__file__))  # sajhamcpserver/sajha/
   config_path = os.path.join(base, '..', 'config', 'workers.json')  # ../../config/workers.json
   
   # NEW (in agent):
   base = os.path.dirname(os.path.abspath(__file__))  # agent/
   config_path = os.path.join(base, '..', 'sajhamcpserver', 'config', 'workers.json')  # ../sajhamcpserver/config/workers.json
   ```

2. Default path in constructor:
   ```python
   def __init__(self, config_path: str = None):
       if config_path is None:
           # Find workers.json relative to agent/ directory
           agent_dir = os.path.dirname(os.path.abspath(__file__))
           config_path = os.path.join(agent_dir, '..', 'sajhamcpserver', 'config', 'workers.json')
   ```

### Step 2: Update agent_server.py Imports
**Old:**
```python
from sajha.worker_repository import WorkerRepository as _WorkerRepository, PostgresWorkerRepository as _PGWorkerRepository
```

**New:**
```python
from agent.repository import WorkerRepository as _WorkerRepository, PostgresWorkerRepository as _PGWorkerRepository
```

### Step 3: Remove SAJHA Imports from agent_server.py
**Remove these lines:**
```python
from sajha.tools.impl.fs_index import build_index, get_index  # Line 41
from sajha.worker_repository import ...  # Line 42
from sajha.storage import storage as _storage  # Line 43
```

**Keep only:**
```python
# Now that we're moving WorkerRepository to agent/, we don't need direct SAJHA imports
```

### Step 4: Update Imports in agent_server.py (Post-WorkerRepository)
After workers.json is moved to agent/, other imports may still reference SAJHA. Track what else needs moving:
- `from sajha.tools.impl.fs_index` → Might be needed for file indexing
- `from sajha.storage` → Might be needed for storage ops
- etc.

**For now:** Only move WorkerRepository. Leave others as-is (next phase).

### Step 5: Test
```bash
# Start agent
cd mcp_onprem/mcp_agent
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
uvicorn agent_server:app --port 8000 --reload

# Test worker endpoints
curl http://localhost:8000/api/super/workers
# Should return list of workers from sajhamcpserver/config/workers.json ✅
```

---

## 📊 Files to Modify

| File | Change | Lines | Risk |
|------|--------|-------|------|
| `agent/repository.py` | CREATE NEW | ~250 | LOW |
| `agent_server.py` | Update imports | 42 | LOW |
| `agent/__init__.py` | Add export (optional) | 1 | LOW |
| `sajhamcpserver/sajha/worker_repository.py` | Keep as-is (no deletion yet) | — | NONE |

---

## ✅ Success Criteria

- ✅ agent/repository.py exists and has both WorkerRepository + PostgresWorkerRepository
- ✅ agent_server.py imports from agent.repository (not sajha.worker_repository)
- ✅ Worker CRUD endpoints still work: GET /api/super/workers, GET /api/super/workers/{id}, etc.
- ✅ Login still works (requires worker lookup via find_by_user)
- ✅ No errors in logs about missing sajha.worker_repository
- ✅ All worker-scoped paths resolve correctly

---

## 🔄 Rollback Plan

If something breaks:
1. Revert agent_server.py imports back to sajha.worker_repository
2. Delete agent/repository.py
3. Restart agent

**Note:** Zero risk of data loss (workers.json stays untouched)

---

## 📈 Phase 2 (Future): Database Migration

Once WorkerRepository is in agent/:

```python
# Later, we can add UserRepository, WorkflowRepository, etc.
agent/repository.py
├── WorkerRepository (JSON now, PostgreSQL later)
├── UserRepository (JSON now, PostgreSQL later)
├── APIKeyRepository (JSON now, PostgreSQL later)
└── ...
```

This makes it much easier to migrate from JSON to PostgreSQL one class at a time.

---

## 🚀 Timeline

| Phase | Task | Time | Status |
|-------|------|------|--------|
| 1 | Create agent/repository.py | 30 min | Ready |
| 2 | Update agent_server.py imports | 10 min | Ready |
| 3 | Test worker endpoints | 15 min | Ready |
| 4 | Verify no side effects | 20 min | Ready |
| **Total** | **Move WorkerRepository to Agent** | **~1.5 hours** | **Ready to start** |

---

## 📌 Notes

- **Why not move users.json too?** Different structure, more complex. Do WorkerRepository first as a template.
- **Why keep PostgresWorkerRepository?** For future database migration. Keep code close to show the transition path.
- **Why not delete sajha/worker_repository.py?** Not yet. SAJHA might use it for its own purposes. Delete after confirming no internal dependencies.

---

**Ready to proceed with Step 1?** ✅
