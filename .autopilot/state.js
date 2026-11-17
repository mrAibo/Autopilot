window.STATE =
{
  "version": 2,
  "slug": "orchestrator-spend-waves-4-6",
  "dir": "2026-11-17-orchestrator-spend-waves-4-6--wip",
  "title": "Autopilot: волны 4–6 (R11–R21)",
  "mode": "semi",
  "depth": "normal",
  "tier": "T2",
  "strictRouting": false,
  "gateSigned": false,
  "sequentialHost": false,
  "isolateTickets": false,
  "briefFile": "2026-11-17-brief.md",
  "memoryFile": "AGENTS.md",
  "memoryOwner": "autopilot",
  "skillDir": "C:/Users/crown/Downloads/Projects/Autopilot/skills/autopilot",
  "baseCommit": null,
  "startedAt": "2026-11-17T03:03:11+01:00",
  "updatedAt": "2026-11-17T03:15:12+01:00",
  "finishedAt": null,
  "stages": [
    {
      "id": "preflight",
      "status": "done",
      "startedAt": "2026-11-17T03:03:11+01:00",
      "segments": [
        {
          "startedAt": "2026-11-17T03:03:11+01:00",
          "finishedAt": "2026-11-17T03:03:16+01:00"
        }
      ],
      "finishedAt": "2026-11-17T03:03:16+01:00"
    },
    {
      "id": "manifest",
      "status": "done",
      "segments": [
        {
          "startedAt": "2026-11-17T03:03:16+01:00",
          "finishedAt": "2026-11-17T03:03:34+01:00"
        }
      ],
      "startedAt": "2026-11-17T03:03:16+01:00",
      "finishedAt": "2026-11-17T03:03:34+01:00"
    },
    {
      "id": "briefing",
      "status": "skipped",
      "segments": [
        {
          "startedAt": "2026-11-17T03:03:34+01:00",
          "finishedAt": "2026-11-17T03:03:40+01:00"
        }
      ],
      "startedAt": "2026-11-17T03:03:34+01:00",
      "finishedAt": "2026-11-17T03:03:40+01:00",
      "note": "бриф однозначен: решения «-latest разрешить», порядок и объём заданы в задаче; остальное — решения планировщика"
    },
    {
      "id": "spec",
      "status": "done",
      "segments": [
        {
          "startedAt": "2026-11-17T03:03:41+01:00",
          "finishedAt": "2026-11-17T03:15:04+01:00"
        }
      ],
      "startedAt": "2026-11-17T03:03:41+01:00",
      "finishedAt": "2026-11-17T03:15:04+01:00"
    },
    {
      "id": "plan",
      "status": "active",
      "segments": [
        {
          "startedAt": "2026-11-17T03:15:04+01:00",
          "finishedAt": null
        }
      ],
      "startedAt": "2026-11-17T03:15:04+01:00"
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
    "total": 11,
    "done": 0,
    "inTicket": 11,
    "inSpec": 0,
    "placeholder": 0,
    "deferred": 0,
    "dropped": 0
  },
  "tickets": [
    {
      "id": "01",
      "title": "r13-model-names-latest",
      "requirements": [
        "R13"
      ],
      "blockedBy": [],
      "wave": 1,
      "zone": [
        "skills/autopilot/tools/model_router.py",
        "tests/test_model_router.py",
        "tests/test_claude_agent_guard.py",
        "docs/autopilot/model-routing.md"
      ],
      "review": "нет",
      "model": "обычная",
      "fingerprint": "b4574734bce6dc089a67a81f57f9bec30941df6832a579bf1da125872017ab16",
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
        "score": 61,
        "factors": {
          "algorithm": 10,
          "coupling": 15,
          "uncertainty": 11,
          "context": 5,
          "testing": 10,
          "risk": 10
        },
        "reason": "score=61; profile=strong; high-risk=True; class=обычный; risk=высокий; why=одна правка регэкспа и таблица тестов на имена, зона чувствительная (`model_router`), поэтому маршрут не ниже сильного\r",
        "requiresReview": true,
        "status": "blocked",
        "fingerprint": "b4574734bce6dc089a67a81f57f9bec30941df6832a579bf1da125872017ab16",
        "hostExecutionVerified": false,
        "error": "No verified host capabilities",
        "applied": false
      }
    },
    {
      "id": "02",
      "title": "r17-parallel-test-runner",
      "requirements": [
        "R17"
      ],
      "blockedBy": [],
      "wave": 1,
      "zone": [
        "tools/run-tests.py",
        "tests/test_run_tests.py",
        "AGENTS.md"
      ],
      "review": "нет",
      "model": "обычная",
      "fingerprint": "aa13e2fe8256917fa59d39e8a43e20e5f472788e8a99f2d3a73108f2bafb74fc",
      "status": "pending",
      "retries": 0,
      "repairs": 0,
      "plannedRouting": {
        "ticket": "02",
        "provider": "anthropic",
        "model": "sonnet",
        "effort": "medium",
        "effortEnforced": null,
        "profile": "balanced",
        "score": 41,
        "factors": {
          "algorithm": 10,
          "coupling": 10,
          "uncertainty": 11,
          "context": 5,
          "testing": 5,
          "risk": 0
        },
        "reason": "score=41; profile=balanced; high-risk=False; class=обычный; risk=обычный; why=новый запускатель на stdlib с дроблением по классам и сложением итогов, логика без риска для данных\r",
        "requiresReview": false,
        "status": "blocked",
        "fingerprint": "aa13e2fe8256917fa59d39e8a43e20e5f472788e8a99f2d3a73108f2bafb74fc",
        "hostExecutionVerified": false,
        "error": "No verified host capabilities",
        "applied": false
      }
    },
    {
      "id": "03",
      "title": "r21-readme-quickstart-history",
      "requirements": [
        "R21"
      ],
      "blockedBy": [],
      "wave": 1,
      "zone": [
        "README.md",
        "README.ru.md",
        "README.de.md",
        "STATUS.md",
        "HANDOFF.md",
        "HANDOFF_NEXT_CLIENT_2026-10-26.md",
        "BRIEF-2026-11-improvements.md",
        "docs/history/",
        "docs/autopilot/release-readiness.md",
        "docs/autopilot/scope-and-labs.md",
        "docs/autopilot/gui-clients.md",
        "tests/test_documentation_locales.py"
      ],
      "review": "нет",
      "model": "обычная",
      "fingerprint": "6f3e54f1bb75027823748e65b1518cad1cb1327051784551facda7e989c0c38a",
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
        "score": 51,
        "factors": {
          "algorithm": 10,
          "coupling": 20,
          "uncertainty": 11,
          "context": 5,
          "testing": 5,
          "risk": 0
        },
        "reason": "score=51; profile=balanced; high-risk=False; class=обычный; risk=обычный; why=правка трёх README в одном порядке разделов и перенос файлов с исправлением ссылок, нужно держать структуру заголовков и тесты ссылок\r",
        "requiresReview": false,
        "status": "blocked",
        "fingerprint": "6f3e54f1bb75027823748e65b1518cad1cb1327051784551facda7e989c0c38a",
        "hostExecutionVerified": false,
        "error": "No verified host capabilities",
        "applied": false
      }
    },
    {
      "id": "04",
      "title": "r14-r20-server-ping-token-errors",
      "requirements": [
        "R14",
        "R20"
      ],
      "blockedBy": [],
      "wave": 1,
      "zone": [
        "skills/autopilot/tools/ap.py",
        "skills/autopilot/phases/dashboard-template.html",
        "tests/test_followups_token.py",
        "tests/test_ap_audit.py",
        "tests/test_dashboard_views.py",
        "tests/test_followups_dashboard.py",
        "docs/adr/0013-server-ping.md",
        "docs/adr/0001-dashboard-server-token-host-check.md"
      ],
      "review": "нет",
      "model": "обычная",
      "fingerprint": "a551de83d47be437072b4dbc9c0fc8e80a76667ea4b21419f5ae01426fc22a17",
      "status": "pending",
      "retries": 0,
      "repairs": 0,
      "plannedRouting": {
        "ticket": "04",
        "provider": "anthropic",
        "model": "sonnet",
        "effort": "xhigh",
        "effortEnforced": null,
        "profile": "critical",
        "score": 65,
        "factors": {
          "algorithm": 20,
          "coupling": 20,
          "uncertainty": 0,
          "context": 5,
          "testing": 10,
          "risk": 10
        },
        "reason": "score=65; profile=critical; high-risk=True; class=сложный; risk=высокий; why=подтверждение сервера по hmac от токена затрагивает защиту токена из ADR 0001, плюс общая серверная часть и поведение страницы при 403\r",
        "requiresReview": true,
        "status": "blocked",
        "fingerprint": "a551de83d47be437072b4dbc9c0fc8e80a76667ea4b21419f5ae01426fc22a17",
        "hostExecutionVerified": false,
        "error": "No verified host capabilities",
        "applied": false
      }
    },
    {
      "id": "05",
      "title": "r15-history-cache",
      "requirements": [
        "R15"
      ],
      "blockedBy": [
        "04"
      ],
      "wave": 2,
      "zone": [
        "skills/autopilot/tools/ap.py",
        "tests/test_ap_audit.py",
        "tests/test_ap.py"
      ],
      "review": "нет",
      "model": "обычная",
      "fingerprint": "cdb2887fdbf4df71ffd08257c63fc5ff9ec3d6782ee1a4a6096899d38394fc09",
      "status": "pending",
      "retries": 0,
      "repairs": 0,
      "plannedRouting": {
        "ticket": "05",
        "provider": "anthropic",
        "model": "sonnet",
        "effort": "medium",
        "effortEnforced": null,
        "profile": "balanced",
        "score": 41,
        "factors": {
          "algorithm": 10,
          "coupling": 10,
          "uncertainty": 11,
          "context": 5,
          "testing": 5,
          "risk": 0
        },
        "reason": "score=41; profile=balanced; high-risk=False; class=обычный; risk=обычный; why=кэш по mtime и размеру с молчаливым пересчётом, логика в одной функции\r",
        "requiresReview": false,
        "status": "blocked",
        "fingerprint": "cdb2887fdbf4df71ffd08257c63fc5ff9ec3d6782ee1a4a6096899d38394fc09",
        "hostExecutionVerified": false,
        "error": "No verified host capabilities",
        "applied": false
      }
    },
    {
      "id": "06",
      "title": "r12-router-scale-table",
      "requirements": [
        "R12"
      ],
      "blockedBy": [
        "01",
        "03",
        "04"
      ],
      "wave": 2,
      "zone": [
        "docs/autopilot/model-routing.md",
        "README.md",
        "README.ru.md",
        "README.de.md",
        "skills/autopilot/phases/dashboard-template.html",
        "tests/test_model_router.py",
        "tests/test_dashboard_boards.py",
        "tests/test_followups_dashboard.py",
        "tests/test_dashboard_views.py",
        "tests/test_documentation_locales.py"
      ],
      "review": "нет",
      "model": "обычная",
      "fingerprint": "3c07e07becf419e1953f910cce7a65a583f2ef0cf04944b227ab568fb34f5e20",
      "status": "pending",
      "retries": 0,
      "repairs": 0,
      "plannedRouting": {
        "ticket": "06",
        "provider": "anthropic",
        "model": "sonnet",
        "effort": "medium",
        "effortEnforced": null,
        "profile": "balanced",
        "score": 51,
        "factors": {
          "algorithm": 10,
          "coupling": 20,
          "uncertainty": 11,
          "context": 5,
          "testing": 5,
          "risk": 0
        },
        "reason": "score=51; profile=balanced; high-risk=False; class=обычный; risk=обычный; why=таблица и тест сверки с роутером, правка `humanRoute` по готовому формату `reason`\r",
        "requiresReview": false,
        "status": "blocked",
        "fingerprint": "3c07e07becf419e1953f910cce7a65a583f2ef0cf04944b227ab568fb34f5e20",
        "hostExecutionVerified": false,
        "error": "No verified host capabilities",
        "applied": false
      }
    },
    {
      "id": "07",
      "title": "r16-r18-finish-attestations-profiles",
      "requirements": [
        "R16",
        "R18"
      ],
      "blockedBy": [
        "05"
      ],
      "wave": 3,
      "zone": [
        "skills/autopilot/tools/ap.py",
        "skills/autopilot/tools/agent_profiles.py",
        "skills/autopilot/tools/claude_agent_guard.py",
        "skills/autopilot/phases/0-preflight.md",
        "skills/autopilot/phases/0-instruments.md",
        "tests/test_ap.py",
        "tests/test_light_profiles.py",
        "tests/test_agent_profiles.py",
        "docs/autopilot/claude-code.md"
      ],
      "review": "нет",
      "model": "обычная",
      "fingerprint": "9e807ae2dc099de7f50701868ba10ecd2b4fa3e5747de30a938f76e34299273c",
      "status": "pending",
      "retries": 0,
      "repairs": 0,
      "plannedRouting": {
        "ticket": "07",
        "provider": "anthropic",
        "model": "sonnet",
        "effort": "high",
        "effortEnforced": null,
        "profile": "strong",
        "score": 66,
        "factors": {
          "algorithm": 10,
          "coupling": 20,
          "uncertainty": 11,
          "context": 5,
          "testing": 10,
          "risk": 10
        },
        "reason": "score=66; profile=strong; high-risk=True; class=обычный; risk=высокий; why=собственный код удаляет файлы профилей и переносит подписанный журнал аттестаций при `finish`, ошибка уничтожает чужие профили или ломает подписи\r",
        "requiresReview": true,
        "status": "blocked",
        "fingerprint": "9e807ae2dc099de7f50701868ba10ecd2b4fa3e5747de30a938f76e34299273c",
        "hostExecutionVerified": false,
        "error": "No verified host capabilities",
        "applied": false
      }
    },
    {
      "id": "08",
      "title": "r11-class-model-effort-report",
      "requirements": [
        "R11"
      ],
      "blockedBy": [
        "07"
      ],
      "wave": 4,
      "zone": [
        "skills/autopilot/tools/ap.py",
        "skills/autopilot/tools/run_log.py",
        "tests/test_ap_audit.py",
        "tests/test_run_log.py",
        "tests/test_ap.py",
        "docs/autopilot/run-log.md",
        "docs/autopilot/measuring-cost.md"
      ],
      "review": "нет",
      "model": "обычная",
      "fingerprint": "2c2f97633f5de63c405ed1db0de4ebbef0a285926901a8f66cf180c8057e532b",
      "status": "pending",
      "retries": 0,
      "repairs": 0,
      "plannedRouting": {
        "ticket": "08",
        "provider": "anthropic",
        "model": "sonnet",
        "effort": "medium",
        "effortEnforced": null,
        "profile": "balanced",
        "score": 51,
        "factors": {
          "algorithm": 10,
          "coupling": 20,
          "uncertainty": 11,
          "context": 5,
          "testing": 5,
          "risk": 0
        },
        "reason": "score=51; profile=balanced; high-risk=False; class=обычный; risk=обычный; why=новая схема строки журнала и сводная таблица по ней, несколько мест, но без риска для данных\r",
        "requiresReview": false,
        "status": "blocked",
        "fingerprint": "2c2f97633f5de63c405ed1db0de4ebbef0a285926901a8f66cf180c8057e532b",
        "hostExecutionVerified": false,
        "error": "No verified host capabilities",
        "applied": false
      }
    },
    {
      "id": "09",
      "title": "r19-forecast-report-budget",
      "requirements": [
        "R19"
      ],
      "blockedBy": [
        "06",
        "08"
      ],
      "wave": 5,
      "zone": [
        "skills/autopilot/tools/ap.py",
        "skills/autopilot/phases/4-plan.md",
        "skills/autopilot/phases/8-final.md",
        "skills/autopilot/phases/0-modes.md",
        "skills/autopilot/phases/dashboard-template.html",
        "tests/test_ap_audit.py",
        "tests/test_dashboard_views.py",
        "tests/test_dashboard_details.py",
        "tests/test_text_split.py",
        "docs/autopilot/observability.md"
      ],
      "review": "нет",
      "model": "обычная",
      "fingerprint": "527beb5583b28797edd3651da2f48a50bec7bb1528b69d7d9ae2e92872ffe00f",
      "status": "pending",
      "retries": 0,
      "repairs": 0,
      "plannedRouting": {
        "ticket": "09",
        "provider": "anthropic",
        "model": "sonnet",
        "effort": "medium",
        "effortEnforced": null,
        "profile": "balanced",
        "score": 51,
        "factors": {
          "algorithm": 10,
          "coupling": 20,
          "uncertainty": 11,
          "context": 5,
          "testing": 5,
          "risk": 0
        },
        "reason": "score=51; profile=balanced; high-risk=False; class=обычный; risk=обычный; why=строка прогноза из готовой истории, две строки текста навыка и плитка лимита на дашборде\r",
        "requiresReview": false,
        "status": "blocked",
        "fingerprint": "527beb5583b28797edd3651da2f48a50bec7bb1528b69d7d9ae2e92872ffe00f",
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
    "found": 14,
    "fixed": 14,
    "deferred": 0,
    "items": []
  },
  "concerns": [],
  "blockingFindings": [],
  "blind": null,
  "beats": [
    "2026-11-17T03:03:11+01:00",
    "2026-11-17T03:03:16+01:00",
    "2026-11-17T03:03:28+01:00",
    "2026-11-17T03:03:34+01:00",
    "2026-11-17T03:03:40+01:00",
    "2026-11-17T03:03:41+01:00",
    "2026-11-17T03:13:00+01:00",
    "2026-11-17T03:15:04+01:00",
    "2026-11-17T03:15:05+01:00",
    "2026-11-17T03:15:06+01:00",
    "2026-11-17T03:15:10+01:00",
    "2026-11-17T03:15:11+01:00",
    "2026-11-17T03:15:12+01:00"
  ],
  "rev": 14,
  "waiting": null,
  "waits": [],
  "log": [
    {
      "t": "2026-11-17T03:03:11+01:00",
      "k": "init"
    },
    {
      "t": "2026-11-17T03:03:16+01:00",
      "k": "stage",
      "id": "manifest",
      "act": "start"
    },
    {
      "t": "2026-11-17T03:03:34+01:00",
      "k": "stage",
      "id": "briefing",
      "act": "start"
    },
    {
      "t": "2026-11-17T03:03:40+01:00",
      "k": "stage",
      "id": "briefing",
      "act": "skip",
      "note": "бриф однозначен: решения «-latest разрешить», порядок и объём заданы в задаче; остальное — решения планировщика"
    },
    {
      "t": "2026-11-17T03:03:41+01:00",
      "k": "gate",
      "g": "G1",
      "ok": false,
      "open": 11,
      "total": 11
    },
    {
      "t": "2026-11-17T03:03:41+01:00",
      "k": "stage",
      "id": "spec",
      "act": "start"
    },
    {
      "t": "2026-11-17T03:13:00+01:00",
      "k": "gate",
      "g": "G1",
      "ok": true,
      "open": 0,
      "total": 11
    },
    {
      "t": "2026-11-17T03:13:00+01:00",
      "k": "stage",
      "id": "spec",
      "act": "start"
    },
    {
      "t": "2026-11-17T03:15:04+01:00",
      "k": "stage",
      "id": "plan",
      "act": "start"
    },
    {
      "t": "2026-11-17T03:15:05+01:00",
      "k": "tickets",
      "n": 9
    },
    {
      "t": "2026-11-17T03:15:06+01:00",
      "k": "gate",
      "g": "G3",
      "ok": true,
      "problems": 0
    },
    {
      "t": "2026-11-17T03:15:10+01:00",
      "k": "gate",
      "g": "G2",
      "ok": true,
      "found": 14,
      "fixed": 14,
      "deferred": 0
    },
    {
      "t": "2026-11-17T03:15:11+01:00",
      "k": "tier",
      "v": "T2"
    },
    {
      "t": "2026-11-17T03:15:12+01:00",
      "k": "plan-models",
      "provider": "anthropic",
      "applied": false,
      "tickets": 9,
      "blocked": 9
    }
  ],
  "reqList": [
    {
      "id": "R11",
      "text": "«Свод для калибровки роутера» — report-run печатает по сочетанию «класс × модель × усилие»; plan-models печатает строку совета из истории",
      "status": "in-ticket"
    },
    {
      "id": "R12",
      "text": "«Шкала роутера показана такой, какая она есть» — таблица в model-routing.md и трёх README; карточка таска на дашборде показывает класс, риск, причину",
      "status": "in-ticket"
    },
    {
      "id": "R13",
      "text": "«Имена моделей семейства 5» — тесты на написания claude--5-; алиас -latest у Haiku и Sonnet разрешён",
      "status": "in-ticket"
    },
    {
      "id": "R14",
      "text": "«ap.py на Windows не зовёт PowerShell на каждую команду»",
      "status": "in-ticket"
    },
    {
      "id": "R15",
      "text": "«История прошлых сборок не перечитывается каждой командой»",
      "status": "in-ticket"
    },
    {
      "id": "R16",
      "text": "«Аттестации не растут без конца»",
      "status": "in-ticket"
    },
    {
      "id": "R17",
      "text": "«Тесты самого Autopilot идут параллельно»",
      "status": "in-ticket"
    },
    {
      "id": "R18",
      "text": "«Профили агентов сданной сборки удаляются»",
      "status": "in-ticket"
    },
    {
      "id": "R19",
      "text": "«Прогноз после плана и расход в отчёте»",
      "status": "in-ticket"
    },
    {
      "id": "R20",
      "text": "«Понятные ошибки дашборда»",
      "status": "in-ticket"
    },
    {
      "id": "R21",
      "text": "«Быстрый старт в начале README»",
      "status": "in-ticket"
    }
  ],
  "gates": {
    "G1": {
      "ok": true,
      "at": "2026-11-17T03:13:00+01:00",
      "open": 0,
      "total": 11
    },
    "G3": {
      "ok": true,
      "at": "2026-11-17T03:15:06+01:00",
      "problems": 0
    },
    "G2": {
      "ok": true,
      "at": "2026-11-17T03:15:10+01:00",
      "found": 14,
      "fixed": 14,
      "deferred": 0
    }
  },
  "result": null,
  "skillVersion": "2.7.0",
  "spend": {
    "byRole": {},
    "byModel": {},
    "byTicket": {}
  },
  "history": [
    {
      "dir": "2026-11-16-cheaper-faster",
      "title": "Autopilot: дешевле, быстрее, удобнее",
      "startedAt": "2026-11-16T17:13:04+01:00",
      "finishedAt": "2026-11-16T19:33:40+01:00",
      "minutes": 139,
      "tickets": 4,
      "repairs": 0,
      "tokens": 396276,
      "result": "Волны 1–3: лёгкие профили, подсказка о контексте, chore, ticket land, bootstrap, doctor, второй круг приёмки по расхождениям, текст обычного пути короче; 1027 тестов зелёные"
    },
    {
      "dir": "2026-11-16-subagent-spend-nonstrict",
      "title": "Расход субагентов виден в обычном режиме",
      "startedAt": "2026-11-16T02:27:36+01:00",
      "finishedAt": "2026-11-16T03:05:46+01:00",
      "minutes": 37,
      "tickets": 1,
      "repairs": 0,
      "tokens": 73515,
      "result": "Расход субагентов виден в обычном режиме: ap.py spend-subagents и finish пишут его из журналов Claude Code, report-run и дашборд показывают; 959 тестов зелёные, слепая приёмка 10 из 11, круг 2 закрыл последний пункт"
    },
    {
      "dir": "2026-11-16-spend-optimization",
      "title": "Оптимизация расхода: учёт и короткий вывод проверок",
      "startedAt": "2026-11-16T00:32:00+01:00",
      "finishedAt": "2026-11-16T01:16:41+01:00",
      "minutes": 44,
      "tickets": 3,
      "repairs": 0,
      "tokens": 45662,
      "result": "Оптимизация расхода: spend видит кэш и главную сессию (оркестратора), report-run и дашборд показывают их, исполнитель запускает проверки с коротким выводом; 942 теста зелёные, слепая приёмка 5 из 7 (замер общего кэша исполнителей не получен)"
    },
    {
      "dir": "2026-11-15-dashboard-token-fixes",
      "title": "Доделки после аудита: токен дашборда, ключ подписи, спека",
      "startedAt": "2026-11-15T20:36:48+01:00",
      "finishedAt": "2026-11-15T23:03:26+01:00",
      "minutes": 143,
      "tickets": 4,
      "repairs": 0,
      "tokens": 0,
      "result": "Доделки после аудита: страница без токена не несёт данных, адрес с токеном печатает только ap.py url, ключ подписи создаётся атомарно, «Сейчас» и «Требования» компактны, маршрут таска задаёт оценка планировщика вместо регулярных выражений; 922 теста зелёные, слепая приёмка 5 из 6 (гонка со старым пустым ключом осталась)"
    },
    {
      "dir": "2026-11-15-audit-dashboard-haiku",
      "title": "Правки аудита 2026-11-15: дашборд, маршрутизация, Haiku",
      "startedAt": "2026-11-15T03:30:28+01:00",
      "finishedAt": "2026-11-15T17:23:21+01:00",
      "minutes": 325,
      "tickets": 7,
      "repairs": 1,
      "tokens": 1163950,
      "result": "Правки аудита: страница «Сейчас», доски, расход и история, сервер дашборда с токеном, класс таска и Haiku-профили с эскалацией на Sonnet, DPAPI-ключ и узкая граница Bash; 865 тестов зелёные, слепая приёмка 29 из 29"
    },
    {
      "dir": "2026-11-08-opus-auto",
      "title": "Opus и гейты без вмешательства пользователя",
      "startedAt": "2026-11-08T16:28:02+01:00",
      "finishedAt": "2026-11-08T19:13:16+01:00",
      "minutes": 164,
      "tickets": 4,
      "repairs": 0,
      "tokens": 148373,
      "result": "Opus-ремонт и ревью ветки, подписи Opus привязаны к прогону, автообновление инструментов, fix-таски не сбрасывают гейты"
    },
    {
      "dir": "2026-11-08-upstream-port-opus",
      "title": "Порт апстрима 2.2.2/2.2.3 и точечный Opus",
      "startedAt": "2026-11-08T14:16:44+01:00",
      "finishedAt": "2026-11-08T16:25:17+01:00",
      "minutes": 121,
      "tickets": 6,
      "repairs": 1,
      "tokens": 385893,
      "result": "Порт апстрима 2.2.2/2.2.3 и точечный Opus по подписанному подтверждению"
    },
    {
      "dir": "2026-11-06-r22d-run-log-hardening",
      "title": "Журнал надёжнее (R22d)",
      "startedAt": "2026-11-06T01:32:19+01:00",
      "finishedAt": "2026-11-06T02:18:42+01:00",
      "minutes": 46,
      "tickets": 2,
      "repairs": 0,
      "tokens": 46237,
      "result": "Журнал прогона надёжнее: предупреждение без run_log.py, тест списка копирования, свод переживает испорченные строки, роль субагента в журнале"
    },
    {
      "dir": "2026-11-06-claude-code-wave2-run-log",
      "title": "Волна 2: журнал прогона и дыры хука (R22, R22a–R22c)",
      "startedAt": "2026-11-06T00:27:56+01:00",
      "finishedAt": "2026-11-06T01:27:14+01:00",
      "minutes": 57,
      "tickets": 3,
      "repairs": 0,
      "tokens": 0,
      "result": "Журнал прогона и report-run, закрыты дыры хука git, accept-edit проверяет worktree"
    },
    {
      "dir": "2026-11-05-claude-code-wave1",
      "title": "Правки по итогам сборки и Claude Code: волна 1 (R01–R06)",
      "startedAt": "2026-11-05T18:34:27+01:00",
      "finishedAt": "2026-11-05T21:34:44+01:00",
      "minutes": 76,
      "tickets": 2,
      "repairs": 2,
      "tokens": 0,
      "result": "Волна 1: отпечатки тасков, accept-edit, запрет git stash у исполнителей, проверка путей и версии Claude Code"
    },
    {
      "dir": "2026-11-03-dashboard-themes",
      "title": "Выбор темы дашборда: несколько информативных видов",
      "startedAt": "2026-11-03T20:17:53+01:00",
      "finishedAt": "2026-11-05T18:09:46+01:00",
      "minutes": 2699,
      "tickets": 11,
      "repairs": 2,
      "tokens": 0,
      "result": "В дашборде восемь видов на выбор, «Обзор» и «Компактный» подогнаны под макеты, лого, заметки по таскам, подписи на полосах Ганта; обновление дашборда читает state.js с BOM"
    },
    {
      "dir": "2026-11-03-audit-fixes",
      "title": "Исправления по аудиту Autopilot 2026-11-03",
      "startedAt": "2026-11-03T16:24:15+00:00",
      "finishedAt": "2026-11-03T20:02:53+01:00",
      "minutes": 147,
      "tickets": 4,
      "repairs": 2,
      "tokens": 0,
      "result": "Закрыты 18 пунктов аудита: общий state_io, проверка зон и путей, точный allowlist моделей, подпись гейтов, документация и CI"
    }
  ],
  "logFailures": 0,
  "planContractDigest": "c14283e12f228421f7ae4602328eded8451790318f711e99c4d3d2a80293de1c",
  "planValidationDigest": "86cae297359abd77220694978b34c940f0cad37688d6e59656a9b18daca92de4"
}
