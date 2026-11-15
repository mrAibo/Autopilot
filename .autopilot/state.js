window.STATE =
{
  "version": 2,
  "slug": "dashboard-token-fixes",
  "dir": "2026-11-15-dashboard-token-fixes",
  "title": "Доделки после аудита: токен дашборда, ключ подписи, спека",
  "mode": "semi",
  "depth": "normal",
  "tier": "T0",
  "strictRouting": false,
  "gateSigned": false,
  "sequentialHost": false,
  "isolateTickets": false,
  "briefFile": "2026-11-15-brief.md",
  "memoryFile": "AGENTS.md",
  "memoryOwner": "autopilot",
  "skillDir": "C:/Users/crown/Downloads/Projects/Autopilot/skills/autopilot",
  "baseCommit": "52f4909",
  "startedAt": "2026-11-15T20:36:48+01:00",
  "updatedAt": "2026-11-15T23:03:26+01:00",
  "finishedAt": "2026-11-15T23:03:26+01:00",
  "stages": [
    {
      "id": "preflight",
      "status": "done",
      "startedAt": "2026-11-15T20:36:48+01:00",
      "segments": [
        {
          "startedAt": "2026-11-15T20:36:48+01:00",
          "finishedAt": "2026-11-15T20:37:00+01:00"
        }
      ],
      "finishedAt": "2026-11-15T20:37:00+01:00"
    },
    {
      "id": "manifest",
      "status": "done",
      "segments": [
        {
          "startedAt": "2026-11-15T20:37:00+01:00",
          "finishedAt": "2026-11-15T20:37:06+01:00"
        }
      ],
      "startedAt": "2026-11-15T20:37:00+01:00",
      "finishedAt": "2026-11-15T20:37:06+01:00"
    },
    {
      "id": "briefing",
      "status": "done",
      "segments": [
        {
          "startedAt": "2026-11-15T20:37:06+01:00",
          "finishedAt": "2026-11-15T20:41:03+01:00"
        }
      ],
      "startedAt": "2026-11-15T20:37:06+01:00",
      "finishedAt": "2026-11-15T20:41:03+01:00"
    },
    {
      "id": "spec",
      "status": "done",
      "segments": [
        {
          "startedAt": "2026-11-15T20:41:04+01:00",
          "finishedAt": "2026-11-15T20:47:01+01:00"
        }
      ],
      "startedAt": "2026-11-15T20:41:04+01:00",
      "finishedAt": "2026-11-15T20:47:01+01:00"
    },
    {
      "id": "plan",
      "status": "done",
      "segments": [
        {
          "startedAt": "2026-11-15T20:47:02+01:00",
          "finishedAt": "2026-11-15T20:52:41+01:00"
        }
      ],
      "startedAt": "2026-11-15T20:47:02+01:00",
      "finishedAt": "2026-11-15T20:52:41+01:00"
    },
    {
      "id": "build",
      "status": "done",
      "segments": [
        {
          "startedAt": "2026-11-15T20:52:42+01:00",
          "finishedAt": "2026-11-15T21:35:08+01:00"
        }
      ],
      "startedAt": "2026-11-15T20:52:42+01:00",
      "finishedAt": "2026-11-15T21:35:08+01:00"
    },
    {
      "id": "review",
      "status": "done",
      "segments": [
        {
          "startedAt": "2026-11-15T21:35:08+01:00",
          "finishedAt": "2026-11-15T22:00:21+01:00"
        }
      ],
      "startedAt": "2026-11-15T21:35:08+01:00",
      "finishedAt": "2026-11-15T22:00:21+01:00"
    },
    {
      "id": "final",
      "status": "done",
      "segments": [
        {
          "startedAt": "2026-11-15T22:00:33+01:00",
          "finishedAt": "2026-11-15T23:03:26+01:00"
        }
      ],
      "startedAt": "2026-11-15T22:00:33+01:00",
      "finishedAt": "2026-11-15T23:03:26+01:00"
    }
  ],
  "requirements": {
    "total": 7,
    "done": 6,
    "inTicket": 0,
    "inSpec": 0,
    "placeholder": 0,
    "deferred": 1,
    "dropped": 0
  },
  "tickets": [
    {
      "id": "01",
      "title": "Доделки после аудита: токен, ключ, правила, компактный дашборд, оценка планировщика",
      "requirements": [
        "R01",
        "R02",
        "R03",
        "R04",
        "R05",
        "R07"
      ],
      "blockedBy": [],
      "wave": 1,
      "zone": [
        "skills/autopilot/tools/ap.py",
        "skills/autopilot/tools/gate_sign.py",
        "skills/autopilot/tools/model_router.py",
        "skills/autopilot/tools/agent_profiles.py",
        "skills/autopilot/phases/dashboard-template.html",
        "skills/autopilot/phases/4-plan.md",
        "skills/autopilot/phases/1-manifest.md",
        "skills/autopilot/phases/8-final.md",
        "skills/autopilot/phases/0-instruments.md",
        "docs/autopilot/model-routing.md",
        "docs/autopilot/dashboard-views.md",
        "docs/adr/",
        "AGENTS.md",
        "tests/"
      ],
      "review": "нет",
      "model": "сильная",
      "fingerprint": "c46ebe81288578aa7bc3d508b6ebc2ee7e209a58c6be51ca379d558f5b944853",
      "status": "done",
      "startedAt": "2026-11-15T20:52:42+01:00",
      "finishedAt": "2026-11-15T21:35:06+01:00",
      "retries": 0,
      "repairs": 0,
      "tests": {
        "passed": 910,
        "failed": 0
      },
      "commit": "b5f3850",
      "placeholders": [],
      "plannedRouting": {
        "ticket": "01",
        "provider": "anthropic",
        "model": "sonnet",
        "effort": "xhigh",
        "effortEnforced": null,
        "profile": "critical",
        "score": 70,
        "factors": {
          "algorithm": 20,
          "coupling": 20,
          "uncertainty": 0,
          "context": 10,
          "testing": 10,
          "risk": 10
        },
        "reason": "score=70; profile=critical; high-risk=True",
        "requiresReview": true,
        "status": "blocked",
        "fingerprint": "c46ebe81288578aa7bc3d508b6ebc2ee7e209a58c6be51ca379d558f5b944853",
        "hostExecutionVerified": false,
        "error": "No verified host capabilities",
        "applied": false
      }
    },
    {
      "id": "F1",
      "title": "Правки по код-ревью ветки",
      "requirements": [
        "R01",
        "R02"
      ],
      "blockedBy": [],
      "wave": 2,
      "zone": [
        "skills/autopilot/tools/ap.py",
        "tests/test_followups_token.py",
        "tests/test_ap_audit.py"
      ],
      "review": "да — ремонт ветки",
      "model": "сильная",
      "fingerprint": "625815a0bade5d97a9977fdb48d63391a27d84be731403f2a4e20554afbdb46c",
      "status": "done",
      "startedAt": "2026-11-15T22:00:19+01:00",
      "finishedAt": "2026-11-15T22:00:19+01:00",
      "retries": 0,
      "repairs": 0,
      "tests": {
        "passed": 918,
        "failed": 0
      },
      "commit": "e9fcc9b",
      "placeholders": []
    },
    {
      "id": "F2",
      "title": "Правки по слепой приёмке: голый `ap.py` без токена, гонка со старым пустым ключом",
      "requirements": [
        "R02",
        "R03"
      ],
      "blockedBy": [],
      "wave": 3,
      "zone": [
        "skills/autopilot/tools/ap.py",
        "skills/autopilot/tools/gate_sign.py",
        "skills/autopilot/phases/0-instruments.md",
        "AGENTS.md",
        "tests/test_followups_token.py",
        "tests/test_followups_key.py",
        "tests/test_ap_audit.py"
      ],
      "review": "нет",
      "model": "сильная",
      "fingerprint": "738ec364fcf898ef20cdd4620962ac1b5e0fb803ebe67440733dac4290e908ec",
      "status": "done",
      "startedAt": "2026-11-15T22:08:28+01:00",
      "finishedAt": "2026-11-15T22:20:00+01:00",
      "retries": 0,
      "repairs": 0,
      "tests": {
        "passed": 919,
        "failed": 0
      },
      "commit": "65adce3",
      "placeholders": []
    },
    {
      "id": "F3",
      "title": "Калибровка роутера: «обычный» не уходит на Haiku, зона по целым сегментам",
      "requirements": [
        "R07"
      ],
      "blockedBy": [],
      "wave": 4,
      "zone": [
        "skills/autopilot/tools/model_router.py",
        "skills/autopilot/phases/4-plan.md",
        "docs/autopilot/model-routing.md",
        "docs/adr/0007-planner-assessment-instead-of-regex.md",
        "tests/test_followups_routing.py",
        "tests/test_audit_routing.py",
        "tests/test_model_router.py",
        "tests/test_ap.py",
        "tests/test_offline_supervisor.py",
        "tests/test_host_loop.py"
      ],
      "review": "нет",
      "model": "сильная",
      "fingerprint": "1bec5f47b6b147c901e5fff530b88608cc95aa3da6b649b1e7f318cd2d2a3c3f",
      "status": "done",
      "startedAt": "2026-11-15T23:02:36+01:00",
      "finishedAt": "2026-11-15T23:02:36+01:00",
      "retries": 0,
      "repairs": 0,
      "tests": {
        "passed": 922,
        "failed": 0
      },
      "commit": "297ac3a",
      "placeholders": []
    }
  ],
  "tests": {
    "passed": 922,
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
    "fixed": 2,
    "deferred": 2,
    "items": [
      "компактность досок, панели таска и «нужен твой ответ» — вне рамок: пользователь выбрал A+B",
      "выбор моделей ролей — вне рамок: R07 про маршрут таска"
    ]
  },
  "concerns": [],
  "blockingFindings": [],
  "blind": {
    "checked": 6,
    "matched": 5,
    "mismatches": [
      "R03 — при старом пустом gate.key одновременный запуск из 8 процессов по 4 потока в 6 из 28 прогонов даёт два разных ключа или читателя без ключа (свежий и полный ключ в порядке)"
    ]
  },
  "beats": [
    "2026-11-15T20:36:48+01:00",
    "2026-11-15T20:36:59+01:00",
    "2026-11-15T20:37:00+01:00",
    "2026-11-15T20:37:06+01:00",
    "2026-11-15T20:37:07+01:00",
    "2026-11-15T20:41:02+01:00",
    "2026-11-15T20:41:03+01:00",
    "2026-11-15T20:41:04+01:00",
    "2026-11-15T20:47:00+01:00",
    "2026-11-15T20:47:01+01:00",
    "2026-11-15T20:47:02+01:00",
    "2026-11-15T20:52:20+01:00",
    "2026-11-15T20:52:21+01:00",
    "2026-11-15T20:52:22+01:00",
    "2026-11-15T20:52:28+01:00",
    "2026-11-15T20:52:31+01:00",
    "2026-11-15T20:52:40+01:00",
    "2026-11-15T20:52:41+01:00",
    "2026-11-15T20:52:42+01:00",
    "2026-11-15T21:35:05+01:00",
    "2026-11-15T21:35:06+01:00",
    "2026-11-15T21:35:07+01:00",
    "2026-11-15T21:35:08+01:00",
    "2026-11-15T21:35:09+01:00",
    "2026-11-15T21:35:10+01:00",
    "2026-11-15T21:35:23+01:00",
    "2026-11-15T21:49:47+01:00",
    "2026-11-15T21:59:05+01:00",
    "2026-11-15T22:00:19+01:00",
    "2026-11-15T22:00:20+01:00",
    "2026-11-15T22:00:21+01:00",
    "2026-11-15T22:00:33+01:00",
    "2026-11-15T22:08:23+01:00",
    "2026-11-15T22:08:27+01:00",
    "2026-11-15T22:08:28+01:00",
    "2026-11-15T22:20:00+01:00",
    "2026-11-15T22:20:01+01:00",
    "2026-11-15T22:27:32+01:00",
    "2026-11-15T22:27:55+01:00",
    "2026-11-15T22:27:56+01:00",
    "2026-11-15T22:34:45+01:00",
    "2026-11-15T22:53:46+01:00",
    "2026-11-15T23:02:35+01:00",
    "2026-11-15T23:02:36+01:00",
    "2026-11-15T23:02:37+01:00",
    "2026-11-15T23:02:52+01:00",
    "2026-11-15T23:02:53+01:00",
    "2026-11-15T23:02:54+01:00",
    "2026-11-15T23:02:55+01:00",
    "2026-11-15T23:02:56+01:00",
    "2026-11-15T23:02:57+01:00",
    "2026-11-15T23:02:58+01:00",
    "2026-11-15T23:03:25+01:00",
    "2026-11-15T23:03:26+01:00"
  ],
  "rev": 58,
  "waiting": null,
  "waits": [
    {
      "kind": "briefing",
      "from": "2026-11-15T20:37:07+01:00",
      "to": "2026-11-15T20:41:02+01:00"
    }
  ],
  "log": [
    {
      "t": "2026-11-15T20:36:48+01:00",
      "k": "init"
    },
    {
      "t": "2026-11-15T20:37:00+01:00",
      "k": "stage",
      "id": "manifest",
      "act": "start"
    },
    {
      "t": "2026-11-15T20:37:06+01:00",
      "k": "stage",
      "id": "briefing",
      "act": "start"
    },
    {
      "t": "2026-11-15T20:37:07+01:00",
      "k": "ask",
      "kind": "briefing",
      "note": "один вопрос в чате: что сжать на дашборде (R05)"
    },
    {
      "t": "2026-11-15T20:41:02+01:00",
      "k": "answered",
      "kind": "briefing"
    },
    {
      "t": "2026-11-15T20:41:03+01:00",
      "k": "stage",
      "id": "briefing",
      "act": "done"
    },
    {
      "t": "2026-11-15T20:41:04+01:00",
      "k": "gate",
      "g": "G1",
      "ok": false,
      "open": 6,
      "total": 7
    },
    {
      "t": "2026-11-15T20:41:04+01:00",
      "k": "stage",
      "id": "spec",
      "act": "start"
    },
    {
      "t": "2026-11-15T20:47:00+01:00",
      "k": "gate",
      "g": "G2",
      "ok": false,
      "found": 6,
      "fixed": 2,
      "deferred": 2
    },
    {
      "t": "2026-11-15T20:47:00+01:00",
      "k": "gate",
      "g": "G1",
      "ok": true,
      "open": 0,
      "total": 7
    },
    {
      "t": "2026-11-15T20:47:01+01:00",
      "k": "stage",
      "id": "spec",
      "act": "done"
    },
    {
      "t": "2026-11-15T20:47:02+01:00",
      "k": "stage",
      "id": "plan",
      "act": "start"
    },
    {
      "t": "2026-11-15T20:52:20+01:00",
      "k": "tier",
      "v": "T0"
    },
    {
      "t": "2026-11-15T20:52:21+01:00",
      "k": "tickets",
      "n": 1
    },
    {
      "t": "2026-11-15T20:52:22+01:00",
      "k": "gate",
      "g": "G3",
      "ok": true,
      "problems": 0
    },
    {
      "t": "2026-11-15T20:52:28+01:00",
      "k": "plan-models",
      "provider": "anthropic",
      "applied": false,
      "tickets": 1,
      "blocked": 1
    },
    {
      "t": "2026-11-15T20:52:31+01:00",
      "k": "plan-models",
      "provider": "anthropic",
      "applied": false,
      "tickets": 1,
      "blocked": 1
    },
    {
      "t": "2026-11-15T20:52:41+01:00",
      "k": "stage",
      "id": "plan",
      "act": "done"
    },
    {
      "t": "2026-11-15T20:52:42+01:00",
      "k": "stage",
      "id": "build",
      "act": "start"
    },
    {
      "t": "2026-11-15T20:52:42+01:00",
      "k": "ticket",
      "ids": [
        "01"
      ],
      "act": "start"
    },
    {
      "t": "2026-11-15T21:35:05+01:00",
      "k": "ticket",
      "ids": [
        "01"
      ],
      "act": "review"
    },
    {
      "t": "2026-11-15T21:35:06+01:00",
      "k": "ticket",
      "ids": [
        "01"
      ],
      "act": "done",
      "tests": {
        "passed": 910,
        "failed": 0
      }
    },
    {
      "t": "2026-11-15T21:35:07+01:00",
      "k": "tests",
      "passed": 910,
      "failed": 0
    },
    {
      "t": "2026-11-15T21:35:08+01:00",
      "k": "stage",
      "id": "build",
      "act": "done"
    },
    {
      "t": "2026-11-15T21:35:08+01:00",
      "k": "stage",
      "id": "review",
      "act": "start"
    },
    {
      "t": "2026-11-15T21:35:09+01:00",
      "k": "tickets",
      "n": 2
    },
    {
      "t": "2026-11-15T21:35:10+01:00",
      "k": "ticket",
      "ids": [
        "F1"
      ],
      "act": "start"
    },
    {
      "t": "2026-11-15T21:35:23+01:00",
      "k": "ticket-reset",
      "id": "F1",
      "reason": "ticket-edited"
    },
    {
      "t": "2026-11-15T21:35:23+01:00",
      "k": "tickets",
      "n": 2
    },
    {
      "t": "2026-11-15T21:49:47+01:00",
      "k": "tickets",
      "n": 2
    },
    {
      "t": "2026-11-15T21:59:05+01:00",
      "k": "ticket",
      "ids": [
        "F1"
      ],
      "act": "review"
    },
    {
      "t": "2026-11-15T22:00:19+01:00",
      "k": "ticket",
      "ids": [
        "F1"
      ],
      "act": "done",
      "tests": {
        "passed": 918,
        "failed": 0
      }
    },
    {
      "t": "2026-11-15T22:00:20+01:00",
      "k": "tests",
      "passed": 918,
      "failed": 0
    },
    {
      "t": "2026-11-15T22:00:21+01:00",
      "k": "stage",
      "id": "review",
      "act": "done"
    },
    {
      "t": "2026-11-15T22:00:33+01:00",
      "k": "stage",
      "id": "final",
      "act": "start"
    },
    {
      "t": "2026-11-15T22:08:23+01:00",
      "k": "gate",
      "g": "G4",
      "ok": false,
      "checked": 6,
      "matched": 4
    },
    {
      "t": "2026-11-15T22:08:27+01:00",
      "k": "tickets",
      "n": 3
    },
    {
      "t": "2026-11-15T22:08:28+01:00",
      "k": "ticket",
      "ids": [
        "F2"
      ],
      "act": "start"
    },
    {
      "t": "2026-11-15T22:20:00+01:00",
      "k": "ticket",
      "ids": [
        "F2"
      ],
      "act": "done",
      "tests": {
        "passed": 919,
        "failed": 0
      }
    },
    {
      "t": "2026-11-15T22:20:01+01:00",
      "k": "tests",
      "passed": 919,
      "failed": 0
    },
    {
      "t": "2026-11-15T22:27:32+01:00",
      "k": "gate",
      "g": "G4",
      "ok": false,
      "checked": 6,
      "matched": 5
    },
    {
      "t": "2026-11-15T22:27:55+01:00",
      "k": "tickets",
      "n": 4
    },
    {
      "t": "2026-11-15T22:27:56+01:00",
      "k": "ticket",
      "ids": [
        "F3"
      ],
      "act": "start"
    },
    {
      "t": "2026-11-15T22:34:45+01:00",
      "k": "ticket-reset",
      "id": "F3",
      "reason": "ticket-edited"
    },
    {
      "t": "2026-11-15T22:34:45+01:00",
      "k": "tickets",
      "n": 4
    },
    {
      "t": "2026-11-15T22:53:46+01:00",
      "k": "tickets",
      "n": 4
    },
    {
      "t": "2026-11-15T23:02:35+01:00",
      "k": "ticket",
      "ids": [
        "F3"
      ],
      "act": "review"
    },
    {
      "t": "2026-11-15T23:02:36+01:00",
      "k": "ticket",
      "ids": [
        "F3"
      ],
      "act": "done",
      "tests": {
        "passed": 922,
        "failed": 0
      }
    },
    {
      "t": "2026-11-15T23:02:37+01:00",
      "k": "tests",
      "passed": 922,
      "failed": 0
    },
    {
      "t": "2026-11-15T23:02:52+01:00",
      "k": "add",
      "key": "report",
      "n": 1
    },
    {
      "t": "2026-11-15T23:02:53+01:00",
      "k": "add",
      "key": "report",
      "n": 1
    },
    {
      "t": "2026-11-15T23:02:54+01:00",
      "k": "add",
      "key": "report",
      "n": 1
    },
    {
      "t": "2026-11-15T23:02:55+01:00",
      "k": "add",
      "key": "report",
      "n": 1
    },
    {
      "t": "2026-11-15T23:02:55+01:00",
      "k": "add",
      "key": "report",
      "n": 1
    },
    {
      "t": "2026-11-15T23:02:56+01:00",
      "k": "add",
      "key": "report",
      "n": 1
    },
    {
      "t": "2026-11-15T23:02:57+01:00",
      "k": "add",
      "key": "report",
      "n": 1
    },
    {
      "t": "2026-11-15T23:02:58+01:00",
      "k": "add",
      "key": "report",
      "n": 1
    },
    {
      "t": "2026-11-15T23:03:25+01:00",
      "k": "gate",
      "g": "G2",
      "ok": true,
      "found": 4,
      "fixed": 2,
      "deferred": 2
    },
    {
      "t": "2026-11-15T23:03:26+01:00",
      "k": "finish",
      "result": "Доделки после аудита: страница без токена не несёт данных, адрес с токеном печатает только ap.py url, ключ подписи создаётся атомарно, «Сейчас» и «Требования» компактны, маршрут таска задаёт оценка планировщика вместо регулярных выражений; 922 теста зелёные, слепая приёмка 5 из 6 (гонка со старым пустым ключом осталась)",
      "problems": 1
    }
  ],
  "reqList": [
    {
      "id": "R01",
      "text": "«По второму пункту – да, надо доделать» — dashboard.html отдаётся без токена и несёт снимок состояния",
      "status": "done"
    },
    {
      "id": "R02",
      "text": "«По второму пункту – да, надо доделать» — адрес с ?t= печатается при каждой команде ap.py",
      "status": "done"
    },
    {
      "id": "R03",
      "text": "«По второму пункту – да, надо доделать» — ключ gate.key создаётся не атомарно",
      "status": "done"
    },
    {
      "id": "R04",
      "text": "«По второму пункту – да, надо доделать» — противоречие в спеке: R24 «снимает только пользователь» и finish --by-user снимает открытые строки цитатой",
      "status": "done"
    },
    {
      "id": "R05",
      "text": "«Под первым пунктом я бы хотел что-то более компактное, но в принципе так тоже пойдет»",
      "status": "done"
    },
    {
      "id": "R06",
      "text": "«Третий пункт пока игнорирую»",
      "status": "deferred",
      "why": "пользователь сам отложил: ключ context7, сессия cosmic-willow, два неотслеживаемых файла"
    },
    {
      "id": "R07",
      "text": "«Надо бы выбирать модели более интеллигентно, а не по regular expression, есть там слово какое-то или нет. Это слишком ненадежно и грубо.»",
      "status": "done"
    }
  ],
  "gates": {
    "G1": {
      "ok": true,
      "at": "2026-11-15T20:47:00+01:00",
      "open": 0,
      "total": 7
    },
    "G2": {
      "ok": true,
      "at": "2026-11-15T23:03:25+01:00",
      "found": 4,
      "fixed": 2,
      "deferred": 2
    },
    "G3": {
      "ok": true,
      "at": "2026-11-15T20:52:22+01:00",
      "problems": 0
    },
    "G4": {
      "ok": false,
      "at": "2026-11-15T22:27:32+01:00",
      "checked": 6,
      "matched": 5
    }
  },
  "result": "Доделки после аудита: страница без токена не несёт данных, адрес с токеном печатает только ap.py url, ключ подписи создаётся атомарно, «Сейчас» и «Требования» компактны, маршрут таска задаёт оценка планировщика вместо регулярных выражений; 922 теста зелёные, слепая приёмка 5 из 6 (гонка со старым пустым ключом осталась)",
  "skillVersion": "2.7.0",
  "spend": {
    "byRole": {},
    "byModel": {},
    "byTicket": {}
  },
  "history": [
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
  "planContractDigest": "7168ba9393bb8e0b1458e235e3705d99f8a795780b20d113a1d4e4086e754d8b",
  "planValidationDigest": "01b19cefcb29b7eeeb6401674458ea147c3b214e811dc2be361c1ec08a5e824d",
  "blindRounds": 2,
  "report": [
    "gate_sign: при старом пустом gate.key одновременный запуск из 8 процессов по 4 потока в 6 из 28 прогонов даёт два ключа или читателя без ключа; свежий и полный ключ в порядке (R03, слепая приёмка, второй круг)",
    "refresh_dashboard: exec_module не ловит SyntaxError в чужом dashboard_upgrade.py; копия в tmp называется slug-метка-хеш — два обновления одного текста в одну секунду сталкиваются",
    "Страница с неверным ?t= показывает общую ошибку и опрашивает state.js с 403 бесконечно, а не подсказку про ap.py url; подсказка только когда t нет вовсе",
    "Заголовок героя «Сейчас»: сущности вроде &amp; в title экранируются дважды",
    "Сохранённые маршруты: старый таск без заголовков, посчитанный по словам, теперь считается по зоне; после upgrade-tools на живом полёте повторить plan-models (в retry-policy и model-routing предупреждения нет)",
    "check-plan не требует класс у F<n>: phases/6-review.md не пишет заголовки; uncertainty в оценке теперь постоянна; приём «temp + link» продублирован в serve_token и _create_key_atomically",
    "Слово env как сегмент зоны считается чувствительным (.env.example, env.py) — сознательно; файлы вида tests/test_model_router.py чувствительными не считаются",
    "Режим без строгой маршрутизации: модель закреплена параметром вызова Agent, а не профилем; усилие (effort) не проверяется и не задаётся"
  ],
  "landedWith": {
    "problems": [
      "слепая приёмка: расхождения остались после 2 кругов (1 из 6)"
    ],
    "byUser": null
  }
}
