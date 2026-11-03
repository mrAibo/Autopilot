window.STATE =
{
  "version": 2,
  "slug": "audit-fixes",
  "dir": "2026-11-03-audit-fixes--wip",
  "title": "Исправления по аудиту Autopilot 2026-11-03",
  "mode": "semi",
  "depth": "normal",
  "tier": "T1",
  "strictRouting": true,
  "sequentialHost": false,
  "isolateTickets": false,
  "briefFile": "2026-11-03-brief.md",
  "memoryFile": "AGENTS.md",
  "memoryOwner": "autopilot",
  "skillDir": "/home/user/Autopilot/skills/autopilot",
  "baseCommit": "aea02cc",
  "startedAt": "2026-11-03T16:24:15+00:00",
  "updatedAt": "2026-11-03T16:33:19+00:00",
  "finishedAt": null,
  "stages": [
    {
      "id": "preflight",
      "status": "done",
      "startedAt": "2026-11-03T16:24:15+00:00",
      "finishedAt": "2026-11-03T16:24:27+00:00"
    },
    {
      "id": "manifest",
      "status": "done",
      "startedAt": "2026-11-03T16:24:27+00:00",
      "finishedAt": "2026-11-03T16:24:47+00:00"
    },
    {
      "id": "briefing",
      "status": "done",
      "startedAt": "2026-11-03T16:24:47+00:00",
      "finishedAt": "2026-11-03T16:26:05+00:00"
    },
    {
      "id": "spec",
      "status": "done",
      "startedAt": "2026-11-03T16:26:05+00:00",
      "note": "x",
      "finishedAt": "2026-11-03T16:31:57+00:00"
    },
    {
      "id": "plan",
      "status": "active",
      "startedAt": "2026-11-03T16:31:57+00:00"
    },
    {
      "id": "build",
      "status": "pending"
    },
    {
      "id": "review",
      "status": "pending"
    },
    {
      "id": "final",
      "status": "pending"
    }
  ],
  "requirements": {
    "total": 18,
    "done": 0,
    "inTicket": 18,
    "inSpec": 0,
    "placeholder": 0,
    "deferred": 0,
    "dropped": 0
  },
  "tickets": [
    {
      "id": "01",
      "title": "Состояние, безопасность путей и выбор моделей",
      "requirements": [
        "R16",
        "R01",
        "R07",
        "R08",
        "R09",
        "R02",
        "R03",
        "R04",
        "R06",
        "R18",
        "R10"
      ],
      "blockedBy": [],
      "wave": 1,
      "zone": [
        "skills/autopilot/tools/state_io.py",
        "skills/autopilot/tools/ap.py",
        "skills/autopilot/tools/controller.py",
        "skills/autopilot/tools/spend_guard.py",
        "skills/autopilot/tools/codex_dispatch.py",
        "skills/autopilot/tools/retry_policy.py",
        "skills/autopilot/tools/worktrees.py",
        "skills/autopilot/tools/worker_outcome.py",
        "skills/autopilot/tools/process_containment.py",
        "skills/autopilot/tools/test_evidence.py",
        "skills/autopilot/tools/model_router.py",
        "skills/autopilot/tools/claude_agent_guard.py",
        "skills/autopilot/phases/0-instruments.md",
        "tests/test_state_io.py",
        "tests/test_ap.py",
        "tests/test_controller.py",
        "tests/test_spend_guard.py",
        "tests/test_codex_dispatch.py",
        "tests/test_retry_policy.py",
        "tests/test_worktrees.py",
        "tests/test_worker_outcome.py",
        "tests/test_process_containment.py",
        "tests/test_test_evidence.py",
        "tests/test_cargo_evidence.py",
        "tests/test_model_router.py",
        "tests/test_claude_agent_guard.py"
      ],
      "review": "да — фундамент",
      "model": "сильная",
      "fingerprint": "3be55889d35738071f1538195e1e8c7907aa1e4778f3dba77361bb548f4895ba",
      "status": "pending",
      "retries": 0,
      "repairs": 0,
      "plannedRouting": {
        "ticket": "01",
        "provider": "anthropic",
        "model": "sonnet",
        "effort": "high",
        "effortEnforced": null,
        "profile": "strong",
        "score": 50,
        "factors": {
          "algorithm": 5,
          "coupling": 20,
          "uncertainty": 0,
          "context": 5,
          "testing": 10,
          "risk": 10
        },
        "reason": "score=50; profile=strong; high-risk=True",
        "requiresReview": true,
        "status": "blocked",
        "fingerprint": "3be55889d35738071f1538195e1e8c7907aa1e4778f3dba77361bb548f4895ba",
        "hostExecutionVerified": false,
        "error": "No verified host capabilities",
        "applied": false
      }
    },
    {
      "id": "02",
      "title": "Документация, CI и бэкапы дашборда",
      "requirements": [
        "R11",
        "R12",
        "R13",
        "R14",
        "R15"
      ],
      "blockedBy": [],
      "wave": 1,
      "zone": [
        "STATUS.md",
        "README.md",
        "README.ru.md",
        "README.de.md",
        "docs/autopilot/gui-clients.md",
        "docs/autopilot/worktrees.md",
        "docs/autopilot/controller.md",
        "docs/autopilot/model-routing.md",
        "skills/autopilot/SKILL.md",
        ".github/workflows/python-tests.yml",
        "skills/autopilot/tools/dashboard_upgrade.py",
        "tests/test_skill_allowed_tools.py",
        "tests/test_documentation_locales.py",
        "tests/test_dashboard_upgrade.py"
      ],
      "review": "нет",
      "model": "обычная",
      "fingerprint": "c95853badf540c7047384a2f37d97982639a5c363d2bd46d44721a55f86819a5",
      "status": "pending",
      "retries": 0,
      "repairs": 0,
      "plannedRouting": {
        "ticket": "02",
        "provider": "anthropic",
        "model": "sonnet",
        "effort": "high",
        "effortEnforced": null,
        "profile": "strong",
        "score": 55,
        "factors": {
          "algorithm": 20,
          "coupling": 20,
          "uncertainty": 0,
          "context": 5,
          "testing": 10,
          "risk": 0
        },
        "reason": "score=55; profile=strong; high-risk=False",
        "requiresReview": true,
        "status": "blocked",
        "fingerprint": "c95853badf540c7047384a2f37d97982639a5c363d2bd46d44721a55f86819a5",
        "hostExecutionVerified": false,
        "error": "No verified host capabilities",
        "applied": false
      }
    },
    {
      "id": "03",
      "title": "Подпись гейтов и защита файлов прогона",
      "requirements": [
        "R17",
        "R05"
      ],
      "blockedBy": [
        "01"
      ],
      "wave": 2,
      "zone": [
        "skills/autopilot/tools/gate_sign.py",
        "skills/autopilot/tools/claude_attest.py",
        "skills/autopilot/tools/claude_agent_guard.py",
        "skills/autopilot/tools/test_evidence.py",
        "skills/autopilot/tools/ap.py",
        "skills/autopilot/phases/0-instruments.md",
        "docs/autopilot/claude-code.md",
        "tests/test_gate_sign.py",
        "tests/test_claude_attest.py",
        "tests/test_claude_agent_guard.py",
        "tests/test_test_evidence.py",
        "tests/test_ap.py"
      ],
      "review": "да — ключи и подписи",
      "model": "сильная",
      "fingerprint": "a6f6c452e3d8ace9f36e1e7df73ae1dd744dd50e2fd7ff0754788ef2e169e74c",
      "status": "pending",
      "retries": 0,
      "repairs": 0,
      "plannedRouting": {
        "ticket": "03",
        "provider": "anthropic",
        "model": "sonnet",
        "effort": "medium",
        "effortEnforced": null,
        "profile": "balanced",
        "score": 35,
        "factors": {
          "algorithm": 5,
          "coupling": 20,
          "uncertainty": 0,
          "context": 5,
          "testing": 5,
          "risk": 0
        },
        "reason": "score=35; profile=balanced; high-risk=False",
        "requiresReview": false,
        "status": "blocked",
        "fingerprint": "a6f6c452e3d8ace9f36e1e7df73ae1dd744dd50e2fd7ff0754788ef2e169e74c",
        "hostExecutionVerified": false,
        "error": "No verified host capabilities",
        "applied": false
      }
    }
  ],
  "tests": null,
  "usageEvents": [],
  "budgetTokens": null,
  "debt": {
    "placeholders": [],
    "assumptions": [],
    "emptyEnv": []
  },
  "additions": [],
  "coverage": {
    "found": 3,
    "fixed": 3,
    "deferred": 0,
    "items": []
  },
  "concerns": [],
  "blockingFindings": [],
  "blind": null,
  "beats": [
    "2026-11-03T16:24:15+00:00",
    "2026-11-03T16:24:27+00:00",
    "2026-11-03T16:24:42+00:00",
    "2026-11-03T16:24:47+00:00",
    "2026-11-03T16:25:03+00:00",
    "2026-11-03T16:26:04+00:00",
    "2026-11-03T16:26:05+00:00",
    "2026-11-03T16:30:47+00:00",
    "2026-11-03T16:31:00+00:00",
    "2026-11-03T16:31:57+00:00",
    "2026-11-03T16:32:53+00:00",
    "2026-11-03T16:33:13+00:00",
    "2026-11-03T16:33:19+00:00"
  ],
  "rev": 20,
  "waiting": {
    "kind": "stop",
    "since": "2026-11-03T16:33:19+00:00",
    "note": "выбор режима исполнения: strict (нужен новый чат на вашей машине) или sequential-host (здесь, по одному таску)"
  },
  "waits": [
    {
      "kind": "briefing",
      "from": "2026-11-03T16:25:03+00:00",
      "to": "2026-11-03T16:26:04+00:00"
    }
  ],
  "log": [
    {
      "t": "2026-11-03T16:24:15+00:00",
      "k": "init"
    },
    {
      "t": "2026-11-03T16:24:27+00:00",
      "k": "stage",
      "id": "manifest",
      "act": "start"
    },
    {
      "t": "2026-11-03T16:24:47+00:00",
      "k": "stage",
      "id": "briefing",
      "act": "start"
    },
    {
      "t": "2026-11-03T16:25:03+00:00",
      "k": "ask",
      "kind": "briefing",
      "note": "два вопроса по подписи гейтов (R17, R05): где хранить ключ и что делать со старыми прогонами"
    },
    {
      "t": "2026-11-03T16:26:04+00:00",
      "k": "answered",
      "kind": "briefing"
    },
    {
      "t": "2026-11-03T16:26:05+00:00",
      "k": "gate",
      "g": "G1",
      "ok": false,
      "open": 18,
      "total": 18
    },
    {
      "t": "2026-11-03T16:26:05+00:00",
      "k": "stage",
      "id": "spec",
      "act": "start"
    },
    {
      "t": "2026-11-03T16:30:47+00:00",
      "k": "stage",
      "id": "spec",
      "act": "skip",
      "note": "x"
    },
    {
      "t": "2026-11-03T16:31:00+00:00",
      "k": "gate",
      "g": "G1",
      "ok": false,
      "open": 18,
      "total": 18
    },
    {
      "t": "2026-11-03T16:31:00+00:00",
      "k": "stage",
      "id": "spec",
      "act": "start"
    },
    {
      "t": "2026-11-03T16:31:57+00:00",
      "k": "gate",
      "g": "G2",
      "ok": true,
      "found": 3,
      "fixed": 3,
      "deferred": 0
    },
    {
      "t": "2026-11-03T16:31:57+00:00",
      "k": "stage",
      "id": "plan",
      "act": "start"
    },
    {
      "t": "2026-11-03T16:32:53+00:00",
      "k": "tier",
      "v": "T1"
    },
    {
      "t": "2026-11-03T16:32:53+00:00",
      "k": "tickets",
      "n": 3
    },
    {
      "t": "2026-11-03T16:32:53+00:00",
      "k": "gate",
      "g": "G3",
      "ok": true,
      "problems": 0
    },
    {
      "t": "2026-11-03T16:33:13+00:00",
      "k": "plan-models",
      "provider": "anthropic",
      "applied": false,
      "tickets": 3,
      "blocked": 3
    },
    {
      "t": "2026-11-03T16:33:19+00:00",
      "k": "ask",
      "kind": "stop",
      "note": "выбор режима исполнения: strict (нужен новый чат на вашей машине) или sequential-host (здесь, по одному таску)"
    }
  ],
  "reqList": [
    {
      "id": "R01",
      "text": "«A01: save() делает os.replace без повтора»",
      "status": "in-ticket"
    },
    {
      "id": "R02",
      "text": "«A02: land() не проверяет зоны и пути; тесты берутся из текста --tests N/0»",
      "status": "in-ticket"
    },
    {
      "id": "R03",
      "text": "«A03: git diff --cached --name-only без --no-renames»",
      "status": "in-ticket"
    },
    {
      "id": "R04",
      "text": "«A04: риск тикета считается только по словарю слов»",
      "status": "in-ticket"
    },
    {
      "id": "R05",
      "text": "«A05: гард защищает от промахов оркестратора, не от исполнителя»",
      "status": "in-ticket"
    },
    {
      "id": "R06",
      "text": "«A06: запрет премиум-моделей по префиксу строки»",
      "status": "in-ticket"
    },
    {
      "id": "R07",
      "text": "«A07: четыре разборщика state.js с разной терпимостью»",
      "status": "in-ticket"
    },
    {
      "id": "R08",
      "text": "«A08: init --force теряет журнал»",
      "status": "in-ticket"
    },
    {
      "id": "R09",
      "text": "«A09: classify смотрит только первые 12 000 символов»",
      "status": "in-ticket"
    },
    {
      "id": "R10",
      "text": "«A10: trusted-раннер не использует OwnedJob»",
      "status": "in-ticket"
    },
    {
      "id": "R11",
      "text": "«A11: версии не сходятся»",
      "status": "in-ticket"
    },
    {
      "id": "R12",
      "text": "«A12: доки велят py -3.13 … и controller.py, а allowed-tools пропускает только py -3 .autopilot/ap.py »",
      "status": "in-ticket"
    },
    {
      "id": "R13",
      "text": "«A13: в таблице и скоринге нет tier critical»",
      "status": "in-ticket"
    },
    {
      "id": "R14",
      "text": "«A14: бэкап HTML со снимком state.js в общем tempdir»",
      "status": "in-ticket"
    },
    {
      "id": "R15",
      "text": "«A15: compileall только skills/autopilot/tools и tests»",
      "status": "in-ticket"
    },
    {
      "id": "R16",
      "text": "«I01: общий модуль чтения/записи state.js (BOM, префикс, повтор replace) — закрывает A01 и A07 разом»",
      "status": "in-ticket"
    },
    {
      "id": "R17",
      "text": "«I02: подписанные квитанции гейтов, ключ вне .autopilot — иначе правка state.js/attestations.jsonl проходит сверку (A05)»",
      "status": "in-ticket"
    },
    {
      "id": "R18",
      "text": "«I03: точный allowlist моделей в роутере вместо префиксов + тесты на Bedrock-ID и claude-3-opus (A06)»",
      "status": "in-ticket"
    }
  ],
  "gates": {
    "G1": {
      "ok": false,
      "at": "2026-11-03T16:31:00+00:00",
      "open": 18,
      "total": 18
    },
    "G2": {
      "ok": true,
      "at": "2026-11-03T16:31:57+00:00",
      "found": 3,
      "fixed": 3,
      "deferred": 0
    },
    "G3": {
      "ok": true,
      "at": "2026-11-03T16:32:53+00:00",
      "problems": 0
    }
  },
  "result": null,
  "skillVersion": "2.6.0",
  "planContractDigest": "2e6ca6c997cf1cc19fe470b8b2d06418c2b6d732b14a967f1891974f19ec9ee8",
  "planValidationDigest": "2a84e0f72ca643f2ab74f9517d85875fa5fe84bc3ad5d36fec427cc597235063"
}
