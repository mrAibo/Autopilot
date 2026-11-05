window.STATE =
{
  "version": 2,
  "slug": "dashboard-themes",
  "dir": "2026-11-03-dashboard-themes",
  "title": "Выбор темы дашборда: несколько информативных видов",
  "mode": "semi",
  "depth": "normal",
  "tier": "T0",
  "strictRouting": true,
  "gateSigned": true,
  "sequentialHost": false,
  "isolateTickets": false,
  "briefFile": "2026-11-03-brief.md",
  "memoryFile": "AGENTS.md",
  "memoryOwner": "autopilot",
  "skillDir": "C:/Users/crown/Downloads/Projects/Autopilot/skills/autopilot",
  "baseCommit": "b8d29e5",
  "startedAt": "2026-11-03T20:17:53+01:00",
  "updatedAt": "2026-11-05T18:09:45+01:00",
  "finishedAt": "2026-11-05T18:09:46+01:00",
  "stages": [
    {
      "id": "preflight",
      "status": "done",
      "startedAt": "2026-11-03T20:17:53+01:00",
      "finishedAt": "2026-11-03T20:18:08+01:00"
    },
    {
      "id": "manifest",
      "status": "done",
      "startedAt": "2026-11-03T22:31:52+01:00",
      "finishedAt": "2026-11-03T22:32:14+01:00"
    },
    {
      "id": "briefing",
      "status": "skipped",
      "startedAt": "2026-11-03T22:32:13+01:00",
      "finishedAt": "2026-11-03T22:32:13+01:00",
      "note": "всё сказано в брифе; открытых вопросов нет"
    },
    {
      "id": "spec",
      "status": "done",
      "startedAt": "2026-11-03T22:32:14+01:00",
      "finishedAt": "2026-11-05T17:59:54+01:00"
    },
    {
      "id": "plan",
      "status": "done",
      "startedAt": "2026-11-03T22:34:11+01:00",
      "finishedAt": "2026-11-03T22:34:12+01:00"
    },
    {
      "id": "build",
      "status": "done",
      "startedAt": "2026-11-03T22:34:13+01:00",
      "finishedAt": "2026-11-05T18:09:46+01:00"
    },
    {
      "id": "review",
      "status": "skipped",
      "note": "не понадобился",
      "finishedAt": "2026-11-05T18:09:46+01:00"
    },
    {
      "id": "final",
      "status": "done",
      "finishedAt": "2026-11-05T18:09:46+01:00",
      "startedAt": "2026-11-05T18:09:46+01:00"
    }
  ],
  "requirements": {
    "total": 15,
    "done": 15,
    "inTicket": 0,
    "inSpec": 0,
    "placeholder": 0,
    "deferred": 0,
    "dropped": 0
  },
  "tickets": [
    {
      "id": "01",
      "title": "Темы дашборда и логотип",
      "requirements": [
        "R01",
        "R02",
        "R03",
        "R05",
        "R06",
        "R07",
        "R08",
        "R09i",
        "R10i",
        "G02"
      ],
      "blockedBy": [],
      "wave": 1,
      "zone": [
        "skills/autopilot/phases/dashboard-template.html",
        "tests/test_dashboard_views.py",
        "tests/test_brand_assets.py"
      ],
      "review": "нет",
      "model": "обычная",
      "fingerprint": "d2ca6e3e88a332b20dfaea9b12045d67cd584671834fac8f81b6fbd4ef9c9058",
      "status": "done",
      "startedAt": "2026-11-03T20:37:38+01:00",
      "finishedAt": "2026-11-03T20:54:57+01:00",
      "retries": 0,
      "repairs": 0,
      "tests": {
        "passed": 558,
        "failed": 0
      },
      "commit": "5d8d4d5",
      "placeholders": [],
      "routing": {
        "provider": "anthropic",
        "model": "sonnet",
        "effort": "high",
        "effortEnforced": true,
        "score": 55,
        "reason": "score=55; profile=strong; high-risk=True",
        "verified": true,
        "agentType": "autopilot-executor-01-dashboard-views",
        "agentFile": ".claude/agents/autopilot-executor-01-dashboard-views.md",
        "profileSha": "e5a9b603f5d3501f48eb794462df730223d3c4c1f816ac037e0909e36f7b45a1",
        "sig": "10832d2de92dc3b868fc7a4111b58c42a7d357bce90324cb3b0bcffb5cc35bd7"
      },
      "plannedRouting": {
        "ticket": "01",
        "provider": "anthropic",
        "model": "sonnet",
        "effort": "high",
        "effortEnforced": true,
        "profile": "strong",
        "score": 55,
        "factors": {
          "algorithm": 5,
          "coupling": 10,
          "uncertainty": 15,
          "context": 5,
          "testing": 10,
          "risk": 10
        },
        "reason": "score=55; profile=strong; high-risk=True",
        "requiresReview": true,
        "status": "ready",
        "fingerprint": "d2ca6e3e88a332b20dfaea9b12045d67cd584671834fac8f81b6fbd4ef9c9058",
        "hostExecutionVerified": false,
        "applied": true
      },
      "attestation": {
        "model": "claude-sonnet-5-5",
        "effort": "high",
        "lines": 60
      }
    },
    {
      "id": "02",
      "title": "Чтение state.js с BOM и документация тем",
      "requirements": [
        "G01",
        "R04"
      ],
      "blockedBy": [
        "01"
      ],
      "wave": 2,
      "zone": [
        "skills/autopilot/tools/dashboard_upgrade.py",
        "tests/test_dashboard_upgrade.py",
        "docs/autopilot/dashboard-views.md",
        "CHANGELOG.md"
      ],
      "review": "нет",
      "model": "обычная",
      "fingerprint": "d69d8562339634cf2333d07dfb816f73738d0f4d07b52a694faf47e5848b4b25",
      "status": "done",
      "startedAt": "2026-11-03T20:55:08+01:00",
      "finishedAt": "2026-11-03T21:02:04+01:00",
      "retries": 0,
      "repairs": 0,
      "tests": {
        "passed": 560,
        "failed": 0
      },
      "commit": "fb61a4d",
      "placeholders": [],
      "routing": {
        "provider": "anthropic",
        "model": "sonnet",
        "effort": "high",
        "effortEnforced": true,
        "score": 45,
        "reason": "score=45; profile=strong; high-risk=True",
        "verified": true,
        "agentType": "autopilot-executor-02-bom-fix-and-docs",
        "agentFile": ".claude/agents/autopilot-executor-02-bom-fix-and-docs.md",
        "profileSha": "aba7ad84209e66993b0e0180c85e2f63f199e16fc8e61423ffae4ac8c49656ea",
        "sig": "83b1b8a19869cb54bbad9894403e3ad05ed76589abda75bf5dbefefb845c7f41"
      },
      "plannedRouting": {
        "ticket": "02",
        "provider": "anthropic",
        "model": "sonnet",
        "effort": "high",
        "effortEnforced": true,
        "profile": "strong",
        "score": 45,
        "factors": {
          "algorithm": 5,
          "coupling": 15,
          "uncertainty": 0,
          "context": 5,
          "testing": 10,
          "risk": 10
        },
        "reason": "score=45; profile=strong; high-risk=True",
        "requiresReview": true,
        "status": "ready",
        "fingerprint": "d69d8562339634cf2333d07dfb816f73738d0f4d07b52a694faf47e5848b4b25",
        "hostExecutionVerified": false,
        "applied": true
      },
      "attestation": {
        "model": "claude-sonnet-5-5",
        "effort": "high",
        "lines": 25
      }
    },
    {
      "id": "F1",
      "title": "Ремонт ветки: навигация тем и узкая панель",
      "requirements": [
        "R01",
        "R07",
        "R10i"
      ],
      "blockedBy": [],
      "wave": 3,
      "zone": [
        "skills/autopilot/phases/dashboard-template.html",
        "tests/test_dashboard_views.py"
      ],
      "review": "да — ремонт ветки",
      "model": "сильная",
      "fingerprint": "a12348e2fb51ab911e16fa7bafa90f6df6b2b96173dec0cb24b5e7577c7bb7a0",
      "status": "done",
      "startedAt": "2026-11-03T21:06:25+01:00",
      "finishedAt": "2026-11-03T21:15:03+01:00",
      "retries": 0,
      "repairs": 0,
      "tests": {
        "passed": 561,
        "failed": 0
      },
      "commit": "bb14d32",
      "placeholders": [],
      "routing": {
        "agentType": "autopilot-executor-repair-2026-11-03-dashboard-themes",
        "agentFile": ".claude/agents/autopilot-executor-repair-2026-11-03-dashboard-themes.md",
        "model": "sonnet",
        "effort": "high",
        "effortEnforced": true,
        "profileSha": "c0bdf44942d330a146f54898e8405e93aca307e8ab51acb897cbfec365a0b193",
        "provider": "anthropic",
        "reason": "ремонт ветки: навигация тем и узкая панель",
        "verified": true,
        "sig": "d1de097f5ab44ce8b2c14a1680e1a39a9ddf6698492b5ce3da924765092beeeb"
      },
      "attestation": {
        "model": "claude-sonnet-5-5",
        "effort": "high",
        "lines": 28
      },
      "attestFrom": 669
    },
    {
      "id": "F2",
      "title": "Вид «Обзор» информативнее «Классики»",
      "requirements": [
        "R02",
        "R06"
      ],
      "blockedBy": [],
      "wave": 4,
      "zone": [
        "skills/autopilot/phases/dashboard-template.html",
        "tests/test_dashboard_views.py"
      ],
      "review": "да — ремонт ветки",
      "model": "сильная",
      "fingerprint": "f8e30b20c6b50bc33e2e01c092e3fa8c781c0a4562bd7a2e1faa118c3344a282",
      "status": "done",
      "startedAt": "2026-11-03T21:58:28+01:00",
      "finishedAt": "2026-11-03T22:07:07+01:00",
      "retries": 0,
      "repairs": 0,
      "tests": {
        "passed": 562,
        "failed": 0
      },
      "commit": "0d7c6c8",
      "placeholders": [],
      "routing": {
        "agentType": "autopilot-executor-repair-2026-11-03-dashboard-themes",
        "agentFile": ".claude/agents/autopilot-executor-repair-2026-11-03-dashboard-themes.md",
        "model": "sonnet",
        "effort": "high",
        "effortEnforced": true,
        "profileSha": "c0bdf44942d330a146f54898e8405e93aca307e8ab51acb897cbfec365a0b193",
        "provider": "anthropic",
        "reason": "ремонт слепой приёмки: Обзор информативнее Классики",
        "verified": true,
        "sig": "9b42f1282e461c1882c312891e78dd4447e33f6bb0fcb2f41f74daa6fa71e116"
      },
      "attestation": {
        "model": "claude-sonnet-5-5",
        "effort": "high",
        "lines": 24
      },
      "attestFrom": 736
    },
    {
      "id": "F3",
      "title": "«Обзор» доработан, две новые темы",
      "requirements": [
        "G03",
        "G04"
      ],
      "blockedBy": [],
      "wave": 5,
      "zone": [
        "skills/autopilot/phases/dashboard-template.html",
        "tests/test_dashboard_views.py",
        "docs/autopilot/dashboard-views.md",
        "CHANGELOG.md"
      ],
      "review": "нет",
      "model": "сильная",
      "fingerprint": "47223b9f7ebc809fcd50a155e9fc9d214011da9a5634b37e3a5716089c8bdfec",
      "status": "done",
      "startedAt": "2026-11-03T22:34:15+01:00",
      "finishedAt": "2026-11-03T22:54:03+01:00",
      "retries": 0,
      "repairs": 0,
      "tests": {
        "passed": 568,
        "failed": 0
      },
      "commit": "379fb18",
      "placeholders": [],
      "routing": {
        "agentType": "autopilot-executor-repair-2026-11-03-dashboard-themes",
        "agentFile": ".claude/agents/autopilot-executor-repair-2026-11-03-dashboard-themes.md",
        "model": "sonnet",
        "effort": "high",
        "effortEnforced": true,
        "profileSha": "c0bdf44942d330a146f54898e8405e93aca307e8ab51acb897cbfec365a0b193",
        "provider": "anthropic",
        "reason": "второй заход: доработка Обзора и две новые темы",
        "verified": true,
        "sig": "789bbe95a5e768fcf99bb99ca996f10ffa6f67d41619789367ba03fbff6ac657"
      },
      "attestation": {
        "model": "claude-sonnet-5-5",
        "effort": "high",
        "lines": 65
      },
      "attestFrom": 800
    },
    {
      "id": "F4",
      "title": "Палитра, «Обзор» и «Компактный» по макетам",
      "requirements": [
        "G05"
      ],
      "blockedBy": [],
      "wave": 6,
      "zone": [
        "skills/autopilot/phases/dashboard-template.html",
        "tests/test_dashboard_views.py"
      ],
      "review": "нет",
      "model": "сильная",
      "fingerprint": "d450a459f1bdf9345784a9f00aab7207123bdab868717299b20b1c49b28c6286",
      "status": "done",
      "startedAt": "2026-11-03T23:02:11+01:00",
      "finishedAt": "2026-11-04T07:29:17+01:00",
      "retries": 0,
      "repairs": 0,
      "tests": {
        "passed": 578,
        "failed": 0
      },
      "commit": "261b334",
      "placeholders": [],
      "routing": {
        "agentType": "autopilot-executor-repair-2026-11-03-dashboard-themes",
        "agentFile": ".claude/agents/autopilot-executor-repair-2026-11-03-dashboard-themes.md",
        "model": "sonnet",
        "effort": "high",
        "effortEnforced": true,
        "profileSha": "c0bdf44942d330a146f54898e8405e93aca307e8ab51acb897cbfec365a0b193",
        "provider": "anthropic",
        "reason": "восстановление записи таска после сброса статуса",
        "verified": true,
        "sig": "6411cbd1da77c8bb9417976674363c778ce8c118851b980a1da30d71d4709316"
      },
      "attestation": {
        "model": "claude-sonnet-5-5",
        "effort": "high",
        "lines": 233
      },
      "attestFrom": 882
    },
    {
      "id": "F5",
      "title": "«Требования», «Итог», «Таймлайн», «Ресурсы» по макетам",
      "requirements": [
        "G05"
      ],
      "blockedBy": [],
      "wave": 7,
      "zone": [
        "skills/autopilot/phases/dashboard-template.html",
        "tests/test_dashboard_views.py",
        "docs/autopilot/dashboard-views.md",
        "CHANGELOG.md"
      ],
      "review": "нет",
      "model": "сильная",
      "fingerprint": "63fda558d214666730952b462a8a295ab6b0a168e4c3c3ffba1fcaa8858c6d46",
      "status": "done",
      "startedAt": "2026-11-03T23:23:04+01:00",
      "finishedAt": "2026-11-04T07:29:20+01:00",
      "retries": 0,
      "repairs": 1,
      "tests": {
        "passed": 586,
        "failed": 0
      },
      "commit": "aff679c",
      "placeholders": [],
      "routing": {
        "agentType": "autopilot-executor-repair-2026-11-03-dashboard-themes",
        "agentFile": ".claude/agents/autopilot-executor-repair-2026-11-03-dashboard-themes.md",
        "model": "sonnet",
        "effort": "high",
        "effortEnforced": true,
        "profileSha": "c0bdf44942d330a146f54898e8405e93aca307e8ab51acb897cbfec365a0b193",
        "provider": "anthropic",
        "reason": "восстановление записи таска после сброса статуса",
        "verified": true,
        "sig": "e544b532d203337b0ed7365074f74bb708633710c069aaa04d5ffca791563df0"
      },
      "attestation": {
        "model": "claude-sonnet-5-5",
        "effort": "high",
        "lines": 169
      },
      "attestFrom": 946
    },
    {
      "id": "F6",
      "title": "Доводка после слепой приёмки",
      "requirements": [
        "G03",
        "G05"
      ],
      "blockedBy": [],
      "wave": 8,
      "zone": [
        "skills/autopilot/phases/dashboard-template.html",
        "tests/test_dashboard_views.py",
        "docs/autopilot/dashboard-views.md",
        "CHANGELOG.md"
      ],
      "review": "нет",
      "model": "сильная",
      "fingerprint": "eb8d1f378fc4dddbb55c945e7603d2a979b1da6db07ca4aa3f1e707b41fd9390",
      "status": "done",
      "startedAt": "2026-11-04T00:04:17+01:00",
      "finishedAt": "2026-11-04T07:29:22+01:00",
      "retries": 0,
      "repairs": 1,
      "tests": {
        "passed": 595,
        "failed": 0
      },
      "commit": "776c535",
      "placeholders": [],
      "routing": {
        "agentType": "autopilot-executor-repair-2026-11-03-dashboard-themes",
        "agentFile": ".claude/agents/autopilot-executor-repair-2026-11-03-dashboard-themes.md",
        "model": "sonnet",
        "effort": "high",
        "effortEnforced": true,
        "profileSha": "c0bdf44942d330a146f54898e8405e93aca307e8ab51acb897cbfec365a0b193",
        "provider": "anthropic",
        "reason": "восстановление записи таска после сброса статуса",
        "verified": true,
        "sig": "b8f27d2805c300a330474124736fa83c60c5e70264ca13705fd0e1e1022aed7e"
      },
      "attestation": {
        "model": "claude-sonnet-5-5",
        "effort": "high",
        "lines": 75
      },
      "attestFrom": 1124
    },
    {
      "id": "F7",
      "title": "Заметки по таскам в «Обзоре», «Таймлайне» и «Компактном»",
      "requirements": [
        "G03"
      ],
      "blockedBy": [],
      "wave": 9,
      "zone": [
        "skills/autopilot/phases/dashboard-template.html",
        "tests/test_dashboard_views.py",
        "docs/autopilot/dashboard-views.md",
        "CHANGELOG.md"
      ],
      "review": "нет",
      "model": "сильная",
      "fingerprint": "6aaf23333923af3e1d874816dc4f6c42765dfe32349ceef4cd2823abfe79f7fb",
      "status": "done",
      "startedAt": "2026-11-04T07:41:55+01:00",
      "finishedAt": "2026-11-04T07:54:00+01:00",
      "retries": 0,
      "repairs": 0,
      "tests": {
        "passed": 599,
        "failed": 0
      },
      "commit": "e6ad89a",
      "placeholders": [],
      "routing": {
        "agentType": "autopilot-executor-repair-2026-11-03-dashboard-themes",
        "agentFile": ".claude/agents/autopilot-executor-repair-2026-11-03-dashboard-themes.md",
        "model": "sonnet",
        "effort": "high",
        "effortEnforced": true,
        "profileSha": "c0bdf44942d330a146f54898e8405e93aca307e8ab51acb897cbfec365a0b193",
        "provider": "anthropic",
        "reason": "заметки по таскам в Обзоре, Таймлайне и Компактном",
        "verified": true,
        "sig": "db850a0a93b60b060d64282623f5cf1a4079db75f3c8dc6db16de272291c3568"
      },
      "attestation": {
        "model": "claude-sonnet-5-5",
        "effort": "high",
        "lines": 46
      },
      "attestFrom": 1271
    },
    {
      "id": "F8",
      "title": "«Обзор» как на макете: без блоков моделей и изоляции",
      "requirements": [
        "G05"
      ],
      "blockedBy": [],
      "wave": 10,
      "zone": [
        "skills/autopilot/phases/dashboard-template.html",
        "tests/test_dashboard_views.py",
        "docs/autopilot/dashboard-views.md",
        "CHANGELOG.md"
      ],
      "review": "нет",
      "model": "сильная",
      "fingerprint": "9dbaae5c4aab26394fc929298a6ab3a79c11100c9e841602fab746fe4c5a1d05",
      "status": "done",
      "startedAt": "2026-11-04T08:27:33+01:00",
      "finishedAt": "2026-11-04T08:37:40+01:00",
      "retries": 0,
      "repairs": 0,
      "tests": {
        "passed": 599,
        "failed": 0
      },
      "commit": "0215121",
      "placeholders": [],
      "routing": {
        "agentType": "autopilot-executor-repair-2026-11-03-dashboard-themes",
        "agentFile": ".claude/agents/autopilot-executor-repair-2026-11-03-dashboard-themes.md",
        "model": "sonnet",
        "effort": "high",
        "effortEnforced": true,
        "profileSha": "c0bdf44942d330a146f54898e8405e93aca307e8ab51acb897cbfec365a0b193",
        "provider": "anthropic",
        "reason": "Обзор как на макете: без блоков моделей и изоляции",
        "verified": true,
        "sig": "4421bb84d24006b40d21083ccfb5b8b0401737a2412db5e5435b0f6c97037507"
      },
      "attestation": {
        "model": "claude-sonnet-5-5",
        "effort": "high",
        "lines": 51
      },
      "attestFrom": 1374
    },
    {
      "id": "F9",
      "title": "Подписи на полосах Ганта не обрезаются",
      "requirements": [
        "G05"
      ],
      "blockedBy": [],
      "wave": 11,
      "zone": [
        "skills/autopilot/phases/dashboard-template.html",
        "tests/test_dashboard_views.py",
        "CHANGELOG.md"
      ],
      "review": "нет",
      "model": "сильная",
      "fingerprint": "6f1036123a90f61c4299282ef404a4ccd7671a010f804cfde3098a4c6b0cbf38",
      "status": "done",
      "startedAt": "2026-11-05T17:39:11+01:00",
      "finishedAt": "2026-11-05T17:59:07+01:00",
      "retries": 0,
      "repairs": 0,
      "tests": {
        "passed": 603,
        "failed": 0
      },
      "commit": "16ea3cc",
      "placeholders": [],
      "routing": {
        "agentType": "autopilot-executor-repair-2026-11-03-dashboard-themes",
        "agentFile": ".claude/agents/autopilot-executor-repair-2026-11-03-dashboard-themes.md",
        "model": "sonnet",
        "effort": "high",
        "effortEnforced": true,
        "profileSha": "c0bdf44942d330a146f54898e8405e93aca307e8ab51acb897cbfec365a0b193",
        "provider": "anthropic",
        "reason": "подписи на полосах Ганта не обрезаются",
        "verified": true,
        "sig": "02899434c47c0b2f330ff5feb835b608ca64e8a9b4131fc6c3023aa1b4784d03"
      },
      "attestation": {
        "model": "claude-sonnet-5-5",
        "effort": "high",
        "lines": 58
      },
      "attestFrom": 1531
    }
  ],
  "tests": {
    "passed": 603,
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
    "fixed": 3,
    "deferred": 1,
    "items": [
      "«Разбивка по волнам» в «Обзоре» понята как подпись волны в строке Ганта, а не отдельный список — решение сборки, в отчёт как открытый вопрос"
    ]
  },
  "concerns": [
    "dashboard-template.html:1182 — в Обзоре часть прироста текста — повторы (плитка требований и сводка, список готовых тасков дважды); тест сравнивает только длину текста",
    "dashboard-template.html — трек этапов в Обзоре показан дважды (hero и trackCard); узкая панель и светлая/тёмная тема проверены только чтением",
    "docs/autopilot/dashboard-views.md:32 — пример «Add a view» называет c.tasksCard, а его в ctx больше нет (activeCard, waitingCard, buildCard, tasksEmpty)",
    "tests/test_dashboard_views.py — проверка Обзора сверяет только заголовки h3; нет теста экранирования skillVersion; «Requirements summary» ослаблено до «Requirements»",
    "CHANGELOG: «одна сводка требований» в Обзоре — карточки сводки больше нет, её заменяет плитка; в темах кроме Обзора ссылка «Overview» ведёт не на обзор (было до F3)",
    "Столбец «приёмка» матрицы и вердикт «Итога» считают приёмку пройденной для любого требования при наличии blind (в т.ч. placeholder, deferred, dropped); ревью и тесты в матрице выводятся из статуса таска без данных tests",
    "Тест «Классика ⊂ Обзор» сверяет только h3; плитки Классики (Требования, Таски, Тесты) заменены кольцом без охраны; нет теста XSS для новых блоков; до первого render() экран загрузки подхватывает часть правил не-классики",
    "Смешанный случай (часть тасков с отметками времени, часть без) в Ганте не покрыт тестом",
    "dashboard-template.html:915 — правило ≤520px «.tools .views{order:1}» без привязки к теме: в Классике на узкой ширине переключатель видов переезжает после кнопок темы и языка",
    "Ресурсы: колонка токенов показывает «0» там, где usageEvents не записаны (нет данных ≠ ноль); в Обзоре нет заметок по таскам (замечания ревью, повторы/починки, причина упавшего) — они остались только в Классике",
    "Обзор: Гант показывает 8 строк, остальное за «ещё» — случай ≥9 тасков тестом не покрыт; шапка «обновлено N назад» считает бесконечно и в сданной сборке; полоса T01 в узком Ганте Таймлайна обрезана до «✓ 14»",
    "F7: порог отношения Компактный/Обзор в тесте поднят 0.5→0.55 (заметки добавляют вес обоим); часы в харнессе заморожены; кнопка «Показать ещё» у заметок проверена только в node-харнессе, не кликом в браузере",
    "F9: подпись полос подбирается в браузере по измерению (gxFit) — resize проверен только строковым тестом и поддельным DOM; в хвосте прогноза при нехватке места текст остаётся только в title; поднят лимит длины строки заметки 1500→1800 в тесте",
    "F9: gxFit на каждый resize без троттлинга; вынесенная подпись выбирает сторону по месту, но не проверяет её ширину; смена ширины контейнера без resize пересчитывается только при следующей отрисовке"
  ],
  "blockingFindings": [
    {
      "id": "B01",
      "text": "B1: таск без startedAt пропадает из Таймлайна, а Таймлайн и Компактный показывают ложное «тасков нет» при T.length>0",
      "ticket": "F5",
      "openedAt": "2026-11-03T23:47:14+01:00",
      "status": "resolved",
      "openedCommit": "3908897",
      "resolvedAt": "2026-11-03T23:55:30+01:00",
      "resolutionCommit": "aff679c",
      "resolutionTests": {
        "passed": 586,
        "failed": 0
      },
      "review": "независимый ревьюер перепроверил условие: таски без startedAt остаются в Таймлайне и мини-Ганте, ложная подпись только при T.length==0, новых поломок нет"
    },
    {
      "id": "B02",
      "text": "R1: правило ≤520px «.tools .views{order:1}» не должно задевать Классику (раскладка Классики при ≤520 px как до F4). R2: в Ресурсах нет данных о токенах (нет usageEvents) — показывать «—», а не «0»; «0» только для таска, у которого события есть или который ожидает и его токены заведомо нулевые",
      "ticket": "F6",
      "openedAt": "2026-11-04T07:19:50+01:00",
      "status": "resolved",
      "openedCommit": "092f081",
      "resolvedAt": "2026-11-04T07:28:11+01:00",
      "resolutionCommit": "776c535",
      "resolutionTests": {
        "passed": 595,
        "failed": 0
      },
      "review": "независимый ревьюер перепроверил оба условия: правило ≤520px не действует на Классику, токены без данных показывают «—»; новых поломок нет"
    }
  ],
  "blind": {
    "checked": 16,
    "matched": 16,
    "mismatches": []
  },
  "beats": [
    "2026-11-03T20:17:53+01:00",
    "2026-11-03T20:18:08+01:00",
    "2026-11-03T20:18:29+01:00",
    "2026-11-03T20:18:46+01:00",
    "2026-11-03T20:19:59+01:00",
    "2026-11-03T20:20:00+01:00",
    "2026-11-03T20:24:00+01:00",
    "2026-11-03T20:24:01+01:00",
    "2026-11-03T20:24:32+01:00",
    "2026-11-03T20:24:33+01:00",
    "2026-11-03T20:24:39+01:00",
    "2026-11-03T20:24:40+01:00",
    "2026-11-03T20:24:48+01:00",
    "2026-11-03T20:24:57+01:00",
    "2026-11-03T20:25:04+01:00",
    "2026-11-03T20:37:14+01:00",
    "2026-11-03T20:37:38+01:00",
    "2026-11-03T20:49:16+01:00",
    "2026-11-03T20:54:57+01:00",
    "2026-11-03T20:55:08+01:00",
    "2026-11-03T21:02:04+01:00",
    "2026-11-03T21:06:16+01:00",
    "2026-11-03T21:06:22+01:00",
    "2026-11-03T21:06:23+01:00",
    "2026-11-03T21:06:25+01:00",
    "2026-11-03T21:14:02+01:00",
    "2026-11-03T21:15:03+01:00",
    "2026-11-03T21:15:04+01:00",
    "2026-11-03T21:18:04+01:00",
    "2026-11-03T21:18:05+01:00",
    "2026-11-03T21:18:28+01:00",
    "2026-11-03T21:58:22+01:00",
    "2026-11-03T21:58:23+01:00",
    "2026-11-03T21:58:24+01:00",
    "2026-11-03T21:58:28+01:00",
    "2026-11-03T22:05:37+01:00",
    "2026-11-03T22:07:07+01:00",
    "2026-11-03T22:07:08+01:00",
    "2026-11-03T22:09:52+01:00",
    "2026-11-03T22:09:53+01:00",
    "2026-11-03T22:09:54+01:00",
    "2026-11-03T22:09:55+01:00",
    "2026-11-03T22:10:18+01:00",
    "2026-11-03T22:10:59+01:00",
    "2026-11-03T22:11:00+01:00",
    "2026-11-03T22:11:01+01:00",
    "2026-11-03T22:11:02+01:00",
    "2026-11-03T22:11:06+01:00",
    "2026-11-03T22:31:52+01:00",
    "2026-11-03T22:32:00+01:00",
    "2026-11-03T22:32:13+01:00",
    "2026-11-03T22:32:14+01:00",
    "2026-11-03T22:33:15+01:00",
    "2026-11-03T22:33:16+01:00",
    "2026-11-03T22:33:17+01:00",
    "2026-11-03T22:33:22+01:00",
    "2026-11-03T22:33:28+01:00",
    "2026-11-03T22:33:29+01:00",
    "2026-11-03T22:33:37+01:00",
    "2026-11-03T22:33:41+01:00",
    "2026-11-03T22:33:42+01:00",
    "2026-11-03T22:33:59+01:00",
    "2026-11-03T22:34:00+01:00",
    "2026-11-03T22:34:10+01:00",
    "2026-11-03T22:34:11+01:00",
    "2026-11-03T22:34:12+01:00",
    "2026-11-03T22:34:13+01:00",
    "2026-11-03T22:34:14+01:00",
    "2026-11-03T22:34:15+01:00",
    "2026-11-03T22:54:03+01:00",
    "2026-11-03T22:59:28+01:00",
    "2026-11-03T22:59:29+01:00",
    "2026-11-03T22:59:30+01:00",
    "2026-11-03T23:01:04+01:00",
    "2026-11-03T23:01:05+01:00",
    "2026-11-03T23:01:25+01:00",
    "2026-11-03T23:02:05+01:00",
    "2026-11-03T23:02:09+01:00",
    "2026-11-03T23:02:10+01:00",
    "2026-11-03T23:02:11+01:00",
    "2026-11-03T23:23:02+01:00",
    "2026-11-03T23:23:03+01:00",
    "2026-11-03T23:23:04+01:00",
    "2026-11-03T23:41:28+01:00",
    "2026-11-03T23:47:14+01:00",
    "2026-11-03T23:47:15+01:00",
    "2026-11-03T23:47:17+01:00",
    "2026-11-03T23:55:30+01:00",
    "2026-11-03T23:55:32+01:00",
    "2026-11-03T23:55:34+01:00",
    "2026-11-03T23:55:35+01:00",
    "2026-11-03T23:56:55+01:00",
    "2026-11-03T23:56:56+01:00",
    "2026-11-04T00:03:51+01:00",
    "2026-11-04T00:04:11+01:00",
    "2026-11-04T00:04:13+01:00",
    "2026-11-04T00:04:15+01:00",
    "2026-11-04T00:04:17+01:00",
    "2026-11-04T03:19:32+01:00",
    "2026-11-04T03:19:34+01:00",
    "2026-11-04T03:19:36+01:00",
    "2026-11-04T03:24:17+01:00",
    "2026-11-04T07:19:50+01:00",
    "2026-11-04T07:28:11+01:00",
    "2026-11-04T07:28:13+01:00",
    "2026-11-04T07:28:15+01:00",
    "2026-11-04T07:29:04+01:00",
    "2026-11-04T07:29:07+01:00",
    "2026-11-04T07:29:09+01:00",
    "2026-11-04T07:29:17+01:00",
    "2026-11-04T07:29:20+01:00",
    "2026-11-04T07:29:22+01:00",
    "2026-11-04T07:29:32+01:00",
    "2026-11-04T07:30:29+01:00",
    "2026-11-04T07:30:32+01:00",
    "2026-11-04T07:30:34+01:00",
    "2026-11-04T07:41:22+01:00",
    "2026-11-04T07:41:26+01:00",
    "2026-11-04T07:41:29+01:00",
    "2026-11-04T07:41:37+01:00",
    "2026-11-04T07:41:41+01:00",
    "2026-11-04T07:41:52+01:00",
    "2026-11-04T07:41:55+01:00",
    "2026-11-04T07:54:00+01:00",
    "2026-11-04T07:54:03+01:00",
    "2026-11-04T07:54:06+01:00",
    "2026-11-04T07:54:54+01:00",
    "2026-11-04T07:54:57+01:00",
    "2026-11-04T07:54:59+01:00",
    "2026-11-04T08:04:58+01:00",
    "2026-11-04T08:27:23+01:00",
    "2026-11-04T08:27:27+01:00",
    "2026-11-04T08:27:30+01:00",
    "2026-11-04T08:27:33+01:00",
    "2026-11-04T08:37:40+01:00",
    "2026-11-04T08:37:43+01:00",
    "2026-11-04T08:38:45+01:00",
    "2026-11-04T08:38:48+01:00",
    "2026-11-04T08:38:51+01:00",
    "2026-11-04T08:44:57+01:00",
    "2026-11-05T12:03:47+01:00",
    "2026-11-05T12:17:50+01:00",
    "2026-11-05T17:39:06+01:00",
    "2026-11-05T17:39:10+01:00",
    "2026-11-05T17:39:11+01:00",
    "2026-11-05T17:59:07+01:00",
    "2026-11-05T17:59:08+01:00",
    "2026-11-05T17:59:09+01:00",
    "2026-11-05T17:59:53+01:00",
    "2026-11-05T17:59:54+01:00",
    "2026-11-05T18:03:03+01:00",
    "2026-11-05T18:09:16+01:00",
    "2026-11-05T18:09:17+01:00",
    "2026-11-05T18:09:45+01:00"
  ],
  "rev": 173,
  "waiting": null,
  "waits": [
    {
      "kind": "briefing",
      "from": "2026-11-03T20:18:46+01:00",
      "to": "2026-11-03T20:19:59+01:00"
    },
    {
      "kind": "stop",
      "from": "2026-11-03T20:25:04+01:00",
      "to": "2026-11-03T20:37:14+01:00"
    },
    {
      "kind": "stop",
      "from": "2026-11-03T21:18:28+01:00",
      "to": "2026-11-03T21:58:22+01:00"
    }
  ],
  "log": [
    {
      "t": "2026-11-03T20:17:53+01:00",
      "k": "init"
    },
    {
      "t": "2026-11-03T20:18:08+01:00",
      "k": "stage",
      "id": "manifest",
      "act": "start"
    },
    {
      "t": "2026-11-03T20:18:29+01:00",
      "k": "stage",
      "id": "briefing",
      "act": "start"
    },
    {
      "t": "2026-11-03T20:18:46+01:00",
      "k": "ask",
      "kind": "briefing",
      "note": "один вопрос — брать ли из прошлой сборки правку BOM в dashboard_upgrade.py"
    },
    {
      "t": "2026-11-03T20:19:59+01:00",
      "k": "answered",
      "kind": "briefing"
    },
    {
      "t": "2026-11-03T20:20:00+01:00",
      "k": "gate",
      "g": "G1",
      "ok": false,
      "open": 11,
      "total": 11
    },
    {
      "t": "2026-11-03T20:20:00+01:00",
      "k": "stage",
      "id": "spec",
      "act": "start"
    },
    {
      "t": "2026-11-03T20:24:00+01:00",
      "k": "gate",
      "g": "G2",
      "ok": true,
      "found": 4,
      "fixed": 3,
      "deferred": 1
    },
    {
      "t": "2026-11-03T20:24:01+01:00",
      "k": "stage",
      "id": "plan",
      "act": "start"
    },
    {
      "t": "2026-11-03T20:24:32+01:00",
      "k": "tickets",
      "n": 2
    },
    {
      "t": "2026-11-03T20:24:33+01:00",
      "k": "gate",
      "g": "G3",
      "ok": true,
      "problems": 0
    },
    {
      "t": "2026-11-03T20:24:39+01:00",
      "k": "tier",
      "v": "T1"
    },
    {
      "t": "2026-11-03T20:24:48+01:00",
      "k": "plan-models",
      "provider": "anthropic",
      "applied": false,
      "tickets": 2,
      "blocked": 0
    },
    {
      "t": "2026-11-03T20:24:57+01:00",
      "k": "stage",
      "id": "plan",
      "act": "done"
    },
    {
      "t": "2026-11-03T20:24:57+01:00",
      "k": "plan-models",
      "provider": "anthropic",
      "applied": true,
      "tickets": 2,
      "blocked": 0
    },
    {
      "t": "2026-11-03T20:25:04+01:00",
      "k": "ask",
      "kind": "stop",
      "note": "новый чат: агенты зарегистрированы"
    },
    {
      "t": "2026-11-03T20:37:14+01:00",
      "k": "answered",
      "kind": "stop"
    },
    {
      "t": "2026-11-03T20:37:14+01:00",
      "k": "stage",
      "id": "build",
      "act": "start"
    },
    {
      "t": "2026-11-03T20:37:38+01:00",
      "k": "ticket",
      "ids": [
        "01"
      ],
      "act": "start"
    },
    {
      "t": "2026-11-03T20:49:16+01:00",
      "k": "add",
      "key": "report",
      "n": 1
    },
    {
      "t": "2026-11-03T20:54:57+01:00",
      "k": "ticket",
      "ids": [
        "01"
      ],
      "act": "done",
      "tests": {
        "passed": 558,
        "failed": 0
      }
    },
    {
      "t": "2026-11-03T20:55:08+01:00",
      "k": "ticket",
      "ids": [
        "02"
      ],
      "act": "start"
    },
    {
      "t": "2026-11-03T21:02:04+01:00",
      "k": "ticket",
      "ids": [
        "02"
      ],
      "act": "done",
      "tests": {
        "passed": 560,
        "failed": 0
      }
    },
    {
      "t": "2026-11-03T21:02:04+01:00",
      "k": "stage",
      "id": "review",
      "act": "start"
    },
    {
      "t": "2026-11-03T21:06:16+01:00",
      "k": "tickets",
      "n": 3
    },
    {
      "t": "2026-11-03T21:06:16+01:00",
      "k": "gate",
      "g": "G3",
      "ok": true,
      "problems": 0
    },
    {
      "t": "2026-11-03T21:06:16+01:00",
      "k": "gate",
      "g": "G1",
      "ok": false,
      "reason": "plan-changed"
    },
    {
      "t": "2026-11-03T21:06:16+01:00",
      "k": "gate",
      "g": "G2",
      "ok": false,
      "reason": "plan-changed"
    },
    {
      "t": "2026-11-03T21:06:16+01:00",
      "k": "gate",
      "g": "G4",
      "ok": false,
      "reason": "plan-changed"
    },
    {
      "t": "2026-11-03T21:06:22+01:00",
      "k": "add",
      "key": "report",
      "n": 7
    },
    {
      "t": "2026-11-03T21:06:23+01:00",
      "k": "ticket",
      "ids": [
        "F1"
      ],
      "act": "route"
    },
    {
      "t": "2026-11-03T21:06:25+01:00",
      "k": "ticket",
      "ids": [
        "F1"
      ],
      "act": "start"
    },
    {
      "t": "2026-11-03T21:14:02+01:00",
      "k": "ticket",
      "ids": [
        "F1"
      ],
      "act": "review"
    },
    {
      "t": "2026-11-03T21:15:03+01:00",
      "k": "ticket",
      "ids": [
        "F1"
      ],
      "act": "done",
      "tests": {
        "passed": 561,
        "failed": 0
      }
    },
    {
      "t": "2026-11-03T21:15:04+01:00",
      "k": "add",
      "key": "report",
      "n": 1
    },
    {
      "t": "2026-11-03T21:15:04+01:00",
      "k": "stage",
      "id": "final",
      "act": "start"
    },
    {
      "t": "2026-11-03T21:18:04+01:00",
      "k": "gate",
      "g": "G4",
      "ok": false,
      "checked": 6,
      "matched": 5
    },
    {
      "t": "2026-11-03T21:18:05+01:00",
      "k": "tests",
      "passed": 561,
      "failed": 0
    },
    {
      "t": "2026-11-03T21:18:28+01:00",
      "k": "ask",
      "kind": "stop",
      "note": "слепая приёмка: вид «Обзор» по умолчанию — достаточно ли он информативен, доделывать ли"
    },
    {
      "t": "2026-11-03T21:58:22+01:00",
      "k": "answered",
      "kind": "stop"
    },
    {
      "t": "2026-11-03T21:58:23+01:00",
      "k": "tickets",
      "n": 4
    },
    {
      "t": "2026-11-03T21:58:24+01:00",
      "k": "ticket",
      "ids": [
        "F2"
      ],
      "act": "route"
    },
    {
      "t": "2026-11-03T21:58:28+01:00",
      "k": "ticket",
      "ids": [
        "F2"
      ],
      "act": "start"
    },
    {
      "t": "2026-11-03T22:05:37+01:00",
      "k": "ticket",
      "ids": [
        "F2"
      ],
      "act": "review"
    },
    {
      "t": "2026-11-03T22:07:07+01:00",
      "k": "ticket",
      "ids": [
        "F2"
      ],
      "act": "done",
      "tests": {
        "passed": 562,
        "failed": 0
      }
    },
    {
      "t": "2026-11-03T22:07:07+01:00",
      "k": "add",
      "key": "concerns",
      "n": 1
    },
    {
      "t": "2026-11-03T22:07:08+01:00",
      "k": "add",
      "key": "concerns",
      "n": 1
    },
    {
      "t": "2026-11-03T22:09:52+01:00",
      "k": "gate",
      "g": "G4",
      "ok": true,
      "checked": 6,
      "matched": 6
    },
    {
      "t": "2026-11-03T22:09:53+01:00",
      "k": "add",
      "key": "report",
      "n": 1
    },
    {
      "t": "2026-11-03T22:09:54+01:00",
      "k": "add",
      "key": "report",
      "n": 1
    },
    {
      "t": "2026-11-03T22:09:54+01:00",
      "k": "add",
      "key": "report",
      "n": 1
    },
    {
      "t": "2026-11-03T22:09:55+01:00",
      "k": "tests",
      "passed": 562,
      "failed": 0
    },
    {
      "t": "2026-11-03T22:10:18+01:00",
      "k": "gate",
      "g": "G3",
      "ok": true,
      "problems": 0
    },
    {
      "t": "2026-11-03T22:10:18+01:00",
      "k": "gate",
      "g": "G1",
      "ok": false,
      "reason": "plan-changed"
    },
    {
      "t": "2026-11-03T22:10:18+01:00",
      "k": "gate",
      "g": "G2",
      "ok": false,
      "reason": "plan-changed"
    },
    {
      "t": "2026-11-03T22:10:18+01:00",
      "k": "gate",
      "g": "G4",
      "ok": false,
      "reason": "plan-changed"
    },
    {
      "t": "2026-11-03T22:10:59+01:00",
      "k": "gate",
      "g": "G2",
      "ok": true,
      "found": 1,
      "fixed": 0,
      "deferred": 1
    },
    {
      "t": "2026-11-03T22:11:00+01:00",
      "k": "gate",
      "g": "G1",
      "ok": true,
      "open": 0,
      "total": 12
    },
    {
      "t": "2026-11-03T22:11:00+01:00",
      "k": "stage",
      "id": "spec",
      "act": "done"
    },
    {
      "t": "2026-11-03T22:11:01+01:00",
      "k": "gate",
      "g": "G4",
      "ok": true,
      "checked": 6,
      "matched": 6
    },
    {
      "t": "2026-11-03T22:11:02+01:00",
      "k": "stage",
      "id": "final",
      "act": "start"
    },
    {
      "t": "2026-11-03T22:11:06+01:00",
      "k": "finish",
      "result": "В дашборде шесть тем на выбор, логотип, выбор запоминается; «Обзор» информативнее «Классики»; обновление дашборда читает state.js с BOM"
    },
    {
      "t": "2026-11-03T22:31:52+01:00",
      "k": "reopen"
    },
    {
      "t": "2026-11-03T22:32:00+01:00",
      "k": "stage",
      "id": "manifest",
      "act": "start"
    },
    {
      "t": "2026-11-03T22:32:13+01:00",
      "k": "stage",
      "id": "briefing",
      "act": "skip",
      "note": "всё сказано в брифе; открытых вопросов нет"
    },
    {
      "t": "2026-11-03T22:32:14+01:00",
      "k": "gate",
      "g": "G1",
      "ok": false,
      "open": 2,
      "total": 14
    },
    {
      "t": "2026-11-03T22:32:14+01:00",
      "k": "stage",
      "id": "spec",
      "act": "start"
    },
    {
      "t": "2026-11-03T22:33:15+01:00",
      "k": "tickets",
      "n": 5
    },
    {
      "t": "2026-11-03T22:33:16+01:00",
      "k": "gate",
      "g": "G3",
      "ok": false,
      "problems": 2
    },
    {
      "t": "2026-11-03T22:33:16+01:00",
      "k": "gate",
      "g": "G1",
      "ok": false,
      "reason": "plan-changed"
    },
    {
      "t": "2026-11-03T22:33:16+01:00",
      "k": "gate",
      "g": "G2",
      "ok": false,
      "reason": "plan-changed"
    },
    {
      "t": "2026-11-03T22:33:16+01:00",
      "k": "gate",
      "g": "G4",
      "ok": false,
      "reason": "plan-changed"
    },
    {
      "t": "2026-11-03T22:33:17+01:00",
      "k": "tier",
      "v": "T0"
    },
    {
      "t": "2026-11-03T22:33:22+01:00",
      "k": "tickets",
      "n": 5
    },
    {
      "t": "2026-11-03T22:33:22+01:00",
      "k": "gate",
      "g": "G3",
      "ok": false,
      "problems": 2
    },
    {
      "t": "2026-11-03T22:33:28+01:00",
      "k": "tickets",
      "n": 5
    },
    {
      "t": "2026-11-03T22:33:29+01:00",
      "k": "gate",
      "g": "G3",
      "ok": false,
      "problems": 2
    },
    {
      "t": "2026-11-03T22:33:37+01:00",
      "k": "tickets",
      "n": 5
    },
    {
      "t": "2026-11-03T22:33:37+01:00",
      "k": "gate",
      "g": "G3",
      "ok": true,
      "problems": 0
    },
    {
      "t": "2026-11-03T22:33:41+01:00",
      "k": "gate",
      "g": "G2",
      "ok": true,
      "found": 3,
      "fixed": 2,
      "deferred": 1
    },
    {
      "t": "2026-11-03T22:33:42+01:00",
      "k": "gate",
      "g": "G1",
      "ok": true,
      "open": 0,
      "total": 14
    },
    {
      "t": "2026-11-03T22:33:42+01:00",
      "k": "stage",
      "id": "spec",
      "act": "done"
    },
    {
      "t": "2026-11-03T22:33:59+01:00",
      "k": "tickets",
      "n": 5
    },
    {
      "t": "2026-11-03T22:34:00+01:00",
      "k": "gate",
      "g": "G3",
      "ok": true,
      "problems": 0
    },
    {
      "t": "2026-11-03T22:34:00+01:00",
      "k": "gate",
      "g": "G1",
      "ok": false,
      "reason": "plan-changed"
    },
    {
      "t": "2026-11-03T22:34:00+01:00",
      "k": "gate",
      "g": "G2",
      "ok": false,
      "reason": "plan-changed"
    },
    {
      "t": "2026-11-03T22:34:00+01:00",
      "k": "gate",
      "g": "G4",
      "ok": false,
      "reason": "plan-changed"
    },
    {
      "t": "2026-11-03T22:34:10+01:00",
      "k": "gate",
      "g": "G2",
      "ok": true,
      "found": 3,
      "fixed": 2,
      "deferred": 1
    },
    {
      "t": "2026-11-03T22:34:10+01:00",
      "k": "gate",
      "g": "G1",
      "ok": true,
      "open": 0,
      "total": 14
    },
    {
      "t": "2026-11-03T22:34:10+01:00",
      "k": "stage",
      "id": "spec",
      "act": "done"
    },
    {
      "t": "2026-11-03T22:34:11+01:00",
      "k": "stage",
      "id": "plan",
      "act": "start"
    },
    {
      "t": "2026-11-03T22:34:12+01:00",
      "k": "stage",
      "id": "plan",
      "act": "done"
    },
    {
      "t": "2026-11-03T22:34:13+01:00",
      "k": "stage",
      "id": "build",
      "act": "start"
    },
    {
      "t": "2026-11-03T22:34:14+01:00",
      "k": "ticket",
      "ids": [
        "F3"
      ],
      "act": "route"
    },
    {
      "t": "2026-11-03T22:34:15+01:00",
      "k": "ticket",
      "ids": [
        "F3"
      ],
      "act": "start"
    },
    {
      "t": "2026-11-03T22:54:03+01:00",
      "k": "ticket",
      "ids": [
        "F3"
      ],
      "act": "done",
      "tests": {
        "passed": 568,
        "failed": 0
      }
    },
    {
      "t": "2026-11-03T22:59:28+01:00",
      "k": "add",
      "key": "concerns",
      "n": 1
    },
    {
      "t": "2026-11-03T22:59:29+01:00",
      "k": "add",
      "key": "concerns",
      "n": 1
    },
    {
      "t": "2026-11-03T22:59:30+01:00",
      "k": "add",
      "key": "concerns",
      "n": 1
    },
    {
      "t": "2026-11-03T23:01:04+01:00",
      "k": "tickets",
      "n": 7
    },
    {
      "t": "2026-11-03T23:01:05+01:00",
      "k": "gate",
      "g": "G3",
      "ok": true,
      "problems": 0
    },
    {
      "t": "2026-11-03T23:01:05+01:00",
      "k": "gate",
      "g": "G1",
      "ok": false,
      "reason": "plan-changed"
    },
    {
      "t": "2026-11-03T23:01:05+01:00",
      "k": "gate",
      "g": "G2",
      "ok": false,
      "reason": "plan-changed"
    },
    {
      "t": "2026-11-03T23:01:05+01:00",
      "k": "gate",
      "g": "G4",
      "ok": false,
      "reason": "plan-changed"
    },
    {
      "t": "2026-11-03T23:01:25+01:00",
      "k": "tickets",
      "n": 7
    },
    {
      "t": "2026-11-03T23:02:05+01:00",
      "k": "gate",
      "g": "G3",
      "ok": true,
      "problems": 0
    },
    {
      "t": "2026-11-03T23:02:05+01:00",
      "k": "gate",
      "g": "G1",
      "ok": false,
      "reason": "plan-changed"
    },
    {
      "t": "2026-11-03T23:02:05+01:00",
      "k": "gate",
      "g": "G2",
      "ok": false,
      "reason": "plan-changed"
    },
    {
      "t": "2026-11-03T23:02:05+01:00",
      "k": "gate",
      "g": "G4",
      "ok": false,
      "reason": "plan-changed"
    },
    {
      "t": "2026-11-03T23:02:09+01:00",
      "k": "stage",
      "id": "build",
      "act": "start"
    },
    {
      "t": "2026-11-03T23:02:10+01:00",
      "k": "ticket",
      "ids": [
        "F4"
      ],
      "act": "route"
    },
    {
      "t": "2026-11-03T23:02:11+01:00",
      "k": "ticket",
      "ids": [
        "F4"
      ],
      "act": "start"
    },
    {
      "t": "2026-11-03T23:23:02+01:00",
      "k": "ticket",
      "ids": [
        "F4"
      ],
      "act": "done",
      "tests": {
        "passed": 578,
        "failed": 0
      }
    },
    {
      "t": "2026-11-03T23:23:03+01:00",
      "k": "ticket",
      "ids": [
        "F5"
      ],
      "act": "route"
    },
    {
      "t": "2026-11-03T23:23:04+01:00",
      "k": "ticket",
      "ids": [
        "F5"
      ],
      "act": "start"
    },
    {
      "t": "2026-11-03T23:41:28+01:00",
      "k": "ticket",
      "ids": [
        "F5"
      ],
      "act": "done",
      "tests": {
        "passed": 585,
        "failed": 0
      }
    },
    {
      "t": "2026-11-03T23:47:14+01:00",
      "k": "blocker",
      "id": "B01",
      "act": "open",
      "ticket": "F5"
    },
    {
      "t": "2026-11-03T23:47:14+01:00",
      "k": "ticket",
      "ids": [
        "F5"
      ],
      "act": "repair",
      "note": "B1: таск без startedAt пропадает из Таймлайна, а Таймлайн и Компактный показывают ложное «тасков нет» при T.length>0"
    },
    {
      "t": "2026-11-03T23:47:15+01:00",
      "k": "add",
      "key": "concerns",
      "n": 1
    },
    {
      "t": "2026-11-03T23:47:17+01:00",
      "k": "add",
      "key": "concerns",
      "n": 1
    },
    {
      "t": "2026-11-03T23:55:30+01:00",
      "k": "blocker",
      "id": "B01",
      "act": "resolve",
      "ticket": "F5"
    },
    {
      "t": "2026-11-03T23:55:32+01:00",
      "k": "ticket",
      "ids": [
        "F5"
      ],
      "act": "done",
      "tests": {
        "passed": 586,
        "failed": 0
      }
    },
    {
      "t": "2026-11-03T23:55:34+01:00",
      "k": "add",
      "key": "concerns",
      "n": 1
    },
    {
      "t": "2026-11-03T23:55:35+01:00",
      "k": "gate",
      "g": "G3",
      "ok": true,
      "problems": 0
    },
    {
      "t": "2026-11-03T23:56:55+01:00",
      "k": "gate",
      "g": "G2",
      "ok": true,
      "found": 5,
      "fixed": 5,
      "deferred": 0
    },
    {
      "t": "2026-11-03T23:56:56+01:00",
      "k": "gate",
      "g": "G1",
      "ok": true,
      "open": 0,
      "total": 15
    },
    {
      "t": "2026-11-03T23:56:56+01:00",
      "k": "stage",
      "id": "spec",
      "act": "done"
    },
    {
      "t": "2026-11-04T00:03:51+01:00",
      "k": "gate",
      "g": "G4",
      "ok": false,
      "checked": 6,
      "matched": 4
    },
    {
      "t": "2026-11-04T00:04:11+01:00",
      "k": "tickets",
      "n": 8
    },
    {
      "t": "2026-11-04T00:04:13+01:00",
      "k": "gate",
      "g": "G3",
      "ok": true,
      "problems": 0
    },
    {
      "t": "2026-11-04T00:04:13+01:00",
      "k": "gate",
      "g": "G1",
      "ok": false,
      "reason": "plan-changed"
    },
    {
      "t": "2026-11-04T00:04:13+01:00",
      "k": "gate",
      "g": "G2",
      "ok": false,
      "reason": "plan-changed"
    },
    {
      "t": "2026-11-04T00:04:13+01:00",
      "k": "gate",
      "g": "G4",
      "ok": false,
      "reason": "plan-changed"
    },
    {
      "t": "2026-11-04T00:04:15+01:00",
      "k": "ticket",
      "ids": [
        "F6"
      ],
      "act": "route"
    },
    {
      "t": "2026-11-04T00:04:17+01:00",
      "k": "ticket",
      "ids": [
        "F6"
      ],
      "act": "start"
    },
    {
      "t": "2026-11-04T03:19:32+01:00",
      "k": "add",
      "key": "concerns",
      "n": 1
    },
    {
      "t": "2026-11-04T03:19:34+01:00",
      "k": "add",
      "key": "concerns",
      "n": 1
    },
    {
      "t": "2026-11-04T03:19:36+01:00",
      "k": "add",
      "key": "concerns",
      "n": 1
    },
    {
      "t": "2026-11-04T03:24:17+01:00",
      "k": "ticket",
      "ids": [
        "F6"
      ],
      "act": "done",
      "tests": {
        "passed": 593,
        "failed": 0
      }
    },
    {
      "t": "2026-11-04T07:19:50+01:00",
      "k": "blocker",
      "id": "B02",
      "act": "open",
      "ticket": "F6"
    },
    {
      "t": "2026-11-04T07:19:50+01:00",
      "k": "ticket",
      "ids": [
        "F6"
      ],
      "act": "repair",
      "note": "R1: правило ≤520px «.tools .views{order:1}» не должно задевать Классику (раскладка Классики при ≤520 px как до F4). R2: в Ресурсах нет данных о токенах (нет usageEvents) — показывать «—», а не «0»; «0» только для таска, у которого события есть или который ожидает и его токены заведомо нулевые"
    },
    {
      "t": "2026-11-04T07:28:11+01:00",
      "k": "blocker",
      "id": "B02",
      "act": "resolve",
      "ticket": "F6"
    },
    {
      "t": "2026-11-04T07:28:13+01:00",
      "k": "ticket",
      "ids": [
        "F6"
      ],
      "act": "done",
      "tests": {
        "passed": 595,
        "failed": 0
      }
    },
    {
      "t": "2026-11-04T07:28:15+01:00",
      "k": "gate",
      "g": "G3",
      "ok": true,
      "problems": 0
    },
    {
      "t": "2026-11-04T07:28:15+01:00",
      "k": "gate",
      "g": "G1",
      "ok": false,
      "reason": "plan-changed"
    },
    {
      "t": "2026-11-04T07:28:15+01:00",
      "k": "gate",
      "g": "G2",
      "ok": false,
      "reason": "plan-changed"
    },
    {
      "t": "2026-11-04T07:28:15+01:00",
      "k": "gate",
      "g": "G4",
      "ok": false,
      "reason": "plan-changed"
    },
    {
      "t": "2026-11-04T07:29:04+01:00",
      "k": "ticket",
      "ids": [
        "F4"
      ],
      "act": "route"
    },
    {
      "t": "2026-11-04T07:29:07+01:00",
      "k": "ticket",
      "ids": [
        "F5"
      ],
      "act": "route"
    },
    {
      "t": "2026-11-04T07:29:09+01:00",
      "k": "ticket",
      "ids": [
        "F6"
      ],
      "act": "route"
    },
    {
      "t": "2026-11-04T07:29:17+01:00",
      "k": "ticket",
      "ids": [
        "F4"
      ],
      "act": "done",
      "tests": {
        "passed": 578,
        "failed": 0
      }
    },
    {
      "t": "2026-11-04T07:29:20+01:00",
      "k": "ticket",
      "ids": [
        "F5"
      ],
      "act": "done",
      "tests": {
        "passed": 586,
        "failed": 0
      }
    },
    {
      "t": "2026-11-04T07:29:22+01:00",
      "k": "ticket",
      "ids": [
        "F6"
      ],
      "act": "done",
      "tests": {
        "passed": 595,
        "failed": 0
      }
    },
    {
      "t": "2026-11-04T07:29:32+01:00",
      "k": "gate",
      "g": "G3",
      "ok": true,
      "problems": 0
    },
    {
      "t": "2026-11-04T07:30:29+01:00",
      "k": "gate",
      "g": "G2",
      "ok": true,
      "found": 3,
      "fixed": 3,
      "deferred": 0
    },
    {
      "t": "2026-11-04T07:30:32+01:00",
      "k": "gate",
      "g": "G1",
      "ok": true,
      "open": 0,
      "total": 15
    },
    {
      "t": "2026-11-04T07:30:32+01:00",
      "k": "stage",
      "id": "spec",
      "act": "done"
    },
    {
      "t": "2026-11-04T07:30:34+01:00",
      "k": "stage",
      "id": "build",
      "act": "start"
    },
    {
      "t": "2026-11-04T07:41:22+01:00",
      "k": "gate",
      "g": "G4",
      "ok": false,
      "checked": 8,
      "matched": 7
    },
    {
      "t": "2026-11-04T07:41:26+01:00",
      "k": "add",
      "key": "report",
      "n": 1
    },
    {
      "t": "2026-11-04T07:41:29+01:00",
      "k": "add",
      "key": "report",
      "n": 1
    },
    {
      "t": "2026-11-04T07:41:37+01:00",
      "k": "tickets",
      "n": 9
    },
    {
      "t": "2026-11-04T07:41:41+01:00",
      "k": "gate",
      "g": "G3",
      "ok": true,
      "problems": 0
    },
    {
      "t": "2026-11-04T07:41:41+01:00",
      "k": "gate",
      "g": "G1",
      "ok": false,
      "reason": "plan-changed"
    },
    {
      "t": "2026-11-04T07:41:41+01:00",
      "k": "gate",
      "g": "G2",
      "ok": false,
      "reason": "plan-changed"
    },
    {
      "t": "2026-11-04T07:41:41+01:00",
      "k": "gate",
      "g": "G4",
      "ok": false,
      "reason": "plan-changed"
    },
    {
      "t": "2026-11-04T07:41:52+01:00",
      "k": "ticket",
      "ids": [
        "F7"
      ],
      "act": "route"
    },
    {
      "t": "2026-11-04T07:41:55+01:00",
      "k": "ticket",
      "ids": [
        "F7"
      ],
      "act": "start"
    },
    {
      "t": "2026-11-04T07:54:00+01:00",
      "k": "ticket",
      "ids": [
        "F7"
      ],
      "act": "done",
      "tests": {
        "passed": 599,
        "failed": 0
      }
    },
    {
      "t": "2026-11-04T07:54:03+01:00",
      "k": "add",
      "key": "concerns",
      "n": 1
    },
    {
      "t": "2026-11-04T07:54:06+01:00",
      "k": "gate",
      "g": "G3",
      "ok": true,
      "problems": 0
    },
    {
      "t": "2026-11-04T07:54:54+01:00",
      "k": "gate",
      "g": "G2",
      "ok": true,
      "found": 3,
      "fixed": 3,
      "deferred": 0
    },
    {
      "t": "2026-11-04T07:54:57+01:00",
      "k": "gate",
      "g": "G1",
      "ok": true,
      "open": 0,
      "total": 15
    },
    {
      "t": "2026-11-04T07:54:57+01:00",
      "k": "stage",
      "id": "spec",
      "act": "done"
    },
    {
      "t": "2026-11-04T07:54:59+01:00",
      "k": "stage",
      "id": "build",
      "act": "start"
    },
    {
      "t": "2026-11-04T08:04:58+01:00",
      "k": "gate",
      "g": "G4",
      "ok": false,
      "checked": 8,
      "matched": 6
    },
    {
      "t": "2026-11-04T08:27:23+01:00",
      "k": "tickets",
      "n": 10
    },
    {
      "t": "2026-11-04T08:27:27+01:00",
      "k": "gate",
      "g": "G3",
      "ok": true,
      "problems": 0
    },
    {
      "t": "2026-11-04T08:27:27+01:00",
      "k": "gate",
      "g": "G1",
      "ok": false,
      "reason": "plan-changed"
    },
    {
      "t": "2026-11-04T08:27:27+01:00",
      "k": "gate",
      "g": "G2",
      "ok": false,
      "reason": "plan-changed"
    },
    {
      "t": "2026-11-04T08:27:27+01:00",
      "k": "gate",
      "g": "G4",
      "ok": false,
      "reason": "plan-changed"
    },
    {
      "t": "2026-11-04T08:27:30+01:00",
      "k": "ticket",
      "ids": [
        "F8"
      ],
      "act": "route"
    },
    {
      "t": "2026-11-04T08:27:33+01:00",
      "k": "ticket",
      "ids": [
        "F8"
      ],
      "act": "start"
    },
    {
      "t": "2026-11-04T08:37:40+01:00",
      "k": "ticket",
      "ids": [
        "F8"
      ],
      "act": "done",
      "tests": {
        "passed": 599,
        "failed": 0
      }
    },
    {
      "t": "2026-11-04T08:37:43+01:00",
      "k": "gate",
      "g": "G3",
      "ok": true,
      "problems": 0
    },
    {
      "t": "2026-11-04T08:38:45+01:00",
      "k": "gate",
      "g": "G2",
      "ok": true,
      "found": 5,
      "fixed": 4,
      "deferred": 1
    },
    {
      "t": "2026-11-04T08:38:48+01:00",
      "k": "gate",
      "g": "G1",
      "ok": true,
      "open": 0,
      "total": 15
    },
    {
      "t": "2026-11-04T08:38:48+01:00",
      "k": "stage",
      "id": "spec",
      "act": "done"
    },
    {
      "t": "2026-11-04T08:38:51+01:00",
      "k": "stage",
      "id": "build",
      "act": "start"
    },
    {
      "t": "2026-11-04T08:44:57+01:00",
      "k": "gate",
      "g": "G4",
      "ok": false,
      "checked": 14,
      "matched": 12
    },
    {
      "t": "2026-11-05T12:03:47+01:00",
      "k": "gate",
      "g": "G4",
      "ok": false,
      "checked": 12,
      "matched": 11
    },
    {
      "t": "2026-11-05T12:17:50+01:00",
      "k": "gate",
      "g": "G4",
      "ok": false,
      "checked": 20,
      "matched": 19
    },
    {
      "t": "2026-11-05T17:39:06+01:00",
      "k": "tickets",
      "n": 11
    },
    {
      "t": "2026-11-05T17:39:10+01:00",
      "k": "gate",
      "g": "G3",
      "ok": true,
      "problems": 0
    },
    {
      "t": "2026-11-05T17:39:10+01:00",
      "k": "gate",
      "g": "G1",
      "ok": false,
      "reason": "plan-changed"
    },
    {
      "t": "2026-11-05T17:39:10+01:00",
      "k": "gate",
      "g": "G2",
      "ok": false,
      "reason": "plan-changed"
    },
    {
      "t": "2026-11-05T17:39:10+01:00",
      "k": "gate",
      "g": "G4",
      "ok": false,
      "reason": "plan-changed"
    },
    {
      "t": "2026-11-05T17:39:11+01:00",
      "k": "ticket",
      "ids": [
        "F9"
      ],
      "act": "route"
    },
    {
      "t": "2026-11-05T17:39:11+01:00",
      "k": "ticket",
      "ids": [
        "F9"
      ],
      "act": "start"
    },
    {
      "t": "2026-11-05T17:59:07+01:00",
      "k": "ticket",
      "ids": [
        "F9"
      ],
      "act": "done",
      "tests": {
        "passed": 603,
        "failed": 0
      }
    },
    {
      "t": "2026-11-05T17:59:08+01:00",
      "k": "gate",
      "g": "G3",
      "ok": true,
      "problems": 0
    },
    {
      "t": "2026-11-05T17:59:09+01:00",
      "k": "add",
      "key": "concerns",
      "n": 1
    },
    {
      "t": "2026-11-05T17:59:53+01:00",
      "k": "gate",
      "g": "G2",
      "ok": true,
      "found": 4,
      "fixed": 3,
      "deferred": 1
    },
    {
      "t": "2026-11-05T17:59:54+01:00",
      "k": "gate",
      "g": "G1",
      "ok": true,
      "open": 0,
      "total": 15
    },
    {
      "t": "2026-11-05T17:59:54+01:00",
      "k": "stage",
      "id": "spec",
      "act": "done"
    },
    {
      "t": "2026-11-05T17:59:54+01:00",
      "k": "stage",
      "id": "build",
      "act": "start"
    },
    {
      "t": "2026-11-05T18:03:03+01:00",
      "k": "add",
      "key": "concerns",
      "n": 1
    },
    {
      "t": "2026-11-05T18:09:16+01:00",
      "k": "gate",
      "g": "G4",
      "ok": true,
      "checked": 16,
      "matched": 16
    },
    {
      "t": "2026-11-05T18:09:17+01:00",
      "k": "tests",
      "passed": 603,
      "failed": 0
    },
    {
      "t": "2026-11-05T18:09:45+01:00",
      "k": "finish",
      "result": "В дашборде восемь видов на выбор, «Обзор» и «Компактный» подогнаны под макеты, лого, заметки по таскам, подписи на полосах Ганта; обновление дашборда читает state.js с BOM"
    }
  ],
  "reqList": [
    {
      "id": "R01",
      "text": "«Давай сделаем возможность видоизменять вид дашборда»",
      "status": "done"
    },
    {
      "id": "R02",
      "text": "«Например, на более информативные»",
      "status": "done"
    },
    {
      "id": "R03",
      "text": "«Как вот эти, к примеру» (макеты: артефакт Claude Design и Figma «Autopilot Dashboard — новые виды»)",
      "status": "done"
    },
    {
      "id": "R04",
      "text": "«посмотр, сложно ли это сделать и как это можно решить самым эффективным способом»",
      "status": "done"
    },
    {
      "id": "R05",
      "text": "«Имеется в виду выбор theme»",
      "status": "done"
    },
    {
      "id": "R06",
      "text": "«Дашборд по умолчанию не совсем информативно»",
      "status": "done"
    },
    {
      "id": "R07",
      "text": "«Надо сделать возможность менять ее на более лучшие информативные темы»",
      "status": "done"
    },
    {
      "id": "R08",
      "text": "«сделать несколько на выбор для большего пользовательского опыта»",
      "status": "done"
    },
    {
      "id": "R09i",
      "text": "(подразумевается) выбранная тема запоминается, как язык и светлая/тёмная",
      "status": "done"
    },
    {
      "id": "R10i",
      "text": "(подразумевается) дашборд без выбора и существующие проекты работают как раньше, тесты зелёные",
      "status": "done"
    },
    {
      "id": "G01",
      "text": "«Да, согласен с твоим мнением.» (взять правку: dashboard_upgrade.py:28 разбирает state.js вручную, BOM ломает обновление дашборда)",
      "status": "done"
    },
    {
      "id": "G02",
      "text": "«Да, и не забудь вставлять в дешборд наш лого.»",
      "status": "done"
    },
    {
      "id": "G03",
      "text": "«Добить «Обзор».» (известные недостатки вида «Обзор» из PROGRESS: нет ожидающих тасков и волн, дубли блоков, подпись версии в рейке, подсветка пункта рейки в «Таймлайне», проверка узкой панели и светлой/тёмной темы)",
      "status": "done"
    },
    {
      "id": "G04",
      "text": "«Затем постарайся сгенерировать пару новых тем.»",
      "status": "done"
    },
    {
      "id": "G05",
      "text": "«Посмотр вот это.» + «Подогнать темы» (макеты из HANDOFF_dashboard.md и архива: раскладка, палитра, названия видов; схема состояния и ap.py не меняются)",
      "status": "done"
    }
  ],
  "gates": {
    "G1": {
      "ok": true,
      "at": "2026-11-05T17:59:54+01:00",
      "open": 0,
      "total": 15
    },
    "G3": {
      "ok": true,
      "at": "2026-11-05T17:59:08+01:00",
      "problems": 0
    },
    "G2": {
      "ok": true,
      "at": "2026-11-05T17:59:53+01:00",
      "found": 4,
      "fixed": 3,
      "deferred": 1
    },
    "G4": {
      "ok": true,
      "at": "2026-11-05T18:09:16+01:00",
      "checked": 16,
      "matched": 16
    }
  },
  "result": "В дашборде восемь видов на выбор, «Обзор» и «Компактный» подогнаны под макеты, лого, заметки по таскам, подписи на полосах Ганта; обновление дашборда читает state.js с BOM",
  "gateMark": "6afa4034497cfda1090caab43f915369670c09850aa41e6b1cdd175ae7233f5a",
  "skillVersion": "2.6.0",
  "roleAgents": {
    "reviewer": {
      "agentType": "autopilot-reviewer-2026-11-03-dashboard-themes",
      "agentFile": ".claude/agents/autopilot-reviewer-2026-11-03-dashboard-themes.md",
      "model": "sonnet",
      "effort": "high",
      "effortEnforced": true,
      "profileSha": "8e286f9b8c286616356e6479a3a5b5ffecc9609412ae99cce165251e8de546fc"
    },
    "acceptance": {
      "agentType": "autopilot-acceptance-2026-11-03-dashboard-themes",
      "agentFile": ".claude/agents/autopilot-acceptance-2026-11-03-dashboard-themes.md",
      "model": "sonnet",
      "effort": "medium",
      "effortEnforced": true,
      "profileSha": "027df0a618b875261f2d78a4bfc7ac87575999d6dec1010e2fc0aa569d9ed30a"
    },
    "explorer": {
      "agentType": "autopilot-explorer-2026-11-03-dashboard-themes",
      "agentFile": ".claude/agents/autopilot-explorer-2026-11-03-dashboard-themes.md",
      "model": "haiku",
      "effort": "low",
      "effortEnforced": true,
      "profileSha": "0c14407be1446ca45babc0d42f44a8d656ee17c6d56d2f2986c1d3106847f548"
    }
  },
  "repairAgent": {
    "agentType": "autopilot-executor-repair-2026-11-03-dashboard-themes",
    "agentFile": ".claude/agents/autopilot-executor-repair-2026-11-03-dashboard-themes.md",
    "model": "sonnet",
    "effort": "high",
    "effortEnforced": true,
    "profileSha": "c0bdf44942d330a146f54898e8405e93aca307e8ab51acb897cbfec365a0b193"
  },
  "report": [
    "Тема «Итог»: строка тестов зелёная даже при упавших тестах и расхождениях слепой приёмки — dashboard-template.html:1750",
    "Полоса таймлайна считается по календарному времени, подпись — по активному: у идущего таска они расходятся — dashboard-template.html:1714",
    "Остались неиспользуемые CSS-правила .brand-name и .rail-symbol — dashboard-template.html:76,260,464,488",
    "Тест «Классика совпадает с прежней вёрсткой» проверяет только наличие spotlight; полное сравнение сделал ревьюер вручную, токен в токен — tests/test_dashboard_views.py:159",
    "Документация новой темы не говорит, что нужны якоря mission/tasks/models/quality — docs/autopilot/dashboard-views.md:48",
    "CHANGELOG: логотип стоит ещё и в боковой рейке — CHANGELOG.md:14",
    "Ошибка чтения state.js (OSError) выдаётся как «not valid JSON» — dashboard_upgrade.py:32",
    "Мелочь: правило .cockpit-content:focus{outline:none} убирает рамку фокуса у основного блока на любой ширине — dashboard-template.html:577",
    "Обзор не показывает ожидающие таски и разбивку по волнам (есть в Классике) — слепая приёмка",
    "В боковой рейке: подпись «2.3 / 2.3.0» при версии навыка 2.6.0; в Таймлайне подсвечен пункт «Overview» — слепая приёмка, не чинилось",
    "Не проверено в браузере: file://, узкая панель, завершённая сборка с реальными данными",
    "Подгонка под макеты — частично по замыслу: нет блоков, для которых в state.js нет полей (замечания ревью «было → стало», решения за вас, токены вход/выход/кэш по таскам, журнал контроллера, матрица шагов изоляции, критический путь, штриховка «ждали вас», кнопки «Починить / Принять»)",
    "Слепая приёмка не проверила: контраст 4.5:1 измерением в браузере, старое и пустое состояние в браузере, живой сервер, Классику при 440 px сравнением с исходным коммитом"
  ],
  "planContractDigest": "c451daa448d53f7a38621334f13ebb285dcb57e8a0309449c83069341fc623c6",
  "planValidationDigest": "4b6c376921832e2ac575d67e043091d45444a0b90e8af1007de018f6c74103a2"
}
