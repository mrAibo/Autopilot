window.STATE =
{
  "version": 2,
  "slug": "claude-code-wave1",
  "dir": "2026-11-05-claude-code-wave1--wip",
  "title": "Правки по итогам сборки и Claude Code: волна 1 (R01–R06)",
  "mode": "full",
  "depth": "strict",
  "tier": "T0",
  "strictRouting": true,
  "gateSigned": true,
  "sequentialHost": false,
  "isolateTickets": false,
  "briefFile": "2026-11-05-brief.md",
  "memoryFile": "AGENTS.md",
  "memoryOwner": "autopilot",
  "skillDir": "C:/Users/crown/Downloads/Projects/Autopilot/skills/autopilot",
  "baseCommit": null,
  "startedAt": "2026-11-05T18:34:27+01:00",
  "updatedAt": "2026-11-05T18:39:24+01:00",
  "finishedAt": null,
  "stages": [
    {
      "id": "preflight",
      "status": "done",
      "startedAt": "2026-11-05T18:34:27+01:00",
      "finishedAt": "2026-11-05T18:34:34+01:00"
    },
    {
      "id": "manifest",
      "status": "done",
      "startedAt": "2026-11-05T18:34:34+01:00",
      "finishedAt": "2026-11-05T18:35:01+01:00"
    },
    {
      "id": "briefing",
      "status": "skipped",
      "startedAt": "2026-11-05T18:35:01+01:00",
      "finishedAt": "2026-11-05T18:35:01+01:00",
      "note": "full strict: бриф с критериями приёмки, открытых вопросов нет"
    },
    {
      "id": "spec",
      "status": "done",
      "startedAt": "2026-11-05T18:35:01+01:00",
      "finishedAt": "2026-11-05T18:39:22+01:00"
    },
    {
      "id": "plan",
      "status": "active",
      "startedAt": "2026-11-05T18:39:22+01:00"
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
    "total": 15,
    "done": 0,
    "inTicket": 14,
    "inSpec": 0,
    "placeholder": 0,
    "deferred": 1,
    "dropped": 0
  },
  "tickets": [
    {
      "id": "01",
      "title": "Волна 1: правки процесса и проверка версии Claude Code",
      "requirements": [
        "R01",
        "R01a",
        "R01b",
        "R02",
        "R02a",
        "R03",
        "R03a",
        "R04",
        "R04a",
        "R05",
        "R05a",
        "R06",
        "R06a",
        "R00i"
      ],
      "blockedBy": [],
      "wave": 1,
      "zone": [
        "skills/autopilot/",
        "tests/",
        "docs/autopilot/",
        "CHANGELOG.md"
      ],
      "review": "нет",
      "model": "обычная",
      "fingerprint": "f4914df0d8a7bd68d024950f1413d24e31c882d71aa076756de3ad162ca3cf17",
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
  "coverage": null,
  "concerns": [],
  "blockingFindings": [],
  "blind": null,
  "beats": [
    "2026-11-05T18:34:27+01:00",
    "2026-11-05T18:34:34+01:00",
    "2026-11-05T18:35:00+01:00",
    "2026-11-05T18:35:01+01:00",
    "2026-11-05T18:38:44+01:00",
    "2026-11-05T18:39:22+01:00",
    "2026-11-05T18:39:23+01:00",
    "2026-11-05T18:39:24+01:00"
  ],
  "rev": 11,
  "waiting": null,
  "waits": [],
  "log": [
    {
      "t": "2026-11-05T18:34:27+01:00",
      "k": "init"
    },
    {
      "t": "2026-11-05T18:34:34+01:00",
      "k": "stage",
      "id": "manifest",
      "act": "start"
    },
    {
      "t": "2026-11-05T18:35:01+01:00",
      "k": "stage",
      "id": "briefing",
      "act": "skip",
      "note": "full strict: бриф с критериями приёмки, открытых вопросов нет"
    },
    {
      "t": "2026-11-05T18:35:01+01:00",
      "k": "gate",
      "g": "G1",
      "ok": false,
      "open": 15,
      "total": 15
    },
    {
      "t": "2026-11-05T18:35:01+01:00",
      "k": "stage",
      "id": "spec",
      "act": "start"
    },
    {
      "t": "2026-11-05T18:38:44+01:00",
      "k": "gate",
      "g": "G1",
      "ok": true,
      "open": 0,
      "total": 15
    },
    {
      "t": "2026-11-05T18:38:44+01:00",
      "k": "stage",
      "id": "spec",
      "act": "start"
    },
    {
      "t": "2026-11-05T18:39:22+01:00",
      "k": "stage",
      "id": "plan",
      "act": "start"
    },
    {
      "t": "2026-11-05T18:39:23+01:00",
      "k": "tier",
      "v": "T0"
    },
    {
      "t": "2026-11-05T18:39:24+01:00",
      "k": "tickets",
      "n": 1
    },
    {
      "t": "2026-11-05T18:39:24+01:00",
      "k": "gate",
      "g": "G3",
      "ok": true,
      "problems": 0
    }
  ],
  "reqList": [
    {
      "id": "R01",
      "text": "«Отпечаток считается по нормализованному тексту: LF, без хвостовых пробелов, без BOM.»",
      "status": "in-ticket"
    },
    {
      "id": "R01a",
      "text": "«Совпадение с любым из двух (старый или новый) = таск не менялся, отпечаток молча переписывается на новый.»",
      "status": "in-ticket"
    },
    {
      "id": "R01b",
      "text": "«Смена смысла у сданного таска не сбрасывает его молча: останов с сообщением и командой ticket NN accept-edit --note \"...\".»",
      "status": "in-ticket"
    },
    {
      "id": "R02",
      "text": "«skills/autopilot/prompts/executor.md и профили: запрещены git stash, git reset, git checkout -- <чужие пути>; коммит только git commit --only <файлы зоны>; перед коммитом git diff --cached --stat.»",
      "status": "in-ticket"
    },
    {
      "id": "R02a",
      "text": "«claude_agent_guard.py отклоняет git stash в Bash-вызовах субагентов строгого прогона»",
      "status": "in-ticket"
    },
    {
      "id": "R03",
      "text": "«phases/4-plan.md и промпты: образцы — через <scratchpad> и <repo>.»",
      "status": "in-ticket"
    },
    {
      "id": "R03a",
      "text": "«Проверка при публикации тасков и спецификации (ap.py): абсолютный путь пользователя (шаблоны из tests/test_no_machine_data.py) = отказ с указанием файла и строки.»",
      "status": "in-ticket"
    },
    {
      "id": "R04",
      "text": "«Описать в docs/autopilot/claude-code.md и model-routing.md: советник — серверный инструмент, субагенты наследуют настройку advisorModel, is_allowed_subagent_model его не видит.»",
      "status": "in-ticket"
    },
    {
      "id": "R04a",
      "text": "«phases/0-preflight.md: в строгом прогоне предупредить, если advisorModel настроен; предложить CLAUDE_CODE_DISABLE_ADVISOR_TOOL=1 на время сборки.»",
      "status": "in-ticket"
    },
    {
      "id": "R04b",
      "text": "«Открытый вопрос (решить живой проверкой, записать итог): видны ли вызовы советника в attestations.jsonl (models_used).»",
      "status": "deferred",
      "why": "нужна живая проверка с включённым советником, в этом сеансе её не сделать; открытый вопрос с процедурой — в claude-code.md"
    },
    {
      "id": "R05",
      "text": "«исполнитель упал на лимите → git status и git diff его зоны → SendMessage тому же агенту «продолжи», нового не заводить; пункт про незакоммиченные правки зоны.»",
      "status": "in-ticket"
    },
    {
      "id": "R05a",
      "text": "«в сообщение пользователю — время сброса лимита (5-часовое окно и недельное у плана); для Ultra 5-часового лимита нет.»",
      "status": "in-ticket"
    },
    {
      "id": "R06",
      "text": "«0-preflight.md: claude --version до init, разбор строки версии, тест на разбор.»",
      "status": "in-ticket"
    },
    {
      "id": "R06a",
      "text": "«Жёсткий минимум остаётся 2.1.295 (на нём стоят onFailure и effort на вызов). Версии ниже 2.1.311 — предупреждение с перечнем известных проблем, но не отказ»",
      "status": "in-ticket"
    },
    {
      "id": "R00i",
      "text": "«каждое изменение сопровождается тестом и записью в CHANGELOG.md» (§5; Тесты по каждому R)",
      "status": "in-ticket"
    }
  ],
  "gates": {
    "G1": {
      "ok": true,
      "at": "2026-11-05T18:38:44+01:00",
      "open": 0,
      "total": 15
    },
    "G3": {
      "ok": true,
      "at": "2026-11-05T18:39:24+01:00",
      "problems": 0
    }
  },
  "result": null,
  "gateMark": "1f6627aa79e3665cfe2a92f8893893893c53a417cf4a2aeea74441ed9498b441",
  "skillVersion": "2.7.0",
  "planContractDigest": "f1ae9c9bcf4c17b2561823e9315df6154f2369b1a082550ceec0ff177232208e",
  "planValidationDigest": "47c095f66c529cf39c0156acb7cc90ac9d72a01c01cc1716544373a13c08dcd3"
}
