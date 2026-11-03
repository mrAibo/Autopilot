window.STATE =
{
  "version": 2,
  "slug": "audit-fixes",
  "dir": "2026-11-03-audit-fixes",
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
  "updatedAt": "2026-11-03T20:02:52+01:00",
  "finishedAt": "2026-11-03T20:02:53+01:00",
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
      "finishedAt": "2026-11-03T20:02:49+01:00"
    },
    {
      "id": "plan",
      "status": "done",
      "startedAt": "2026-11-03T16:31:57+00:00",
      "finishedAt": "2026-11-03T17:43:52+01:00"
    },
    {
      "id": "build",
      "status": "done",
      "startedAt": "2026-11-03T17:45:02+01:00",
      "finishedAt": "2026-11-03T19:20:56+01:00"
    },
    {
      "id": "review",
      "status": "done",
      "startedAt": "2026-11-03T19:20:56+01:00",
      "finishedAt": "2026-11-03T19:53:44+01:00"
    },
    {
      "id": "final",
      "status": "done",
      "startedAt": "2026-11-03T19:53:44+01:00",
      "finishedAt": "2026-11-03T20:02:53+01:00"
    }
  ],
  "requirements": {
    "total": 18,
    "done": 18,
    "inTicket": 0,
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
      "fingerprint": "6d458dbee67dc71c5bc32a52eeaf397ab9a85e9e0cc40ed72e9875a40eb39d29",
      "status": "done",
      "startedAt": "2026-11-03T17:45:21+01:00",
      "finishedAt": "2026-11-03T19:00:58+01:00",
      "retries": 0,
      "repairs": 1,
      "repairFindings": [
        "ap.py ~1905: в изолированном режиме без strict testsSource=host ставить только если test_evidence.check подтверждает workerHead/fingerprint текущего HEAD; иначе claimed + строка в debt.assumptions; добавить тест на устаревшее evidence (verify → правка → land --tests)"
      ],
      "tests": {
        "passed": 517,
        "failed": 0
      },
      "commit": "4cfc7be",
      "placeholders": [],
      "routing": {
        "provider": "anthropic",
        "model": "sonnet",
        "effort": "high",
        "effortEnforced": true,
        "score": 50,
        "reason": "score=50; profile=strong; high-risk=True",
        "verified": true,
        "agentType": "autopilot-executor-01-state-safety-routing",
        "agentFile": ".claude/agents/autopilot-executor-01-state-safety-routing.md",
        "profileSha": "ea20ea33350bb5be9da2de28015d78a0124ceba533401bf38d68e9d8c3ca6946"
      },
      "plannedRouting": {
        "ticket": "01",
        "provider": "anthropic",
        "model": "sonnet",
        "effort": "high",
        "effortEnforced": true,
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
        "status": "ready",
        "fingerprint": "6d458dbee67dc71c5bc32a52eeaf397ab9a85e9e0cc40ed72e9875a40eb39d29",
        "hostExecutionVerified": false,
        "applied": true
      },
      "attestation": {
        "model": "claude-sonnet-5-5",
        "effort": "high",
        "lines": 152
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
      "fingerprint": "bfd9f253a15504d8f7469b4eb56b694db8713fcb10beb9ab862583e50ddd4183",
      "status": "done",
      "startedAt": "2026-11-03T17:45:21+01:00",
      "finishedAt": "2026-11-03T17:53:37+01:00",
      "retries": 0,
      "repairs": 0,
      "tests": {
        "passed": 25,
        "failed": 0
      },
      "commit": "79bd014",
      "placeholders": [],
      "routing": {
        "provider": "anthropic",
        "model": "sonnet",
        "effort": "high",
        "effortEnforced": true,
        "score": 55,
        "reason": "score=55; profile=strong; high-risk=False",
        "verified": true,
        "agentType": "autopilot-executor-02-docs-ci-backups",
        "agentFile": ".claude/agents/autopilot-executor-02-docs-ci-backups.md",
        "profileSha": "e9a041197c42ac58918a802c00dc0d1d1aea23f110d18f6d4c2073f23a6b9af8"
      },
      "plannedRouting": {
        "ticket": "02",
        "provider": "anthropic",
        "model": "sonnet",
        "effort": "high",
        "effortEnforced": true,
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
        "status": "ready",
        "fingerprint": "bfd9f253a15504d8f7469b4eb56b694db8713fcb10beb9ab862583e50ddd4183",
        "hostExecutionVerified": false,
        "applied": true
      },
      "attestation": {
        "model": "claude-sonnet-5-5",
        "effort": "high",
        "lines": 58
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
      "fingerprint": "d5f043e96bb4f9113aa67311cd8c18a7c157a75798880d2af4016c9b2d389333",
      "status": "done",
      "startedAt": "2026-11-03T18:18:10+01:00",
      "finishedAt": "2026-11-03T19:53:41+01:00",
      "retries": 0,
      "repairs": 1,
      "repairFindings": [
        "F1: run, начатый подписанным, нельзя понизить правкой state.js (ключ есть, а gateSigned нет или без подписи = стоп, не предупреждение); F2: Write/Edit по .autopilot/*.py верификаторам (gate_sign, claude_agent_guard, claude_attest, ap, test_evidence) запрещены в strict-прогоне"
      ],
      "tests": {
        "passed": 546,
        "failed": 0
      },
      "commit": "84f50cd",
      "placeholders": [],
      "routing": {
        "provider": "anthropic",
        "model": "sonnet",
        "effort": "medium",
        "effortEnforced": true,
        "score": 35,
        "reason": "score=35; profile=balanced; high-risk=False",
        "verified": true,
        "agentType": "autopilot-executor-03-gate-signing-protection",
        "agentFile": ".claude/agents/autopilot-executor-03-gate-signing-protection.md",
        "profileSha": "3284fb911ae093915f46ae369e52fe7b56ca77401ffaa94c1cb311da129ea86c"
      },
      "plannedRouting": {
        "ticket": "03",
        "provider": "anthropic",
        "model": "sonnet",
        "effort": "medium",
        "effortEnforced": true,
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
        "status": "ready",
        "fingerprint": "d5f043e96bb4f9113aa67311cd8c18a7c157a75798880d2af4016c9b2d389333",
        "hostExecutionVerified": false,
        "applied": true
      },
      "attestation": {
        "model": "claude-sonnet-5-5",
        "effort": "medium",
        "lines": 86
      }
    },
    {
      "id": "F1",
      "title": "Ремонт по ревью ветки",
      "requirements": [
        "R05",
        "R17",
        "R06",
        "R12",
        "R18"
      ],
      "blockedBy": [],
      "wave": 3,
      "zone": [
        "skills/autopilot/tools/gate_sign.py",
        "skills/autopilot/tools/claude_agent_guard.py",
        "skills/autopilot/tools/ap.py",
        "skills/autopilot/tools/model_router.py",
        "skills/autopilot/tools/process_containment.py",
        "docs/autopilot/*.md",
        "skills/autopilot/phases/0-resume.md",
        "tests/test_gate_sign.py",
        "tests/test_claude_agent_guard.py",
        "tests/test_ap.py",
        "tests/test_model_router.py",
        "tests/test_process_containment.py",
        "tests/test_skill_allowed_tools.py"
      ],
      "review": "да — ремонт ветки",
      "model": "сильная",
      "fingerprint": "deff2743b0779d529f47d667a3b5dcbd31a06213501a3d631a22bcedd91c666c",
      "status": "done",
      "startedAt": "2026-11-03T19:25:34+01:00",
      "finishedAt": "2026-11-03T19:53:42+01:00",
      "retries": 0,
      "repairs": 0,
      "tests": {
        "passed": 546,
        "failed": 0
      },
      "commit": "84f50cd",
      "placeholders": [],
      "routing": {
        "agentType": "autopilot-executor-repair-2026-11-03-audit-fixes",
        "agentFile": ".claude/agents/autopilot-executor-repair-2026-11-03-audit-fixes.md",
        "model": "sonnet",
        "effort": "high",
        "effortEnforced": true,
        "profileSha": "3172282d8b248f66324f2a495ab8b1b7c1a8ed733ec7169e6120c33e8d86b559",
        "provider": "anthropic",
        "reason": "ремонт ветки: подпись гейта, роутер моделей, контейнмент; сильный",
        "verified": true
      },
      "attestation": {
        "model": "claude-sonnet-5-5",
        "effort": "high",
        "lines": 73
      },
      "attestFrom": 394
    }
  ],
  "tests": {
    "passed": 546,
    "failed": 0
  },
  "usageEvents": [],
  "budgetTokens": null,
  "debt": {
    "placeholders": [],
    "assumptions": [],
    "emptyEnv": []
  },
  "additions": [],
  "coverage": {
    "found": 4,
    "fixed": 1,
    "deferred": 3,
    "items": [
      "A05 strictRouting/finishedAt: закрыто — запись «начат подписанным» вне проекта (F1)",
      "A05 запись через Bash: не закрыта — хук ловит Write/Edit, остаточный предел назван в docs/autopilot/claude-code.md",
      "A05 model-capabilities.json: без подписи, закрыт от Write/Edit хуком",
      "A10 на Windows: автотест внука через skipUnless (POSIX); вручную на Windows проверено, внук убит"
    ]
  },
  "concerns": [
    "T02: py -3.13 остался в docs вне зоны (sequential-host, codex-cli, gui-cli-bridge, host-loop, spend-guard)",
    "T01: land() требует zones — worktrees.md:191 нужен --zone (зона T02); зона .github/ допустима; на Windows run_contained может пропустить внука в первый миг",
    "T01 ревью F2: model_router.py:63 is_allowed_subagent_model('claude-opus-4-1/haiku') даёт True — искать opus/fable и в сыром имени (безопасность)",
    "T01 ревью F3: model_router.py:53 отклоняет claude-3-5-haiku-latest",
    "T01 ревью F4: model_router.py:231 choose_route — второй премиум-чек вместо is_allowed_subagent_model",
    "T01 ревью F5: process_containment.py:158 terminate может поднять ContainmentError до proc.kill; тест внука флачит; нет теста land на rename",
    "T01 ревью F6: scheduler.py:134 и dashboard_upgrade.py:28 — свои разборщики state.js, BOM ломает scheduler CLI",
    "T03 перепроверка: gate_sign.run_mark покрывает dir — finish переименует --wip, маркер станет forged; подписывать slug+startedAt без dir; нет теста finish→reopen",
    "T03: ключ общий на машину — init --strict-routing в другом проекте жёстко останавливает старый неподписанный прогон; в доках нет предупреждения",
    "T03: .autopilot/__pycache__/*.pyc глубины 3 не защищён"
  ],
  "blockingFindings": [
    {
      "id": "B01",
      "text": "ap.py ~1905: в изолированном режиме без strict testsSource=host ставить только если test_evidence.check подтверждает workerHead/fingerprint текущего HEAD; иначе claimed + строка в debt.assumptions; добавить тест на устаревшее evidence (verify → правка → land --tests)",
      "ticket": "01",
      "openedAt": "2026-11-03T18:22:00+01:00",
      "status": "resolved",
      "openedCommit": "47e4ccd",
      "resolvedAt": "2026-11-03T19:00:58+01:00",
      "resolutionCommit": "4cfc7be",
      "resolutionTests": {
        "passed": 517,
        "failed": 0
      },
      "review": "Независимый ревьюер перепроверил условие: host ставится только после test_evidence.check по текущему HEAD, иначе claimed; тесты красные до правки"
    },
    {
      "id": "B02",
      "text": "F1: run, начатый подписанным, нельзя понизить правкой state.js (ключ есть, а gateSigned нет или без подписи = стоп, не предупреждение); F2: Write/Edit по .autopilot/*.py верификаторам (gate_sign, claude_agent_guard, claude_attest, ap, test_evidence) запрещены в strict-прогоне",
      "ticket": "03",
      "openedAt": "2026-11-03T19:03:08+01:00",
      "status": "resolved",
      "openedCommit": "4cfc7be",
      "resolvedAt": "2026-11-03T19:53:40+01:00",
      "resolutionCommit": "84f50cd",
      "resolutionTests": {
        "passed": 546,
        "failed": 0
      },
      "review": "Независимая перепроверка F1: запись «начат подписанным» вне проекта, guard проверяет подпись до «No active strict run»; все критерии закрыты"
    }
  ],
  "blind": {
    "checked": 15,
    "matched": 15,
    "mismatches": []
  },
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
    "2026-11-03T16:33:19+00:00",
    "2026-11-03T17:43:22+01:00",
    "2026-11-03T17:43:42+01:00",
    "2026-11-03T17:43:52+01:00",
    "2026-11-03T17:43:57+01:00",
    "2026-11-03T17:44:58+01:00",
    "2026-11-03T17:45:02+01:00",
    "2026-11-03T17:45:21+01:00",
    "2026-11-03T17:53:37+01:00",
    "2026-11-03T17:53:44+01:00",
    "2026-11-03T18:18:07+01:00",
    "2026-11-03T18:18:09+01:00",
    "2026-11-03T18:18:10+01:00",
    "2026-11-03T18:18:21+01:00",
    "2026-11-03T18:21:51+01:00",
    "2026-11-03T18:22:00+01:00",
    "2026-11-03T18:49:29+01:00",
    "2026-11-03T19:00:58+01:00",
    "2026-11-03T19:00:59+01:00",
    "2026-11-03T19:03:08+01:00",
    "2026-11-03T19:20:43+01:00",
    "2026-11-03T19:20:56+01:00",
    "2026-11-03T19:25:23+01:00",
    "2026-11-03T19:25:24+01:00",
    "2026-11-03T19:25:34+01:00",
    "2026-11-03T19:45:46+01:00",
    "2026-11-03T19:53:40+01:00",
    "2026-11-03T19:53:41+01:00",
    "2026-11-03T19:53:42+01:00",
    "2026-11-03T19:53:43+01:00",
    "2026-11-03T19:53:44+01:00",
    "2026-11-03T19:59:59+01:00",
    "2026-11-03T20:02:11+01:00",
    "2026-11-03T20:02:12+01:00",
    "2026-11-03T20:02:37+01:00",
    "2026-11-03T20:02:49+01:00",
    "2026-11-03T20:02:50+01:00",
    "2026-11-03T20:02:51+01:00",
    "2026-11-03T20:02:52+01:00"
  ],
  "rev": 64,
  "waiting": null,
  "waits": [
    {
      "kind": "briefing",
      "from": "2026-11-03T16:25:03+00:00",
      "to": "2026-11-03T16:26:04+00:00"
    },
    {
      "kind": "stop",
      "from": "2026-11-03T16:33:19+00:00",
      "to": "2026-11-03T17:43:22+01:00"
    },
    {
      "kind": "stop",
      "from": "2026-11-03T17:43:57+01:00",
      "to": "2026-11-03T17:44:58+01:00"
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
    },
    {
      "t": "2026-11-03T17:43:22+01:00",
      "k": "answered",
      "kind": "stop"
    },
    {
      "t": "2026-11-03T17:43:22+01:00",
      "k": "gate",
      "g": "G3",
      "ok": true,
      "problems": 0
    },
    {
      "t": "2026-11-03T17:43:22+01:00",
      "k": "gate",
      "g": "G1",
      "ok": false,
      "reason": "plan-changed"
    },
    {
      "t": "2026-11-03T17:43:22+01:00",
      "k": "gate",
      "g": "G2",
      "ok": false,
      "reason": "plan-changed"
    },
    {
      "t": "2026-11-03T17:43:22+01:00",
      "k": "gate",
      "g": "G4",
      "ok": false,
      "reason": "plan-changed"
    },
    {
      "t": "2026-11-03T17:43:42+01:00",
      "k": "plan-models",
      "provider": "anthropic",
      "applied": false,
      "tickets": 3,
      "blocked": 0
    },
    {
      "t": "2026-11-03T17:43:52+01:00",
      "k": "stage",
      "id": "plan",
      "act": "done"
    },
    {
      "t": "2026-11-03T17:43:52+01:00",
      "k": "plan-models",
      "provider": "anthropic",
      "applied": true,
      "tickets": 3,
      "blocked": 0
    },
    {
      "t": "2026-11-03T17:43:57+01:00",
      "k": "ask",
      "kind": "stop",
      "note": "новый чат: агенты зарегистрированы"
    },
    {
      "t": "2026-11-03T17:44:58+01:00",
      "k": "answered",
      "kind": "stop"
    },
    {
      "t": "2026-11-03T17:44:58+01:00",
      "k": "gate",
      "g": "G3",
      "ok": true,
      "problems": 0
    },
    {
      "t": "2026-11-03T17:45:02+01:00",
      "k": "stage",
      "id": "build",
      "act": "start"
    },
    {
      "t": "2026-11-03T17:45:21+01:00",
      "k": "ticket",
      "ids": [
        "01",
        "02"
      ],
      "act": "start"
    },
    {
      "t": "2026-11-03T17:53:37+01:00",
      "k": "ticket",
      "ids": [
        "02"
      ],
      "act": "done",
      "tests": {
        "passed": 25,
        "failed": 0
      }
    },
    {
      "t": "2026-11-03T17:53:44+01:00",
      "k": "add",
      "key": "concerns",
      "n": 1
    },
    {
      "t": "2026-11-03T18:18:07+01:00",
      "k": "ticket",
      "ids": [
        "01"
      ],
      "act": "done",
      "tests": {
        "passed": 499,
        "failed": 0
      }
    },
    {
      "t": "2026-11-03T18:18:09+01:00",
      "k": "add",
      "key": "concerns",
      "n": 1
    },
    {
      "t": "2026-11-03T18:18:10+01:00",
      "k": "ticket",
      "ids": [
        "03"
      ],
      "act": "start"
    },
    {
      "t": "2026-11-03T18:18:21+01:00",
      "k": "ticket",
      "ids": [
        "01"
      ],
      "act": "review"
    },
    {
      "t": "2026-11-03T18:21:51+01:00",
      "k": "add",
      "key": "concerns",
      "n": 5
    },
    {
      "t": "2026-11-03T18:22:00+01:00",
      "k": "blocker",
      "id": "B01",
      "act": "open",
      "ticket": "01"
    },
    {
      "t": "2026-11-03T18:22:00+01:00",
      "k": "ticket",
      "ids": [
        "01"
      ],
      "act": "repair",
      "note": "ap.py ~1905: в изолированном режиме без strict testsSource=host ставить только если test_evidence.check подтверждает workerHead/fingerprint текущего HEAD; иначе claimed + строка в debt.assumptions; добавить тест на устаревшее evidence (verify → правка → land --tests)"
    },
    {
      "t": "2026-11-03T18:49:29+01:00",
      "k": "ticket",
      "ids": [
        "03"
      ],
      "act": "review"
    },
    {
      "t": "2026-11-03T19:00:58+01:00",
      "k": "blocker",
      "id": "B01",
      "act": "resolve",
      "ticket": "01"
    },
    {
      "t": "2026-11-03T19:00:58+01:00",
      "k": "ticket",
      "ids": [
        "01"
      ],
      "act": "done",
      "tests": {
        "passed": 517,
        "failed": 0
      }
    },
    {
      "t": "2026-11-03T19:00:59+01:00",
      "k": "ticket",
      "ids": [
        "03"
      ],
      "act": "review"
    },
    {
      "t": "2026-11-03T19:03:08+01:00",
      "k": "blocker",
      "id": "B02",
      "act": "open",
      "ticket": "03"
    },
    {
      "t": "2026-11-03T19:03:08+01:00",
      "k": "ticket",
      "ids": [
        "03"
      ],
      "act": "repair",
      "note": "F1: run, начатый подписанным, нельзя понизить правкой state.js (ключ есть, а gateSigned нет или без подписи = стоп, не предупреждение); F2: Write/Edit по .autopilot/*.py верификаторам (gate_sign, claude_agent_guard, claude_attest, ap, test_evidence) запрещены в strict-прогоне"
    },
    {
      "t": "2026-11-03T19:20:43+01:00",
      "k": "add",
      "key": "concerns",
      "n": 3
    },
    {
      "t": "2026-11-03T19:20:56+01:00",
      "k": "stage",
      "id": "review",
      "act": "start"
    },
    {
      "t": "2026-11-03T19:25:23+01:00",
      "k": "tickets",
      "n": 4
    },
    {
      "t": "2026-11-03T19:25:24+01:00",
      "k": "ticket",
      "ids": [
        "F1"
      ],
      "act": "route"
    },
    {
      "t": "2026-11-03T19:25:34+01:00",
      "k": "ticket",
      "ids": [
        "F1"
      ],
      "act": "start"
    },
    {
      "t": "2026-11-03T19:45:46+01:00",
      "k": "ticket",
      "ids": [
        "F1"
      ],
      "act": "review"
    },
    {
      "t": "2026-11-03T19:53:40+01:00",
      "k": "blocker",
      "id": "B02",
      "act": "resolve",
      "ticket": "03"
    },
    {
      "t": "2026-11-03T19:53:41+01:00",
      "k": "ticket",
      "ids": [
        "03"
      ],
      "act": "done",
      "tests": {
        "passed": 546,
        "failed": 0
      }
    },
    {
      "t": "2026-11-03T19:53:42+01:00",
      "k": "ticket",
      "ids": [
        "F1"
      ],
      "act": "done",
      "tests": {
        "passed": 546,
        "failed": 0
      }
    },
    {
      "t": "2026-11-03T19:53:43+01:00",
      "k": "add",
      "key": "report",
      "n": 6
    },
    {
      "t": "2026-11-03T19:53:44+01:00",
      "k": "stage",
      "id": "final",
      "act": "start"
    },
    {
      "t": "2026-11-03T19:59:59+01:00",
      "k": "gate",
      "g": "G4",
      "ok": false,
      "checked": 15,
      "matched": 13
    },
    {
      "t": "2026-11-03T19:59:59+01:00",
      "k": "tests",
      "passed": 546,
      "failed": 0
    },
    {
      "t": "2026-11-03T20:02:11+01:00",
      "k": "gate",
      "g": "G2",
      "ok": true,
      "found": 4,
      "fixed": 1,
      "deferred": 3
    },
    {
      "t": "2026-11-03T20:02:12+01:00",
      "k": "gate",
      "g": "G1",
      "ok": true,
      "open": 0,
      "total": 18
    },
    {
      "t": "2026-11-03T20:02:12+01:00",
      "k": "stage",
      "id": "spec",
      "act": "done"
    },
    {
      "t": "2026-11-03T20:02:37+01:00",
      "k": "gate",
      "g": "G4",
      "ok": true,
      "checked": 15,
      "matched": 15
    },
    {
      "t": "2026-11-03T20:02:49+01:00",
      "k": "gate",
      "g": "G3",
      "ok": true,
      "problems": 0
    },
    {
      "t": "2026-11-03T20:02:49+01:00",
      "k": "gate",
      "g": "G1",
      "ok": false,
      "reason": "plan-changed"
    },
    {
      "t": "2026-11-03T20:02:49+01:00",
      "k": "gate",
      "g": "G2",
      "ok": false,
      "reason": "plan-changed"
    },
    {
      "t": "2026-11-03T20:02:49+01:00",
      "k": "gate",
      "g": "G4",
      "ok": false,
      "reason": "plan-changed"
    },
    {
      "t": "2026-11-03T20:02:49+01:00",
      "k": "gate",
      "g": "G1",
      "ok": true,
      "open": 0,
      "total": 18
    },
    {
      "t": "2026-11-03T20:02:49+01:00",
      "k": "stage",
      "id": "spec",
      "act": "done"
    },
    {
      "t": "2026-11-03T20:02:50+01:00",
      "k": "gate",
      "g": "G2",
      "ok": true,
      "found": 4,
      "fixed": 1,
      "deferred": 3
    },
    {
      "t": "2026-11-03T20:02:51+01:00",
      "k": "gate",
      "g": "G4",
      "ok": true,
      "checked": 15,
      "matched": 15
    },
    {
      "t": "2026-11-03T20:02:52+01:00",
      "k": "tests",
      "passed": 546,
      "failed": 0
    },
    {
      "t": "2026-11-03T20:02:52+01:00",
      "k": "finish",
      "result": "Закрыты 18 пунктов аудита: общий state_io, проверка зон и путей, точный allowlist моделей, подпись гейтов, документация и CI"
    }
  ],
  "reqList": [
    {
      "id": "R01",
      "text": "«A01: save() делает os.replace без повтора»",
      "status": "done"
    },
    {
      "id": "R02",
      "text": "«A02: land() не проверяет зоны и пути; тесты берутся из текста --tests N/0»",
      "status": "done"
    },
    {
      "id": "R03",
      "text": "«A03: git diff --cached --name-only без --no-renames»",
      "status": "done"
    },
    {
      "id": "R04",
      "text": "«A04: риск тикета считается только по словарю слов»",
      "status": "done"
    },
    {
      "id": "R05",
      "text": "«A05: гард защищает от промахов оркестратора, не от исполнителя»",
      "status": "done"
    },
    {
      "id": "R06",
      "text": "«A06: запрет премиум-моделей по префиксу строки»",
      "status": "done"
    },
    {
      "id": "R07",
      "text": "«A07: четыре разборщика state.js с разной терпимостью»",
      "status": "done"
    },
    {
      "id": "R08",
      "text": "«A08: init --force теряет журнал»",
      "status": "done"
    },
    {
      "id": "R09",
      "text": "«A09: classify смотрит только первые 12 000 символов»",
      "status": "done"
    },
    {
      "id": "R10",
      "text": "«A10: trusted-раннер не использует OwnedJob»",
      "status": "done"
    },
    {
      "id": "R11",
      "text": "«A11: версии не сходятся»",
      "status": "done"
    },
    {
      "id": "R12",
      "text": "«A12: доки велят py -3.13 … и controller.py, а allowed-tools пропускает только py -3 .autopilot/ap.py »",
      "status": "done"
    },
    {
      "id": "R13",
      "text": "«A13: в таблице и скоринге нет tier critical»",
      "status": "done"
    },
    {
      "id": "R14",
      "text": "«A14: бэкап HTML со снимком state.js в общем tempdir»",
      "status": "done"
    },
    {
      "id": "R15",
      "text": "«A15: compileall только skills/autopilot/tools и tests»",
      "status": "done"
    },
    {
      "id": "R16",
      "text": "«I01: общий модуль чтения/записи state.js (BOM, префикс, повтор replace) — закрывает A01 и A07 разом»",
      "status": "done"
    },
    {
      "id": "R17",
      "text": "«I02: подписанные квитанции гейтов, ключ вне .autopilot — иначе правка state.js/attestations.jsonl проходит сверку (A05)»",
      "status": "done"
    },
    {
      "id": "R18",
      "text": "«I03: точный allowlist моделей в роутере вместо префиксов + тесты на Bedrock-ID и claude-3-opus (A06)»",
      "status": "done"
    }
  ],
  "gates": {
    "G1": {
      "ok": true,
      "at": "2026-11-03T20:02:49+01:00",
      "open": 0,
      "total": 18
    },
    "G2": {
      "ok": true,
      "at": "2026-11-03T20:02:50+01:00",
      "found": 4,
      "fixed": 1,
      "deferred": 3
    },
    "G3": {
      "ok": true,
      "at": "2026-11-03T20:02:49+01:00",
      "problems": 0
    },
    "G4": {
      "ok": true,
      "at": "2026-11-03T20:02:51+01:00",
      "checked": 15,
      "matched": 15
    }
  },
  "result": "Закрыты 18 пунктов аудита: общий state_io, проверка зон и путей, точный allowlist моделей, подпись гейтов, документация и CI",
  "skillVersion": "2.6.0",
  "planContractDigest": "c46c585cd2f5011d7cb9fd308805ab875991dbf03fb72492150624cde62d64f0",
  "planValidationDigest": "c950f095a53552a7ede06fde7e50789c1b64c73e45778806a447724cec06b2d0",
  "roleAgents": {
    "reviewer": {
      "agentType": "autopilot-reviewer-2026-11-03-audit-fixes",
      "agentFile": ".claude/agents/autopilot-reviewer-2026-11-03-audit-fixes.md",
      "model": "sonnet",
      "effort": "high",
      "effortEnforced": true,
      "profileSha": "c0ce8d027e934dd42a0de465211a7d9e3be521053c5557a02a6438f33b717c52"
    },
    "acceptance": {
      "agentType": "autopilot-acceptance-2026-11-03-audit-fixes",
      "agentFile": ".claude/agents/autopilot-acceptance-2026-11-03-audit-fixes.md",
      "model": "sonnet",
      "effort": "medium",
      "effortEnforced": true,
      "profileSha": "f6e4056522333decb3f59778120895d06d50c03f3b192838cf5eae09eb48c24a"
    },
    "explorer": {
      "agentType": "autopilot-explorer-2026-11-03-audit-fixes",
      "agentFile": ".claude/agents/autopilot-explorer-2026-11-03-audit-fixes.md",
      "model": "haiku",
      "effort": "low",
      "effortEnforced": true,
      "profileSha": "4f8147a1a7e337d4f62e6edb70284103d97150881b953fbdf6ad572feec6e2c0"
    }
  },
  "repairAgent": {
    "agentType": "autopilot-executor-repair-2026-11-03-audit-fixes",
    "agentFile": ".claude/agents/autopilot-executor-repair-2026-11-03-audit-fixes.md",
    "model": "sonnet",
    "effort": "high",
    "effortEnforced": true,
    "profileSha": "3172282d8b248f66324f2a495ab8b1b7c1a8ed733ec7169e6120c33e8d86b559"
  },
  "report": [
    "execution sequential-host стирает запись подписи, но оставляет gateMark: ap.py:985,1586, предупреждение «без подписи» неточно, подписи маршрута и тестов дальше не ставятся",
    "Запись подписи пишется до save(state) и не атомарна (ap.py:2286, 2311): сбой между ними — прогон читается как forged до повторного init",
    "scheduler.py:135 и dashboard_upgrade.py:28 разбирают state.js вручную: BOM ломает scheduler CLI и обновление дашборда",
    "claude-3-5-haiku-latest отклоняется роутером (fail-closed)",
    ".autopilot/__pycache__/*.pyc глубины 3 не защищён Write-хуком",
    "Мелочи: ap.py:1925 ловит только EvidenceError; init создаёт ключ раньше отказа; chmod 0700 на чужой папке в /tmp"
  ]
}
