window.STATE =
{
  "version": 2,
  "slug": "audit-fixes",
  "dir": "2026-11-03-audit-fixes--wip",
  "title": "Исправления по аудиту Autopilot 2026-11-03",
  "mode": "semi",
  "depth": "normal",
  "tier": null,
  "strictRouting": true,
  "sequentialHost": false,
  "isolateTickets": false,
  "briefFile": "2026-11-03-brief.md",
  "memoryFile": "AGENTS.md",
  "memoryOwner": "autopilot",
  "skillDir": "/home/user/Autopilot/skills/autopilot",
  "baseCommit": null,
  "startedAt": "2026-11-03T16:24:15+00:00",
  "updatedAt": "2026-11-03T16:25:03+00:00",
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
      "status": "active",
      "startedAt": "2026-11-03T16:24:47+00:00"
    },
    {
      "id": "spec",
      "status": "pending"
    },
    {
      "id": "plan",
      "status": "pending"
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
    "inTicket": 0,
    "inSpec": 0,
    "placeholder": 0,
    "deferred": 0,
    "dropped": 0
  },
  "tickets": [],
  "tests": null,
  "usageEvents": [],
  "budgetTokens": null,
  "debt": {
    "placeholders": [],
    "assumptions": [],
    "emptyEnv": []
  },
  "additions": [],
  "coverage": null,
  "concerns": [],
  "blockingFindings": [],
  "blind": null,
  "beats": [
    "2026-11-03T16:24:15+00:00",
    "2026-11-03T16:24:27+00:00",
    "2026-11-03T16:24:42+00:00",
    "2026-11-03T16:24:47+00:00",
    "2026-11-03T16:25:03+00:00"
  ],
  "rev": 6,
  "waiting": {
    "kind": "briefing",
    "since": "2026-11-03T16:25:03+00:00",
    "note": "два вопроса по подписи гейтов (R17, R05): где хранить ключ и что делать со старыми прогонами"
  },
  "waits": [],
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
    }
  ],
  "reqList": [
    {
      "id": "R01",
      "text": "«A01: save() делает os.replace без повтора»",
      "status": "open"
    },
    {
      "id": "R02",
      "text": "«A02: land() не проверяет зоны и пути; тесты берутся из текста --tests N/0»",
      "status": "open"
    },
    {
      "id": "R03",
      "text": "«A03: git diff --cached --name-only без --no-renames»",
      "status": "open"
    },
    {
      "id": "R04",
      "text": "«A04: риск тикета считается только по словарю слов»",
      "status": "open"
    },
    {
      "id": "R05",
      "text": "«A05: гард защищает от промахов оркестратора, не от исполнителя»",
      "status": "open"
    },
    {
      "id": "R06",
      "text": "«A06: запрет премиум-моделей по префиксу строки»",
      "status": "open"
    },
    {
      "id": "R07",
      "text": "«A07: четыре разборщика state.js с разной терпимостью»",
      "status": "open"
    },
    {
      "id": "R08",
      "text": "«A08: init --force теряет журнал»",
      "status": "open"
    },
    {
      "id": "R09",
      "text": "«A09: classify смотрит только первые 12 000 символов»",
      "status": "open"
    },
    {
      "id": "R10",
      "text": "«A10: trusted-раннер не использует OwnedJob»",
      "status": "open"
    },
    {
      "id": "R11",
      "text": "«A11: версии не сходятся»",
      "status": "open"
    },
    {
      "id": "R12",
      "text": "«A12: доки велят py -3.13 … и controller.py, а allowed-tools пропускает только py -3 .autopilot/ap.py »",
      "status": "open"
    },
    {
      "id": "R13",
      "text": "«A13: в таблице и скоринге нет tier critical»",
      "status": "open"
    },
    {
      "id": "R14",
      "text": "«A14: бэкап HTML со снимком state.js в общем tempdir»",
      "status": "open"
    },
    {
      "id": "R15",
      "text": "«A15: compileall только skills/autopilot/tools и tests»",
      "status": "open"
    },
    {
      "id": "R16",
      "text": "«I01: общий модуль чтения/записи state.js (BOM, префикс, повтор replace) — закрывает A01 и A07 разом»",
      "status": "open"
    },
    {
      "id": "R17",
      "text": "«I02: подписанные квитанции гейтов, ключ вне .autopilot — иначе правка state.js/attestations.jsonl проходит сверку (A05)»",
      "status": "open"
    },
    {
      "id": "R18",
      "text": "«I03: точный allowlist моделей в роутере вместо префиксов + тесты на Bedrock-ID и claude-3-opus (A06)»",
      "status": "open"
    }
  ],
  "gates": {},
  "result": null,
  "skillVersion": "2.6.0"
}
