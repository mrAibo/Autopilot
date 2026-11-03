window.STATE =
{
  "version": 2,
  "slug": "dashboard-themes",
  "dir": "2026-11-03-dashboard-themes--wip",
  "title": "Выбор темы дашборда: несколько информативных видов",
  "mode": "semi",
  "depth": "normal",
  "tier": "T1",
  "strictRouting": true,
  "gateSigned": true,
  "sequentialHost": false,
  "isolateTickets": false,
  "briefFile": "2026-11-03-brief.md",
  "memoryFile": "AGENTS.md",
  "memoryOwner": "autopilot",
  "skillDir": "C:/Users/crown/Downloads/Projects/Autopilot/skills/autopilot",
  "baseCommit": null,
  "startedAt": "2026-11-03T20:17:53+01:00",
  "updatedAt": "2026-11-03T20:24:39+01:00",
  "finishedAt": null,
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
      "startedAt": "2026-11-03T20:18:08+01:00",
      "finishedAt": "2026-11-03T20:18:29+01:00"
    },
    {
      "id": "briefing",
      "status": "done",
      "startedAt": "2026-11-03T20:18:29+01:00",
      "finishedAt": "2026-11-03T20:20:00+01:00"
    },
    {
      "id": "spec",
      "status": "done",
      "startedAt": "2026-11-03T20:20:00+01:00",
      "finishedAt": "2026-11-03T20:24:01+01:00"
    },
    {
      "id": "plan",
      "status": "active",
      "startedAt": "2026-11-03T20:24:01+01:00"
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
    "total": 12,
    "done": 0,
    "inTicket": 12,
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
      "status": "pending",
      "retries": 0,
      "repairs": 0
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
      "status": "pending",
      "retries": 0,
      "repairs": 0
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
    "found": 4,
    "fixed": 3,
    "deferred": 1,
    "items": [
      "«Как вот эти» (артефакт Claude Design) — состав видов недоступен для чтения: ориентир Figma"
    ]
  },
  "concerns": [],
  "blockingFindings": [],
  "blind": null,
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
    "2026-11-03T20:24:39+01:00"
  ],
  "rev": 13,
  "waiting": null,
  "waits": [
    {
      "kind": "briefing",
      "from": "2026-11-03T20:18:46+01:00",
      "to": "2026-11-03T20:19:59+01:00"
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
    }
  ],
  "reqList": [
    {
      "id": "R01",
      "text": "«Давай сделаем возможность видоизменять вид дашборда»",
      "status": "in-ticket"
    },
    {
      "id": "R02",
      "text": "«Например, на более информативные»",
      "status": "in-ticket"
    },
    {
      "id": "R03",
      "text": "«Как вот эти, к примеру» (макеты: артефакт Claude Design и Figma «Autopilot Dashboard — новые виды»)",
      "status": "in-ticket"
    },
    {
      "id": "R04",
      "text": "«посмотр, сложно ли это сделать и как это можно решить самым эффективным способом»",
      "status": "in-ticket"
    },
    {
      "id": "R05",
      "text": "«Имеется в виду выбор theme»",
      "status": "in-ticket"
    },
    {
      "id": "R06",
      "text": "«Дашборд по умолчанию не совсем информативно»",
      "status": "in-ticket"
    },
    {
      "id": "R07",
      "text": "«Надо сделать возможность менять ее на более лучшие информативные темы»",
      "status": "in-ticket"
    },
    {
      "id": "R08",
      "text": "«сделать несколько на выбор для большего пользовательского опыта»",
      "status": "in-ticket"
    },
    {
      "id": "R09i",
      "text": "(подразумевается) выбранная тема запоминается, как язык и светлая/тёмная",
      "status": "in-ticket"
    },
    {
      "id": "R10i",
      "text": "(подразумевается) дашборд без выбора и существующие проекты работают как раньше, тесты зелёные",
      "status": "in-ticket"
    },
    {
      "id": "G01",
      "text": "«Да, согласен с твоим мнением.» (взять правку: dashboard_upgrade.py:28 разбирает state.js вручную, BOM ломает обновление дашборда)",
      "status": "in-ticket"
    },
    {
      "id": "G02",
      "text": "«Да, и не забудь вставлять в дешборд наш лого.»",
      "status": "in-ticket"
    }
  ],
  "gates": {
    "G1": {
      "ok": false,
      "at": "2026-11-03T20:20:00+01:00",
      "open": 11,
      "total": 11
    },
    "G2": {
      "ok": true,
      "at": "2026-11-03T20:24:00+01:00",
      "found": 4,
      "fixed": 3,
      "deferred": 1
    },
    "G3": {
      "ok": true,
      "at": "2026-11-03T20:24:33+01:00",
      "problems": 0
    }
  },
  "result": null,
  "gateMark": "6afa4034497cfda1090caab43f915369670c09850aa41e6b1cdd175ae7233f5a",
  "skillVersion": "2.6.0",
  "planContractDigest": "dffce9ebfe35e4a463b519a8637f31afc960efa5ca788cce88f905999fceb2f5",
  "planValidationDigest": "74f698f85703590ae7d10de9beda5177e6b1269ebbe8a172f271c7a9e660ccc1"
}
