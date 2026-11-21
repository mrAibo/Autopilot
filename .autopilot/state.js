window.STATE =
{
  "schemaVersion": 1,
  "version": 2,
  "slug": "quality-and-spend",
  "dir": "2026-11-21-quality-and-spend",
  "title": "Качество и расход: land, приёмка, doc-check",
  "mode": "semi",
  "depth": "normal",
  "kind": "task",
  "tier": null,
  "strictRouting": false,
  "gateSigned": false,
  "sequentialHost": false,
  "spendLedger": [
    {
      "t": "2026-11-21T12:00:04+01:00",
      "run": "2026-11-21-quality-and-spend",
      "source": "orchestrator",
      "origin": "claude-transcript",
      "role": "orchestrator",
      "ticket": null,
      "agent": null,
      "agent_type": null,
      "model": "claude-sonnet-5-5",
      "effort": null,
      "turns": 17,
      "input": 38,
      "output": 9130,
      "cache_read": 2353420,
      "cache_write": 266764,
      "tokens": 9168,
      "hit": 90
    },
    {
      "t": "2026-11-21T12:00:04+01:00",
      "run": "2026-11-21-quality-and-spend",
      "source": "subagent",
      "origin": "claude-subagents",
      "role": "acceptance",
      "ticket": null,
      "agent": "ad18be2286a195166",
      "agent_type": "autopilot-acceptance",
      "model": "claude-sonnet-5-5",
      "effort": null,
      "turns": 24,
      "input": 48,
      "output": 10430,
      "cache_read": 893430,
      "cache_write": 51878,
      "tokens": 10478,
      "hit": 95
    }
  ],
  "isolateTickets": false,
  "briefFile": "2026-11-21-brief.md",
  "memoryFile": "AGENTS.md",
  "memoryOwner": "autopilot",
  "skillDir": "C:/Users/crown/Downloads/Projects/Autopilot/skills/autopilot",
  "baseCommit": "85a5a44",
  "startedAt": "2026-11-21T02:22:26+01:00",
  "updatedAt": "2026-11-21T12:00:03+01:00",
  "finishedAt": "2026-11-21T12:00:04+01:00",
  "stages": [
    {
      "id": "preflight",
      "status": "done",
      "startedAt": "2026-11-21T02:22:26+01:00",
      "segments": [
        {
          "startedAt": "2026-11-21T02:22:26+01:00",
          "finishedAt": "2026-11-21T02:22:41+01:00"
        }
      ],
      "finishedAt": "2026-11-21T02:22:41+01:00"
    },
    {
      "id": "manifest",
      "status": "done",
      "segments": [
        {
          "startedAt": "2026-11-21T02:22:41+01:00",
          "finishedAt": "2026-11-21T02:22:46+01:00"
        }
      ],
      "startedAt": "2026-11-21T02:22:41+01:00",
      "finishedAt": "2026-11-21T02:22:46+01:00"
    },
    {
      "id": "briefing",
      "status": "skipped",
      "segments": [
        {
          "startedAt": "2026-11-21T02:22:46+01:00",
          "finishedAt": "2026-11-21T02:22:46+01:00"
        }
      ],
      "startedAt": "2026-11-21T02:22:46+01:00",
      "finishedAt": "2026-11-21T02:22:46+01:00",
      "note": "бриф исчерпывающий, развилок нет"
    },
    {
      "id": "spec",
      "status": "done",
      "segments": [
        {
          "startedAt": "2026-11-21T02:22:46+01:00",
          "finishedAt": "2026-11-21T02:28:04+01:00"
        }
      ],
      "startedAt": "2026-11-21T02:22:46+01:00",
      "finishedAt": "2026-11-21T02:28:04+01:00"
    },
    {
      "id": "plan",
      "status": "done",
      "startedAt": "2026-11-21T02:28:04+01:00",
      "finishedAt": "2026-11-21T02:28:04+01:00"
    },
    {
      "id": "build",
      "status": "done",
      "segments": [
        {
          "startedAt": "2026-11-21T02:28:04+01:00",
          "finishedAt": "2026-11-21T03:03:18+01:00"
        }
      ],
      "startedAt": "2026-11-21T02:28:04+01:00",
      "finishedAt": "2026-11-21T03:03:18+01:00"
    },
    {
      "id": "review",
      "status": "done",
      "segments": [
        {
          "startedAt": "2026-11-21T03:03:18+01:00",
          "finishedAt": "2026-11-21T03:05:54+01:00"
        }
      ],
      "startedAt": "2026-11-21T03:03:18+01:00",
      "finishedAt": "2026-11-21T03:05:54+01:00"
    },
    {
      "id": "final",
      "status": "done",
      "segments": [
        {
          "startedAt": "2026-11-21T03:05:54+01:00",
          "finishedAt": "2026-11-21T12:00:04+01:00"
        }
      ],
      "startedAt": "2026-11-21T03:05:54+01:00",
      "finishedAt": "2026-11-21T12:00:04+01:00"
    }
  ],
  "requirements": {
    "total": 12,
    "done": 12,
    "inTicket": 0,
    "inSpec": 0,
    "placeholder": 0,
    "deferred": 0,
    "dropped": 0
  },
  "tickets": [
    {
      "id": "01",
      "title": "Красный land: имена упавших тестов",
      "requirements": [
        "R01",
        "R02"
      ],
      "blockedBy": [],
      "wave": 1,
      "zone": [
        "skills/autopilot/tools/ap.py",
        "tests/test_land_failures.py"
      ],
      "review": "нет",
      "model": "обычная",
      "repro": false,
      "testsEdit": null,
      "fingerprint": "82a56dc8ec78d35dbbdc3a03088a3cab42b7966e79dd81856c15ad59cc7fff40",
      "status": "done",
      "startedAt": "2026-11-21T02:28:16+01:00",
      "finishedAt": "2026-11-21T02:41:14+01:00",
      "retries": 0,
      "repairs": 0,
      "tests": {
        "passed": 1372,
        "failed": 0
      },
      "commit": "3c5cffc",
      "placeholders": [],
      "plannedRouting": {
        "ticket": "01",
        "provider": "anthropic",
        "model": "sonnet",
        "effort": "medium",
        "effortEnforced": null,
        "profile": "balanced",
        "score": 31,
        "factors": {
          "algorithm": 10,
          "coupling": 5,
          "uncertainty": 11,
          "context": 0,
          "testing": 5,
          "risk": 0
        },
        "reason": "score=31; profile=balanced; high-risk=False; class=обычный; risk=обычный; why=локальная правка cmd_land и новая функция по образцу last_line, тест по образцу tests/test_one_command.py\r",
        "requiresReview": false,
        "status": "blocked",
        "fingerprint": "82a56dc8ec78d35dbbdc3a03088a3cab42b7966e79dd81856c15ad59cc7fff40",
        "hostExecutionVerified": false,
        "error": "No verified host capabilities",
        "applied": false
      },
      "startHead": "85a5a440f0f598f7acb8e59576beffbdbe7b1c8b"
    },
    {
      "id": "02",
      "title": "Целевая проверка на land, полная перед ревью и в finish",
      "requirements": [
        "R05",
        "R06",
        "R07"
      ],
      "blockedBy": [
        "01"
      ],
      "wave": 2,
      "zone": [
        "skills/autopilot/tools/ap.py",
        "tests/test_land_targeted.py"
      ],
      "review": "нет",
      "model": "обычная",
      "repro": false,
      "testsEdit": null,
      "fingerprint": "aafbe68970d006a0792cbcbad2ae96a0b2e62cc61164555c8a0f3caaa315f989",
      "status": "done",
      "startedAt": "2026-11-21T02:43:08+01:00",
      "finishedAt": "2026-11-21T02:52:55+01:00",
      "retries": 0,
      "repairs": 0,
      "tests": {
        "passed": 1389,
        "failed": 0
      },
      "commit": "0bfaef4",
      "placeholders": [],
      "plannedRouting": {
        "ticket": "02",
        "provider": "anthropic",
        "model": "sonnet",
        "effort": "xhigh",
        "effortEnforced": null,
        "profile": "critical",
        "score": 45,
        "factors": {
          "algorithm": 20,
          "coupling": 5,
          "uncertainty": 0,
          "context": 0,
          "testing": 10,
          "risk": 10
        },
        "reason": "score=45; profile=critical; high-risk=True; class=сложный; risk=высокий; why=меняет путь «красный не садится» и два перехода (stage review, finish), ошибка ослабит защиту\r",
        "requiresReview": true,
        "status": "blocked",
        "fingerprint": "aafbe68970d006a0792cbcbad2ae96a0b2e62cc61164555c8a0f3caaa315f989",
        "hostExecutionVerified": false,
        "error": "No verified host capabilities",
        "applied": false
      },
      "startHead": "91cf5239ad54416cf9df57323249fe905d7c884c"
    },
    {
      "id": "03",
      "title": "Фазы: узкая разведка, приёмка без шума из-за отложенного",
      "requirements": [
        "R04",
        "R08"
      ],
      "blockedBy": [],
      "wave": 1,
      "zone": [
        "skills/autopilot/phases/",
        "skills/autopilot/prompts/",
        "tests/test_phase_texts_quality_spend.py"
      ],
      "review": "нет",
      "model": "обычная",
      "repro": false,
      "testsEdit": null,
      "fingerprint": "de930c883ec0bdfa6ac2a6a859af347f453fede040cc965cb60b0badbbf34786",
      "status": "done",
      "startedAt": "2026-11-21T02:28:16+01:00",
      "finishedAt": "2026-11-21T02:43:02+01:00",
      "retries": 0,
      "repairs": 0,
      "tests": {
        "passed": 1372,
        "failed": 0
      },
      "commit": "91cf523",
      "placeholders": [],
      "plannedRouting": {
        "ticket": "03",
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
        "reason": "score=41; profile=balanced; high-risk=False; class=обычный; risk=обычный; why=правка текстов фаз и выжимок с проверкой дословности, тест на наличие фраз\r",
        "requiresReview": false,
        "status": "blocked",
        "fingerprint": "de930c883ec0bdfa6ac2a6a859af347f453fede040cc965cb60b0badbbf34786",
        "hostExecutionVerified": false,
        "error": "No verified host capabilities",
        "applied": false
      },
      "startHead": "85a5a440f0f598f7acb8e59576beffbdbe7b1c8b"
    },
    {
      "id": "04",
      "title": "ap.py doc-check",
      "requirements": [
        "R10",
        "R11"
      ],
      "blockedBy": [
        "02"
      ],
      "wave": 3,
      "zone": [
        "skills/autopilot/tools/ap.py",
        "skills/autopilot/tools/doc_check.py",
        "tests/test_doc_check.py"
      ],
      "review": "нет",
      "model": "обычная",
      "repro": false,
      "testsEdit": null,
      "fingerprint": "4f524c77b79c806bf1b1ec07a8c71bbafe222b9d51e072c2f55d60613e45cc44",
      "status": "done",
      "startedAt": "2026-11-21T02:53:01+01:00",
      "finishedAt": "2026-11-21T02:59:53+01:00",
      "retries": 0,
      "repairs": 0,
      "tests": {
        "passed": 1401,
        "failed": 0
      },
      "commit": "672d9ad",
      "placeholders": [],
      "plannedRouting": {
        "ticket": "04",
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
        "reason": "score=41; profile=balanced; high-risk=False; class=обычный; risk=обычный; why=новый небольшой модуль по образцу lessons.py, диспетчер в ap.py, предупреждение в finish\r",
        "requiresReview": false,
        "status": "blocked",
        "fingerprint": "4f524c77b79c806bf1b1ec07a8c71bbafe222b9d51e072c2f55d60613e45cc44",
        "hostExecutionVerified": false,
        "error": "No verified host capabilities",
        "applied": false
      },
      "startHead": "0bfaef48f3b40271394e42a6c9527c33352a71f6"
    },
    {
      "id": "05",
      "title": "CHANGELOG, ADR 0035, AGENTS.md",
      "requirements": [
        "R01",
        "R03",
        "R05",
        "R10",
        "R12"
      ],
      "blockedBy": [
        "01",
        "02",
        "03",
        "04",
        "06"
      ],
      "wave": 4,
      "zone": [
        "CHANGELOG.md",
        "AGENTS.md",
        "docs/adr/0035-*.md",
        "README.md",
        "README.ru.md",
        "README.de.md"
      ],
      "review": "нет",
      "model": "обычная",
      "repro": false,
      "testsEdit": null,
      "fingerprint": "a519040fb106cba747e78ee82b564296cb11113c41b4e9d2a147c5f2a42a64f8",
      "status": "done",
      "startedAt": "2026-11-21T03:00:01+01:00",
      "finishedAt": "2026-11-21T03:03:13+01:00",
      "retries": 0,
      "repairs": 0,
      "tests": {
        "passed": 1401,
        "failed": 0
      },
      "commit": "91c1cdc",
      "placeholders": [],
      "plannedRouting": {
        "ticket": "05",
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
        "reason": "score=35; profile=balanced; high-risk=False; class=механический; risk=обычный; why=только документы по образцу прежних записей",
        "requiresReview": false,
        "status": "blocked",
        "fingerprint": "a519040fb106cba747e78ee82b564296cb11113c41b4e9d2a147c5f2a42a64f8",
        "hostExecutionVerified": false,
        "error": "No verified host capabilities",
        "applied": false
      },
      "startHead": "672d9adee9ccd0269a70b61ddf6f086ce7b2d326"
    },
    {
      "id": "06",
      "title": "Браузерная проверка «план: N из M»",
      "requirements": [
        "R09"
      ],
      "blockedBy": [],
      "wave": 1,
      "zone": [
        "tools/check-dashboard-browser.py",
        "tests/test_check_dashboard_browser_plan.py"
      ],
      "review": "нет",
      "model": "обычная",
      "repro": false,
      "testsEdit": null,
      "fingerprint": "7a61a1e92d1bf58a5a66c5d055168341106fa13d10c81ecaec948263f34e7d19",
      "status": "done",
      "startedAt": "2026-11-21T02:36:06+01:00",
      "finishedAt": "2026-11-21T02:46:13+01:00",
      "retries": 0,
      "repairs": 0,
      "tests": {
        "passed": 1372,
        "failed": 0
      },
      "commit": "e1c104f",
      "placeholders": [],
      "plannedRouting": {
        "ticket": "06",
        "provider": "anthropic",
        "model": "sonnet",
        "effort": "medium",
        "effortEnforced": null,
        "profile": "balanced",
        "score": 31,
        "factors": {
          "algorithm": 10,
          "coupling": 5,
          "uncertainty": 11,
          "context": 0,
          "testing": 5,
          "risk": 0
        },
        "reason": "score=31; profile=balanced; high-risk=False; class=обычный; risk=обычный; why=расширение скрипта по образцу shoot_designs, DOM-проверка через headless Chrome, тест на чистую функцию и пропуск без Chrome\r",
        "requiresReview": false,
        "status": "blocked",
        "fingerprint": "7a61a1e92d1bf58a5a66c5d055168341106fa13d10c81ecaec948263f34e7d19",
        "hostExecutionVerified": false,
        "error": "No verified host capabilities",
        "applied": false
      },
      "startHead": "85a5a440f0f598f7acb8e59576beffbdbe7b1c8b"
    }
  ],
  "tests": {
    "passed": 1406,
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
    "found": 6,
    "fixed": 6,
    "deferred": 0,
    "items": [
      "G2: prompts, тесты T02/T04/T06, область doc-check, код 1, без браузера — дописано в спеку"
    ]
  },
  "concerns": [
    "план: T05.4 — частично — Результат поиска мигающего теста (из `notes.md` прогона, раздел «Поиск мигающего») записан в CHANGELOG одной строкой"
  ],
  "blockingFindings": [],
  "blind": {
    "checked": 5,
    "matched": 4,
    "mismatches": [
      "поиск мигающего теста: найти и чинить было нечего (в двух чистых прогонах проверяющего мигания нет); печать упавших тестов на красном land проверена вживую — расхождение закрыто"
    ],
    "rounds": [
      {
        "checked": 5,
        "matched": 4,
        "mismatches": [
          "поиск мигающего теста: три полных прогона без падений, найти и починить было нечего; печать упавших тестов на красном land проверена только тестами, вживую не гонялась"
        ]
      },
      {
        "checked": 2,
        "matched": 1,
        "mismatches": [
          "поиск мигающего теста: найти и чинить было нечего (в двух чистых прогонах проверяющего мигания нет); печать упавших тестов на красном land проверена вживую — расхождение закрыто"
        ]
      }
    ]
  },
  "beats": [
    "2026-11-21T02:22:26+01:00",
    "2026-11-21T02:22:41+01:00",
    "2026-11-21T02:22:46+01:00",
    "2026-11-21T02:25:59+01:00",
    "2026-11-21T02:26:29+01:00",
    "2026-11-21T02:26:30+01:00",
    "2026-11-21T02:26:35+01:00",
    "2026-11-21T02:26:42+01:00",
    "2026-11-21T02:27:49+01:00",
    "2026-11-21T02:28:04+01:00",
    "2026-11-21T02:28:11+01:00",
    "2026-11-21T02:28:16+01:00",
    "2026-11-21T02:36:06+01:00",
    "2026-11-21T02:38:34+01:00",
    "2026-11-21T02:41:18+01:00",
    "2026-11-21T02:43:08+01:00",
    "2026-11-21T02:44:22+01:00",
    "2026-11-21T02:51:11+01:00",
    "2026-11-21T02:53:01+01:00",
    "2026-11-21T02:58:10+01:00",
    "2026-11-21T03:00:01+01:00",
    "2026-11-21T03:01:26+01:00",
    "2026-11-21T03:03:18+01:00",
    "2026-11-21T03:05:38+01:00",
    "2026-11-21T03:05:39+01:00",
    "2026-11-21T03:05:51+01:00",
    "2026-11-21T03:05:54+01:00",
    "2026-11-21T03:14:58+01:00",
    "2026-11-21T03:15:06+01:00",
    "2026-11-21T03:15:07+01:00",
    "2026-11-21T11:59:59+01:00",
    "2026-11-21T12:00:00+01:00",
    "2026-11-21T12:00:03+01:00"
  ],
  "rev": 42,
  "waiting": null,
  "waits": [],
  "log": [
    {
      "t": "2026-11-21T02:22:26+01:00",
      "k": "init"
    },
    {
      "t": "2026-11-21T02:22:41+01:00",
      "k": "stage",
      "id": "manifest",
      "act": "start"
    },
    {
      "t": "2026-11-21T02:22:46+01:00",
      "k": "stage",
      "id": "briefing",
      "act": "skip",
      "note": "бриф исчерпывающий, развилок нет"
    },
    {
      "t": "2026-11-21T02:22:46+01:00",
      "k": "gate",
      "g": "G1",
      "ok": false,
      "open": 12,
      "total": 12
    },
    {
      "t": "2026-11-21T02:22:46+01:00",
      "k": "stage",
      "id": "spec",
      "act": "start"
    },
    {
      "t": "2026-11-21T02:25:59+01:00",
      "k": "gate",
      "g": "G2",
      "ok": true,
      "found": 6,
      "fixed": 6,
      "deferred": 0
    },
    {
      "t": "2026-11-21T02:25:59+01:00",
      "k": "gate",
      "g": "G1",
      "ok": true,
      "open": 0,
      "total": 12
    },
    {
      "t": "2026-11-21T02:26:29+01:00",
      "k": "tickets",
      "n": 6
    },
    {
      "t": "2026-11-21T02:26:30+01:00",
      "k": "gate",
      "g": "G3",
      "ok": false,
      "problems": 2
    },
    {
      "t": "2026-11-21T02:26:35+01:00",
      "k": "tickets",
      "n": 6
    },
    {
      "t": "2026-11-21T02:26:35+01:00",
      "k": "gate",
      "g": "G3",
      "ok": true,
      "problems": 0
    },
    {
      "t": "2026-11-21T02:27:49+01:00",
      "k": "gate",
      "g": "G3",
      "ok": true,
      "problems": 0
    },
    {
      "t": "2026-11-21T02:28:04+01:00",
      "k": "stage",
      "id": "build",
      "act": "start"
    },
    {
      "t": "2026-11-21T02:28:11+01:00",
      "k": "plan-models",
      "provider": "anthropic",
      "applied": false,
      "tickets": 6,
      "blocked": 6
    },
    {
      "t": "2026-11-21T02:28:16+01:00",
      "k": "plan-models",
      "provider": "anthropic",
      "applied": false,
      "tickets": 6,
      "blocked": 6
    },
    {
      "t": "2026-11-21T02:28:16+01:00",
      "k": "ticket",
      "ids": [
        "01",
        "03"
      ],
      "act": "start"
    },
    {
      "t": "2026-11-21T02:36:06+01:00",
      "k": "ticket",
      "ids": [
        "06"
      ],
      "act": "start"
    },
    {
      "t": "2026-11-21T02:38:34+01:00",
      "k": "ticket",
      "ids": [
        "01"
      ],
      "act": "done",
      "tests": {
        "passed": 1372,
        "failed": 0
      }
    },
    {
      "t": "2026-11-21T02:41:18+01:00",
      "k": "ticket",
      "ids": [
        "03"
      ],
      "act": "done",
      "tests": {
        "passed": 1372,
        "failed": 0
      }
    },
    {
      "t": "2026-11-21T02:43:08+01:00",
      "k": "ticket",
      "ids": [
        "02"
      ],
      "act": "start"
    },
    {
      "t": "2026-11-21T02:44:22+01:00",
      "k": "ticket",
      "ids": [
        "06"
      ],
      "act": "done",
      "tests": {
        "passed": 1372,
        "failed": 0
      }
    },
    {
      "t": "2026-11-21T02:51:11+01:00",
      "k": "ticket",
      "ids": [
        "02"
      ],
      "act": "done",
      "tests": {
        "passed": 1389,
        "failed": 0
      }
    },
    {
      "t": "2026-11-21T02:53:01+01:00",
      "k": "ticket",
      "ids": [
        "04"
      ],
      "act": "start"
    },
    {
      "t": "2026-11-21T02:58:10+01:00",
      "k": "ticket",
      "ids": [
        "04"
      ],
      "act": "done",
      "tests": {
        "passed": 1401,
        "failed": 0
      }
    },
    {
      "t": "2026-11-21T03:00:01+01:00",
      "k": "ticket",
      "ids": [
        "05"
      ],
      "act": "start"
    },
    {
      "t": "2026-11-21T03:01:26+01:00",
      "k": "ticket",
      "ids": [
        "05"
      ],
      "act": "done",
      "tests": {
        "passed": 1401,
        "failed": 0
      }
    },
    {
      "t": "2026-11-21T03:03:18+01:00",
      "k": "stage",
      "id": "review",
      "act": "start"
    },
    {
      "t": "2026-11-21T03:05:38+01:00",
      "k": "add",
      "key": "report",
      "n": 1
    },
    {
      "t": "2026-11-21T03:05:38+01:00",
      "k": "add",
      "key": "report",
      "n": 1
    },
    {
      "t": "2026-11-21T03:05:38+01:00",
      "k": "add",
      "key": "report",
      "n": 1
    },
    {
      "t": "2026-11-21T03:05:39+01:00",
      "k": "add",
      "key": "report",
      "n": 1
    },
    {
      "t": "2026-11-21T03:05:51+01:00",
      "k": "add",
      "key": "concerns",
      "n": 1
    },
    {
      "t": "2026-11-21T03:05:51+01:00",
      "k": "plan-fact",
      "done": 26,
      "total": 27
    },
    {
      "t": "2026-11-21T03:05:54+01:00",
      "k": "stage",
      "id": "final",
      "act": "start"
    },
    {
      "t": "2026-11-21T03:14:58+01:00",
      "k": "gate",
      "g": "G4",
      "ok": false,
      "checked": 5,
      "matched": 4
    },
    {
      "t": "2026-11-21T03:15:06+01:00",
      "k": "tests",
      "passed": 1406,
      "failed": 0
    },
    {
      "t": "2026-11-21T03:15:07+01:00",
      "k": "tests",
      "passed": 1401,
      "failed": 0
    },
    {
      "t": "2026-11-21T11:59:59+01:00",
      "k": "tests",
      "passed": 1406,
      "failed": 0
    },
    {
      "t": "2026-11-21T12:00:00+01:00",
      "k": "gate",
      "g": "G4",
      "ok": false,
      "checked": 5,
      "matched": 4
    },
    {
      "t": "2026-11-21T12:00:03+01:00",
      "k": "finish",
      "result": "land называет упавшие тесты, целевая проверка на land и полная на stage review/finish, doc-check, строка «план: N из M» в браузерной проверке",
      "problems": 1
    }
  ],
  "reqList": [
    {
      "id": "R01",
      "text": "«ap.py ticket NN land: при красной проверке печатать имена упавших тестов (FAIL/ERROR строки unittest) и хвост вывода»",
      "status": "done"
    },
    {
      "id": "R02",
      "text": "«тест на это» (вывод имён упавших тестов на land)",
      "status": "done"
    },
    {
      "id": "R03",
      "text": "«Попутно найди мигающий тест: прогони полный python tools/run-tests.py несколько раз (в фоне) и, если найдёшь, чини причину»",
      "status": "done"
    },
    {
      "id": "R04",
      "text": "«разведчик получает узкие вопросы или готовый context-pack.md — поправь фазу 3 (phases/3-spec.md, выжимка phases/short/3-spec.md) и prompts, где нужно»",
      "status": "done"
    },
    {
      "id": "R05",
      "text": "«land гоняет целевые тесты таска на посадке (по зоне/файлам тестов таска, если они заданы в таске строкой «Целевая проверка: …»)»",
      "status": "done"
    },
    {
      "id": "R06",
      "text": "«полную проверку — один раз перед ревью ветки (stage review) и в finish»",
      "status": "done"
    },
    {
      "id": "R07",
      "text": "«сохрани прежнее поведение, если строки нет; не ослабляй защиту «красный не садится»»",
      "status": "done"
    },
    {
      "id": "R08",
      "text": "«слепая приёмка: расхождения, где манифест deferred/placeholder или строка спеки «Вне рамок», не считаются 🔴 и не требуют второго круга — правка в phases/8-final.md (и выжимке), ap.py blind не менять в части слепоты и подписей»",
      "status": "done"
    },
    {
      "id": "R09",
      "text": "«tools/check-dashboard-browser.py проверяет строку «план: N из M» (планFact) во всех дизайнах/ширинах, где есть браузер»",
      "status": "done"
    },
    {
      "id": "R10",
      "text": "«команда ap.py doc-check (печатает расхождения, код 1, если нашла; не блокирует finish, только строка-предупреждение), с тестами»",
      "status": "done"
    },
    {
      "id": "R11",
      "text": "«Минимальная версия: имена команд/флагов ap.py, которые CHANGELOG/ADR прогона упоминают в backticks как ap.py <cmd> или --flag, должны существовать в ap.py»",
      "status": "done"
    },
    {
      "id": "R12",
      "text": "«НЕ делать: разрез ap.py на модули; шлюзы, подписи, guard, Opus/Fable, слепоту приёмки»",
      "status": "done"
    }
  ],
  "gates": {
    "G1": {
      "ok": true,
      "at": "2026-11-21T02:25:59+01:00",
      "open": 0,
      "total": 12
    },
    "G2": {
      "ok": true,
      "at": "2026-11-21T02:25:59+01:00",
      "found": 6,
      "fixed": 6,
      "deferred": 0
    },
    "G3": {
      "ok": true,
      "at": "2026-11-21T02:27:49+01:00",
      "problems": 0
    },
    "G4": {
      "ok": false,
      "at": "2026-11-21T12:00:00+01:00",
      "checked": 5,
      "matched": 4
    }
  },
  "result": "land называет упавшие тесты, целевая проверка на land и полная на stage review/finish, doc-check, строка «план: N из M» в браузерной проверке",
  "skillVersion": "2.7.0",
  "spend": {
    "byRole": {
      "acceptance": {
        "n": 1,
        "input": 48,
        "output": 10430,
        "cache_read": 893430,
        "cache_write": 51878,
        "tokens": 10478,
        "hit": 95
      },
      "orchestrator": {
        "n": 1,
        "input": 38,
        "output": 9130,
        "cache_read": 2353420,
        "cache_write": 266764,
        "tokens": 9168,
        "hit": 90
      }
    },
    "byModel": {
      "claude-sonnet-5-5": {
        "n": 2,
        "input": 86,
        "output": 19560,
        "cache_read": 3246850,
        "cache_write": 318642,
        "tokens": 19646,
        "hit": 91
      }
    },
    "byTicket": {}
  },
  "history": [
    {
      "dir": "2026-11-21-tails-and-r28",
      "title": "Хвосты и R28: решения и пресеты",
      "startedAt": "2026-11-21T00:35:02+01:00",
      "finishedAt": "2026-11-21T01:42:08+01:00",
      "minutes": 67,
      "tickets": 8,
      "repairs": 0,
      "result": "Хвосты закрыты и R28 решён ADR 0030-0033 (shots.py за флагом); 17 из 21 требований сделаны, 4 отложены",
      "tokens": 233649
    },
    {
      "dir": "2026-11-20-bugs-and-buttons",
      "title": "Баги ревью и кнопки подтверждения (R33–R35)",
      "startedAt": "2026-11-20T18:55:34+01:00",
      "finishedAt": "2026-11-20T19:53:57+01:00",
      "minutes": 58,
      "tickets": 4,
      "repairs": 0,
      "result": "кнопки подтверждения на дашборде (POST /.ap-act, ap.py await, вид accept, шесть дизайнов) и три слабых места ревью закрыты",
      "tokens": 266996
    },
    {
      "dir": "2026-11-20-close-weak-spots",
      "title": "Слабые места: schedule/review, commit_paths каталог, busy-claim gate_sign",
      "startedAt": "2026-11-20T17:50:32+01:00",
      "finishedAt": "2026-11-20T18:03:05+01:00",
      "minutes": 13,
      "tickets": 1,
      "repairs": 0,
      "result": "schedule пускает таск с зависимостью в review; commit_paths берёт старый путь переименования и при каталоге зоны; ensure_key не падает над целым ключом при занятой заявке",
      "tokens": 70641
    },
    {
      "dir": "2026-11-20-close-review-race-bugs",
      "title": "Баги: review/start, commit_paths, гонка test_gate_sign",
      "startedAt": "2026-11-20T10:26:17+01:00",
      "finishedAt": "2026-11-20T10:55:52+01:00",
      "minutes": 30,
      "tickets": 2,
      "repairs": 0,
      "result": "Закрыты три бага: start зависимого при review, commit_paths с переименованием, гонка gate_sign",
      "tokens": 125197
    },
    {
      "dir": "2026-11-20-close-known-bugs",
      "title": "Закрыть известные баги: plan-fact, land_check, blocker confirm, redproof",
      "startedAt": "2026-11-20T08:59:40+01:00",
      "finishedAt": "2026-11-20T09:11:51+01:00",
      "minutes": 12,
      "tickets": 1,
      "repairs": 0,
      "result": "Закрыты известные баги plan-fact, land_check, blocker confirm, redproof; R28 и R33–R35 не тронуты",
      "tokens": 54268
    },
    {
      "dir": "2026-11-20-close-progress-bugs",
      "title": "Закрыть баги из PROGRESS.md: plan-fact, land_check, blocker confirm, вердикты второго прохода, CI на run-tests",
      "startedAt": "2026-11-20T03:15:58+01:00",
      "finishedAt": "2026-11-20T03:42:56+01:00",
      "minutes": 27,
      "tickets": 2,
      "repairs": 0,
      "result": "Закрыты баги plan-fact record, land_check, blocker confirm/redproof; вердикт второго прохода хранится в блокере; CI на tools/run-tests.py",
      "tokens": 84882
    },
    {
      "dir": "2026-11-19-purpleflow-ideas-waves1-4",
      "title": "Идеи из purpleflow: приёмка, ревью, влитие, скорость, уроки (волны 1–4, R22–R27)",
      "startedAt": "2026-11-19T21:04:43+01:00",
      "finishedAt": "2026-11-19T23:45:39+01:00",
      "minutes": 160,
      "tickets": 7,
      "repairs": 0,
      "result": "Волны 1–4: план→факт, чек-лист и второй проход ревью, виды работы, проверка перед влитием, сторож молчания, уроки и профиль",
      "tokens": 336248
    },
    {
      "dir": "2026-11-19-dashboard-designs-wave1",
      "title": "Дашборд: шесть дизайнов на одной странице (волна 1, R29–R32)",
      "startedAt": "2026-11-19T16:39:57+01:00",
      "finishedAt": "2026-11-19T19:04:55+01:00",
      "minutes": 88,
      "tickets": 7,
      "repairs": 1,
      "result": "Дашборд: шесть дизайнов (Аврора, Отчёт, Пульт, Терминал, Чертёж, Бенто) на одной странице-«Ленте», выбор в шапке, живые данные; кнопки R33–R35 отложены",
      "tokens": 471577
    },
    {
      "dir": "2026-11-17-orchestrator-spend-waves-4-6",
      "title": "Autopilot: волны 4–6 (R11–R21)",
      "startedAt": "2026-11-17T03:03:11+01:00",
      "finishedAt": "2026-11-17T17:42:42+01:00",
      "minutes": 880,
      "tickets": 10,
      "repairs": 0,
      "result": "Волны 4–6 брифа: свод класс×модель×усилие, шкала роутера, -latest, сервер без PowerShell, кэш истории, аттестации и профили на finish, параллельные тесты, ошибки дашборда, быстрый старт README",
      "tokens": 358201
    },
    {
      "dir": "2026-11-16-cheaper-faster",
      "title": "Autopilot: дешевле, быстрее, удобнее",
      "startedAt": "2026-11-16T17:13:04+01:00",
      "finishedAt": "2026-11-16T19:33:40+01:00",
      "minutes": 139,
      "tickets": 4,
      "repairs": 0,
      "result": "Волны 1–3: лёгкие профили, подсказка о контексте, chore, ticket land, bootstrap, doctor, второй круг приёмки по расхождениям, текст обычного пути короче; 1027 тестов зелёные",
      "tokens": 396276
    },
    {
      "dir": "2026-11-16-subagent-spend-nonstrict",
      "title": "Расход субагентов виден в обычном режиме",
      "startedAt": "2026-11-16T02:27:36+01:00",
      "finishedAt": "2026-11-16T03:05:46+01:00",
      "minutes": 37,
      "tickets": 1,
      "repairs": 0,
      "result": "Расход субагентов виден в обычном режиме: ap.py spend-subagents и finish пишут его из журналов Claude Code, report-run и дашборд показывают; 959 тестов зелёные, слепая приёмка 10 из 11, круг 2 закрыл последний пункт",
      "tokens": 73515
    },
    {
      "dir": "2026-11-16-spend-optimization",
      "title": "Оптимизация расхода: учёт и короткий вывод проверок",
      "startedAt": "2026-11-16T00:32:00+01:00",
      "finishedAt": "2026-11-16T01:16:41+01:00",
      "minutes": 44,
      "tickets": 3,
      "repairs": 0,
      "result": "Оптимизация расхода: spend видит кэш и главную сессию (оркестратора), report-run и дашборд показывают их, исполнитель запускает проверки с коротким выводом; 942 теста зелёные, слепая приёмка 5 из 7 (замер общего кэша исполнителей не получен)",
      "tokens": 45662
    },
    {
      "dir": "2026-11-15-dashboard-token-fixes",
      "title": "Доделки после аудита: токен дашборда, ключ подписи, спека",
      "startedAt": "2026-11-15T20:36:48+01:00",
      "finishedAt": "2026-11-15T23:03:26+01:00",
      "minutes": 143,
      "tickets": 4,
      "repairs": 0,
      "result": "Доделки после аудита: страница без токена не несёт данных, адрес с токеном печатает только ap.py url, ключ подписи создаётся атомарно, «Сейчас» и «Требования» компактны, маршрут таска задаёт оценка планировщика вместо регулярных выражений; 922 теста зелёные, слепая приёмка 5 из 6 (гонка со старым пустым ключом осталась)",
      "tokens": 0
    },
    {
      "dir": "2026-11-15-audit-dashboard-haiku",
      "title": "Правки аудита 2026-11-15: дашборд, маршрутизация, Haiku",
      "startedAt": "2026-11-15T03:30:28+01:00",
      "finishedAt": "2026-11-15T17:23:21+01:00",
      "minutes": 325,
      "tickets": 7,
      "repairs": 1,
      "result": "Правки аудита: страница «Сейчас», доски, расход и история, сервер дашборда с токеном, класс таска и Haiku-профили с эскалацией на Sonnet, DPAPI-ключ и узкая граница Bash; 865 тестов зелёные, слепая приёмка 29 из 29",
      "tokens": 1163950
    },
    {
      "dir": "2026-11-08-opus-auto",
      "title": "Opus и гейты без вмешательства пользователя",
      "startedAt": "2026-11-08T16:28:02+01:00",
      "finishedAt": "2026-11-08T19:13:16+01:00",
      "minutes": 164,
      "tickets": 4,
      "repairs": 0,
      "result": "Opus-ремонт и ревью ветки, подписи Opus привязаны к прогону, автообновление инструментов, fix-таски не сбрасывают гейты",
      "tokens": 148373
    },
    {
      "dir": "2026-11-08-upstream-port-opus",
      "title": "Порт апстрима 2.2.2/2.2.3 и точечный Opus",
      "startedAt": "2026-11-08T14:16:44+01:00",
      "finishedAt": "2026-11-08T16:25:17+01:00",
      "minutes": 121,
      "tickets": 6,
      "repairs": 1,
      "result": "Порт апстрима 2.2.2/2.2.3 и точечный Opus по подписанному подтверждению",
      "tokens": 385893
    },
    {
      "dir": "2026-11-06-r22d-run-log-hardening",
      "title": "Журнал надёжнее (R22d)",
      "startedAt": "2026-11-06T01:32:19+01:00",
      "finishedAt": "2026-11-06T02:18:42+01:00",
      "minutes": 46,
      "tickets": 2,
      "repairs": 0,
      "result": "Журнал прогона надёжнее: предупреждение без run_log.py, тест списка копирования, свод переживает испорченные строки, роль субагента в журнале",
      "tokens": 46237
    },
    {
      "dir": "2026-11-06-claude-code-wave2-run-log",
      "title": "Волна 2: журнал прогона и дыры хука (R22, R22a–R22c)",
      "startedAt": "2026-11-06T00:27:56+01:00",
      "finishedAt": "2026-11-06T01:27:14+01:00",
      "minutes": 57,
      "tickets": 3,
      "repairs": 0,
      "result": "Журнал прогона и report-run, закрыты дыры хука git, accept-edit проверяет worktree",
      "tokens": 0
    },
    {
      "dir": "2026-11-05-claude-code-wave1",
      "title": "Правки по итогам сборки и Claude Code: волна 1 (R01–R06)",
      "startedAt": "2026-11-05T18:34:27+01:00",
      "finishedAt": "2026-11-05T21:34:44+01:00",
      "minutes": 76,
      "tickets": 2,
      "repairs": 2,
      "result": "Волна 1: отпечатки тасков, accept-edit, запрет git stash у исполнителей, проверка путей и версии Claude Code",
      "tokens": 0
    },
    {
      "dir": "2026-11-03-dashboard-themes",
      "title": "Выбор темы дашборда: несколько информативных видов",
      "startedAt": "2026-11-03T20:17:53+01:00",
      "finishedAt": "2026-11-05T18:09:46+01:00",
      "minutes": 2699,
      "tickets": 11,
      "repairs": 2,
      "result": "В дашборде восемь видов на выбор, «Обзор» и «Компактный» подогнаны под макеты, лого, заметки по таскам, подписи на полосах Ганта; обновление дашборда читает state.js с BOM",
      "tokens": 0
    }
  ],
  "logFailures": 0,
  "planContractDigest": "87aa3116ceb68d9a170d28d403e17705260715ca35409669f4cb92b2091e67b1",
  "planValidationDigest": "6906ab261a1e978ed8b93e1a97dcd57ae1e2ae4ac1997140bef91408dad55833",
  "report": [
    "Приёмка: правило «Вне рамок — известное, не 🔴» следует вашему брифу дословно; ревьюер заметил риск, что планировщик спрячет там требование — оставлено как есть, снять требование по-прежнему может только пользователь",
    "Целевая проверка берётся из файла таска при land без сверки отпечатка: исполнитель мог бы подменить её; полная проверка на stage review и finish это поймает позже",
    "finish с красной полной проверкой не снимается даже --by-user (для мигающего теста выхода нет)",
    "doc-check: пропускает строки со словом «нет», не читает блоки кода, молча ничего не проверяет, если проект лежит в подпапке репозитория; полная проверка на stage review может идти до 30 мин и теряется, если после неё что-то откажет"
  ],
  "planFact": {
    "items": [
      {
        "id": "T01.1",
        "ticket": "01",
        "text": "`failed_tests(out)` в `ap.py` возвращает `FAIL: имя (модуль.Класс)`/`ERROR: …` без повторов, в порядке вывода; пусто, если таких строк нет",
        "status": "сделано",
        "evidence": "skills/autopilot/tools/ap.py::failed_tests"
      },
      {
        "id": "T01.2",
        "ticket": "01",
        "text": "Красный `land` печатает блок «упавшие тесты (до 20)» и «хвост вывода (последние 15 строк)»; более 20 имён — строка «… и ещё N»",
        "status": "сделано",
        "evidence": "skills/autopilot/tools/ap.py::print_red_check"
      },
      {
        "id": "T01.3",
        "ticket": "01",
        "text": "Тест `tests/test_land_failures.py`: проект с проверкой, печатающей unittest-вывод с `FAIL:` и `ERROR:` → `land` код 2, оба имени и хвост в выводе, коммита нет; красная проверка без FAIL-строк → блока имён нет, хвост есть; зелёная — вывод прежний",
        "status": "сделано",
        "evidence": "tests/test_land_failures.py::LandFailures"
      },
      {
        "id": "T01.4",
        "ticket": "01",
        "text": "Весь набор тестов зелёный (`python tools/run-tests.py`)",
        "status": "сделано",
        "evidence": "tools/run-tests.py:1"
      },
      {
        "id": "T02.1",
        "ticket": "02",
        "text": "`targeted_check_command(state, id)` читает строку из файла таска через `ticket_files`; регэксп допускает префиксы `*`, `-`, `>` и `**` вокруг названия; нет строки → None",
        "status": "сделано",
        "evidence": "skills/autopilot/tools/ap.py::targeted_check_command"
      },
      {
        "id": "T02.2",
        "ticket": "02",
        "text": "`land` с целевой строкой: гоняет её, условия те же (код 0, ≥1 тест, 0 упавших), полная не гоняется, `targetedLands` содержит id; без строки — прежнее поведение (полная), `targetedLands` не растёт",
        "status": "сделано",
        "evidence": "tests/test_land_targeted.py::LandTargeted"
      },
      {
        "id": "T02.3",
        "ticket": "02",
        "text": "`stage review` при непустом `targetedLands`: красная полная → отказ (код ≠ 0, переход не записан, имена упавших в выводе); зелёная → переход, `state[\"tests\"]` обновлён, список пуст; при пустом списке полная не гоняется",
        "status": "сделано",
        "evidence": "skills/autopilot/tools/ap.py::full_check_gate"
      },
      {
        "id": "T02.4",
        "ticket": "02",
        "text": "`finish` при непустом `targetedLands` — то же (красная → отказ); нет строки «Полная проверка» — предупреждение «! …», без запуска",
        "status": "сделано",
        "evidence": "tests/test_land_targeted.py::FullGates"
      },
      {
        "id": "T02.5",
        "ticket": "02",
        "text": "Красная целевая проверка не садится: тест на отказ и на отсутствие коммита; изолированный прогон и `repro` не затронуты",
        "status": "сделано",
        "evidence": "tests/test_land_targeted.py::LandTargeted"
      },
      {
        "id": "T02.6",
        "ticket": "02",
        "text": "Тесты `tests/test_land_targeted.py` на каждый пункт; весь набор зелёный",
        "status": "сделано",
        "evidence": "tests/test_land_targeted.py::TargetedCommand"
      },
      {
        "id": "T03.1",
        "ticket": "03",
        "text": "`phases/3-spec.md` и `short/3-spec.md`: явное правило «узкие вопросы или context-pack»; нет формулировки «изучи проект целиком»",
        "status": "сделано",
        "evidence": "skills/autopilot/phases/3-spec.md:1"
      },
      {
        "id": "T03.2",
        "ticket": "03",
        "text": "`prompts/executor.md` (и `5-subagents.md` + выжимка там, где говорят про context-pack): pack читается первым, вне него — по необходимости",
        "status": "сделано",
        "evidence": "skills/autopilot/prompts/executor.md:10"
      },
      {
        "id": "T03.3",
        "ticket": "03",
        "text": "`phases/8-final.md` и `short/8-final.md`: правило про `deferred`/`placeholder`/«Вне рамок» — «известное, не 🔴, второй круг не нужен»; слепота (спека не показывается) и подписи не тронуты",
        "status": "сделано",
        "evidence": "skills/autopilot/phases/8-final.md:55"
      },
      {
        "id": "T03.4",
        "ticket": "03",
        "text": "`phases/4-plan.md`, `short/4-plan.md`, `5-subagents.md`, `short/5-subagents.md`: строка `Целевая проверка`, когда гоняется полная",
        "status": "сделано",
        "evidence": "skills/autopilot/phases/5-subagents.md:1"
      },
      {
        "id": "T03.5",
        "ticket": "03",
        "text": "Тест `tests/test_phase_texts_quality_spend.py` проверяет наличие ключевых фраз во всех правленых файлах; `tests/test_text_split.py` и тесты выжимок зелёные; весь набор зелёный",
        "status": "сделано",
        "evidence": "tests/test_phase_texts_quality_spend.py:1"
      },
      {
        "id": "T04.1",
        "ticket": "04",
        "text": "`doc_check.claimed`, `known`, `check` по `interfaces.md`; на настоящем репозитории `doc-check` даёт 0 расхождений по текущему CHANGELOG/ADR, а при находке таск не правит чужие документы, а правит правило разбора или сообщает в отчёте таска, что именно не нашлось",
        "status": "сделано",
        "evidence": "skills/autopilot/tools/doc_check.py::check"
      },
      {
        "id": "T04.2",
        "ticket": "04",
        "text": "Тест: вымышленные `ap.py nosuch` и `--nosuchflag` во временном CHANGELOG → расхождения и код 1; верные имена → 0; файл без упоминаний → 0",
        "status": "сделано",
        "evidence": "tests/test_doc_check.py::OnDisk"
      },
      {
        "id": "T04.3",
        "ticket": "04",
        "text": "`finish` при расхождении добавляет в вывод строку «! doc-check: N расхождений», код `finish` не меняется; сбой модуля не роняет `finish`",
        "status": "сделано",
        "evidence": "tests/test_doc_check.py::FinishWarning"
      },
      {
        "id": "T04.4",
        "ticket": "04",
        "text": "Харнессы тестов, копирующие `ap.py`, копируют и `doc_check.py`; `upgrade-tools` его подхватывает (проверено тестом); весь набор зелёный",
        "status": "сделано",
        "evidence": "tests/test_doc_check.py::Cli"
      },
      {
        "id": "T05.1",
        "ticket": "05",
        "text": "CHANGELOG «Unreleased» описывает: имена упавших тестов на `land`, `Целевая проверка`, полную проверку на `stage review`/`finish`, правило приёмки, `ap.py doc-check`, проверку «план: N из M» в браузере; упомянутые команды и флаги существуют (`python .autopilot/ap.py doc-check` — 0)",
        "status": "сделано",
        "evidence": "CHANGELOG.md:1"
      },
      {
        "id": "T05.2",
        "ticket": "05",
        "text": "ADR `0035` (формат соседних): контекст, решение, что не ловится (doc-check — только имена в backticks)",
        "status": "сделано",
        "evidence": "docs/adr/0035-targeted-land-and-doc-check.md:1"
      },
      {
        "id": "T05.3",
        "ticket": "05",
        "text": "`AGENTS.md`: строки про `Целевая проверка`/`targetedLands` и про `doc-check`; число тестов не трогать (генератор `tests-count`)",
        "status": "сделано",
        "evidence": "AGENTS.md:1"
      },
      {
        "id": "T05.4",
        "ticket": "05",
        "text": "Результат поиска мигающего теста (из `notes.md` прогона, раздел «Поиск мигающего») записан в CHANGELOG одной строкой",
        "status": "частично",
        "evidence": "мигающий тест не найден, в CHANGELOG записано честно"
      },
      {
        "id": "T06.1",
        "ticket": "06",
        "text": "Фикстура получает `planFact {done, total}`; сверка извлечённой из DOM строки с регэкспом `план: \\d+ из \\d+` на каждом дизайне и ширине",
        "status": "сделано",
        "evidence": "tools/check-dashboard-browser.py::check_plan_line"
      },
      {
        "id": "T06.2",
        "ticket": "06",
        "text": "Тест на чистую функцию сверки (есть/нет строки, разные N и M) и на пропуск без Chrome, без запуска браузера",
        "status": "сделано",
        "evidence": "tests/test_check_dashboard_browser_plan.py:1"
      },
      {
        "id": "T06.3",
        "ticket": "06",
        "text": "Если Chrome есть: скрипт проходит на машине (`python tools/check-dashboard-browser.py`), результат записан в отчёт таска; нет — написано «не проверено»",
        "status": "сделано",
        "evidence": "tools/check-dashboard-browser.py::plan_line_ok"
      },
      {
        "id": "T06.4",
        "ticket": "06",
        "text": "Весь набор зелёный",
        "status": "сделано",
        "evidence": "tools/run-tests.py:1"
      }
    ],
    "done": 26,
    "total": 27
  },
  "blindRounds": 2,
  "landedWith": {
    "problems": [
      "слепая приёмка: расхождения остались после 2 кругов (1 из 5)"
    ],
    "byUser": null
  }
}
