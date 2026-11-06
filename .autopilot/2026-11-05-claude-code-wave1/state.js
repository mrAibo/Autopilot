window.STATE =
{
  "version": 2,
  "slug": "claude-code-wave1",
  "dir": "2026-11-05-claude-code-wave1",
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
  "baseCommit": "0c4809b",
  "startedAt": "2026-11-05T18:34:27+01:00",
  "updatedAt": "2026-11-05T21:34:44+01:00",
  "finishedAt": "2026-11-05T21:34:44+01:00",
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
      "finishedAt": "2026-11-05T21:34:42+01:00"
    },
    {
      "id": "plan",
      "status": "done",
      "startedAt": "2026-11-05T18:39:22+01:00",
      "finishedAt": "2026-11-05T18:39:44+01:00"
    },
    {
      "id": "build",
      "status": "done",
      "startedAt": "2026-11-05T18:41:10+01:00",
      "finishedAt": "2026-11-05T19:01:30+01:00"
    },
    {
      "id": "review",
      "status": "done",
      "startedAt": "2026-11-05T19:01:30+01:00",
      "finishedAt": "2026-11-05T21:25:56+01:00"
    },
    {
      "id": "final",
      "status": "done",
      "startedAt": "2026-11-05T21:25:56+01:00",
      "finishedAt": "2026-11-05T21:34:44+01:00"
    }
  ],
  "requirements": {
    "total": 15,
    "done": 14,
    "inTicket": 0,
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
      "status": "done",
      "startedAt": "2026-11-05T18:41:24+01:00",
      "finishedAt": "2026-11-05T19:01:26+01:00",
      "retries": 0,
      "repairs": 0,
      "tests": {
        "passed": 622,
        "failed": 0
      },
      "commit": "4488460",
      "placeholders": [],
      "routing": {
        "provider": "anthropic",
        "model": "sonnet",
        "effort": "medium",
        "effortEnforced": true,
        "score": 30,
        "reason": "score=30; profile=balanced; high-risk=False",
        "verified": true,
        "agentType": "autopilot-executor-01-wave1-process-fixes",
        "agentFile": ".claude/agents/autopilot-executor-01-wave1-process-fixes.md",
        "profileSha": "e92e18eb20754c5389dafc30a2c4e29bd0ddd1e1fe371c7629d82abf553ac927",
        "sig": "4bbc3800a4d2d92db791670dd443172408509058b5209a2fea1d1faf23e28564"
      },
      "plannedRouting": {
        "ticket": "01",
        "provider": "anthropic",
        "model": "sonnet",
        "effort": "medium",
        "effortEnforced": true,
        "profile": "balanced",
        "score": 30,
        "factors": {
          "algorithm": 5,
          "coupling": 15,
          "uncertainty": 0,
          "context": 5,
          "testing": 5,
          "risk": 0
        },
        "reason": "score=30; profile=balanced; high-risk=False",
        "requiresReview": false,
        "status": "ready",
        "fingerprint": "f4914df0d8a7bd68d024950f1413d24e31c882d71aa076756de3ad162ca3cf17",
        "hostExecutionVerified": false,
        "applied": true
      },
      "attestation": {
        "model": "claude-sonnet-5-5",
        "effort": "medium",
        "lines": 82
      }
    },
    {
      "id": "F1",
      "title": "Хук git: разделители только вне кавычек",
      "requirements": [
        "R02a"
      ],
      "blockedBy": [],
      "wave": 2,
      "zone": [
        "skills/autopilot/tools/claude_agent_guard.py",
        "tests/test_wave1.py"
      ],
      "review": "да — ремонт ветки",
      "model": "сильная",
      "fingerprint": "8c9063a6b97cd70dab769a4322fb2405d7a36ce8d06c3e5d8ee3bbbe53d45d88",
      "status": "done",
      "startedAt": "2026-11-05T19:07:28+01:00",
      "finishedAt": "2026-11-05T21:26:02+01:00",
      "retries": 0,
      "repairs": 2,
      "repairFindings": [
        "split_unquoted: апостроф в #-комментарии не открывает кавычку; git stash на отдельной строке после комментария с апострофами должен отклоняться",
        "split_unquoted: # начинает комментарий только если перед ним нет экранированной пары; echo a\\ #b; git stash должен отклоняться"
      ],
      "tests": {
        "passed": 622,
        "failed": 0
      },
      "commit": "e858739",
      "placeholders": [],
      "routing": {
        "agentType": "autopilot-executor-repair-2026-11-05-claude-code-wave1",
        "agentFile": ".claude/agents/autopilot-executor-repair-2026-11-05-claude-code-wave1.md",
        "model": "sonnet",
        "effort": "high",
        "effortEnforced": true,
        "profileSha": "a69ecdba508d7a66a615237f5ba60d5f018b4f22750a0685bd5251a095ee0f8c",
        "provider": "anthropic",
        "reason": "ремонт ветки: хук git и кавычки",
        "verified": true,
        "sig": "c2a71512ceff385a1739a250bafbb0d8571c1703ce0e7d9b57c0a163b1293570"
      },
      "attestation": {
        "model": "claude-sonnet-5-5",
        "effort": "high",
        "lines": 31
      },
      "attestFrom": 1751
    }
  ],
  "tests": {
    "passed": 622,
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
    "found": 3,
    "fixed": 0,
    "deferred": 3,
    "items": [
      "Бриф §5: живое подтверждение записей changelog на версии 2.1.302 и на последней — не покрыто, нужен запуск Claude Code пользователем",
      "R04b: вызовы советника в attestations.jsonl — открытый вопрос, итога нет, записан с процедурой проверки",
      "R06: перечень известных проблем лежит в notes.md и коде, в спецификации только ссылка"
    ]
  },
  "concerns": [
    "R01b изменил поведение: сданный таск больше не сбрасывается молча; два старых теста в tests/test_ap.py поправлены"
  ],
  "blockingFindings": [
    {
      "id": "B01",
      "text": "split_unquoted: апостроф в #-комментарии не открывает кавычку; git stash на отдельной строке после комментария с апострофами должен отклоняться",
      "ticket": "F1",
      "openedAt": "2026-11-05T19:19:56+01:00",
      "status": "resolved",
      "openedCommit": "aebd36b",
      "resolvedAt": "2026-11-05T21:25:55+01:00",
      "resolutionCommit": "e858739",
      "resolutionTests": {
        "passed": 622,
        "failed": 0
      },
      "review": "Независимый ревьюер перепроверил условие и подтвердил исправление"
    },
    {
      "id": "B02",
      "text": "split_unquoted: # начинает комментарий только если перед ним нет экранированной пары; echo a\\ #b; git stash должен отклоняться",
      "ticket": "F1",
      "openedAt": "2026-11-05T21:14:34+01:00",
      "status": "resolved",
      "openedCommit": "ca67cd0",
      "resolvedAt": "2026-11-05T21:26:01+01:00",
      "resolutionCommit": "e858739",
      "resolutionTests": {
        "passed": 622,
        "failed": 0
      },
      "review": "Независимый ревьюер перепроверил условие и подтвердил исправление"
    }
  ],
  "blind": {
    "checked": 14,
    "matched": 14,
    "mismatches": []
  },
  "beats": [
    "2026-11-05T18:34:27+01:00",
    "2026-11-05T18:34:34+01:00",
    "2026-11-05T18:35:00+01:00",
    "2026-11-05T18:35:01+01:00",
    "2026-11-05T18:38:44+01:00",
    "2026-11-05T18:39:22+01:00",
    "2026-11-05T18:39:23+01:00",
    "2026-11-05T18:39:24+01:00",
    "2026-11-05T18:39:38+01:00",
    "2026-11-05T18:39:44+01:00",
    "2026-11-05T18:39:52+01:00",
    "2026-11-05T18:41:05+01:00",
    "2026-11-05T18:41:10+01:00",
    "2026-11-05T18:41:24+01:00",
    "2026-11-05T19:01:26+01:00",
    "2026-11-05T19:01:30+01:00",
    "2026-11-05T19:01:38+01:00",
    "2026-11-05T19:07:15+01:00",
    "2026-11-05T19:07:16+01:00",
    "2026-11-05T19:07:17+01:00",
    "2026-11-05T19:07:18+01:00",
    "2026-11-05T19:07:19+01:00",
    "2026-11-05T19:07:20+01:00",
    "2026-11-05T19:07:28+01:00",
    "2026-11-05T19:18:44+01:00",
    "2026-11-05T19:18:45+01:00",
    "2026-11-05T19:19:56+01:00",
    "2026-11-05T19:31:59+01:00",
    "2026-11-05T21:14:34+01:00",
    "2026-11-05T21:14:37+01:00",
    "2026-11-05T21:25:55+01:00",
    "2026-11-05T21:25:56+01:00",
    "2026-11-05T21:26:01+01:00",
    "2026-11-05T21:26:02+01:00",
    "2026-11-05T21:32:26+01:00",
    "2026-11-05T21:32:27+01:00",
    "2026-11-05T21:34:13+01:00",
    "2026-11-05T21:34:19+01:00",
    "2026-11-05T21:34:42+01:00",
    "2026-11-05T21:34:43+01:00",
    "2026-11-05T21:34:44+01:00"
  ],
  "rev": 53,
  "waiting": null,
  "waits": [
    {
      "kind": "stop",
      "from": "2026-11-05T18:39:52+01:00",
      "to": "2026-11-05T18:41:05+01:00"
    },
    {
      "kind": "stop",
      "from": "2026-11-05T19:31:59+01:00",
      "to": "2026-11-05T21:14:34+01:00"
    }
  ],
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
    },
    {
      "t": "2026-11-05T18:39:44+01:00",
      "k": "stage",
      "id": "plan",
      "act": "done"
    },
    {
      "t": "2026-11-05T18:39:44+01:00",
      "k": "plan-models",
      "provider": "anthropic",
      "applied": true,
      "tickets": 1,
      "blocked": 0
    },
    {
      "t": "2026-11-05T18:39:52+01:00",
      "k": "ask",
      "kind": "stop",
      "note": "новый чат: агенты зарегистрированы; перед стартом таска — независимая сверка G2 разведчиком"
    },
    {
      "t": "2026-11-05T18:41:05+01:00",
      "k": "answered",
      "kind": "stop"
    },
    {
      "t": "2026-11-05T18:41:05+01:00",
      "k": "gate",
      "g": "G3",
      "ok": true,
      "problems": 0
    },
    {
      "t": "2026-11-05T18:41:10+01:00",
      "k": "stage",
      "id": "build",
      "act": "start"
    },
    {
      "t": "2026-11-05T18:41:24+01:00",
      "k": "ticket",
      "ids": [
        "01"
      ],
      "act": "start"
    },
    {
      "t": "2026-11-05T19:01:26+01:00",
      "k": "ticket",
      "ids": [
        "01"
      ],
      "act": "done",
      "tests": {
        "passed": 622,
        "failed": 0
      }
    },
    {
      "t": "2026-11-05T19:01:30+01:00",
      "k": "stage",
      "id": "review",
      "act": "start"
    },
    {
      "t": "2026-11-05T19:01:38+01:00",
      "k": "add",
      "key": "concerns",
      "n": 1
    },
    {
      "t": "2026-11-05T19:07:15+01:00",
      "k": "add",
      "key": "report",
      "n": 2
    },
    {
      "t": "2026-11-05T19:07:16+01:00",
      "k": "add",
      "key": "report",
      "n": 1
    },
    {
      "t": "2026-11-05T19:07:17+01:00",
      "k": "add",
      "key": "report",
      "n": 1
    },
    {
      "t": "2026-11-05T19:07:17+01:00",
      "k": "add",
      "key": "report",
      "n": 1
    },
    {
      "t": "2026-11-05T19:07:18+01:00",
      "k": "add",
      "key": "report",
      "n": 1
    },
    {
      "t": "2026-11-05T19:07:18+01:00",
      "k": "add",
      "key": "report",
      "n": 1
    },
    {
      "t": "2026-11-05T19:07:19+01:00",
      "k": "add",
      "key": "report",
      "n": 1
    },
    {
      "t": "2026-11-05T19:07:19+01:00",
      "k": "add",
      "key": "report",
      "n": 1
    },
    {
      "t": "2026-11-05T19:07:20+01:00",
      "k": "add",
      "key": "report",
      "n": 1
    },
    {
      "t": "2026-11-05T19:07:20+01:00",
      "k": "tickets",
      "n": 2
    },
    {
      "t": "2026-11-05T19:07:28+01:00",
      "k": "ticket",
      "ids": [
        "F1"
      ],
      "act": "route"
    },
    {
      "t": "2026-11-05T19:07:28+01:00",
      "k": "ticket",
      "ids": [
        "F1"
      ],
      "act": "start"
    },
    {
      "t": "2026-11-05T19:18:44+01:00",
      "k": "ticket",
      "ids": [
        "F1"
      ],
      "act": "done",
      "tests": {
        "passed": 622,
        "failed": 0
      }
    },
    {
      "t": "2026-11-05T19:18:45+01:00",
      "k": "ticket",
      "ids": [
        "F1"
      ],
      "act": "review"
    },
    {
      "t": "2026-11-05T19:19:56+01:00",
      "k": "blocker",
      "id": "B01",
      "act": "open",
      "ticket": "F1"
    },
    {
      "t": "2026-11-05T19:19:56+01:00",
      "k": "ticket",
      "ids": [
        "F1"
      ],
      "act": "repair",
      "note": "split_unquoted: апостроф в #-комментарии не открывает кавычку; git stash на отдельной строке после комментария с апострофами должен отклоняться"
    },
    {
      "t": "2026-11-05T19:31:59+01:00",
      "k": "ask",
      "kind": "stop"
    },
    {
      "t": "2026-11-05T21:14:34+01:00",
      "k": "answered",
      "kind": "stop"
    },
    {
      "t": "2026-11-05T21:14:34+01:00",
      "k": "blocker",
      "id": "B02",
      "act": "open",
      "ticket": "F1"
    },
    {
      "t": "2026-11-05T21:14:34+01:00",
      "k": "ticket",
      "ids": [
        "F1"
      ],
      "act": "repair",
      "note": "split_unquoted: # начинает комментарий только если перед ним нет экранированной пары; echo a\\ #b; git stash должен отклоняться"
    },
    {
      "t": "2026-11-05T21:25:55+01:00",
      "k": "blocker",
      "id": "B01",
      "act": "resolve",
      "ticket": "F1"
    },
    {
      "t": "2026-11-05T21:25:56+01:00",
      "k": "stage",
      "id": "final",
      "act": "start"
    },
    {
      "t": "2026-11-05T21:26:01+01:00",
      "k": "blocker",
      "id": "B02",
      "act": "resolve",
      "ticket": "F1"
    },
    {
      "t": "2026-11-05T21:26:02+01:00",
      "k": "ticket",
      "ids": [
        "F1"
      ],
      "act": "done",
      "tests": {
        "passed": 622,
        "failed": 0
      }
    },
    {
      "t": "2026-11-05T21:32:26+01:00",
      "k": "gate",
      "g": "G4",
      "ok": true,
      "checked": 14,
      "matched": 14
    },
    {
      "t": "2026-11-05T21:32:27+01:00",
      "k": "tests",
      "passed": 622,
      "failed": 0
    },
    {
      "t": "2026-11-05T21:34:13+01:00",
      "k": "gate",
      "g": "G2",
      "ok": true,
      "found": 3,
      "fixed": 0,
      "deferred": 3
    },
    {
      "t": "2026-11-05T21:34:19+01:00",
      "k": "gate",
      "g": "G3",
      "ok": true,
      "problems": 0
    },
    {
      "t": "2026-11-05T21:34:19+01:00",
      "k": "gate",
      "g": "G1",
      "ok": false,
      "reason": "plan-changed"
    },
    {
      "t": "2026-11-05T21:34:19+01:00",
      "k": "gate",
      "g": "G2",
      "ok": false,
      "reason": "plan-changed"
    },
    {
      "t": "2026-11-05T21:34:19+01:00",
      "k": "gate",
      "g": "G4",
      "ok": false,
      "reason": "plan-changed"
    },
    {
      "t": "2026-11-05T21:34:42+01:00",
      "k": "gate",
      "g": "G1",
      "ok": true,
      "open": 0,
      "total": 15
    },
    {
      "t": "2026-11-05T21:34:42+01:00",
      "k": "stage",
      "id": "spec",
      "act": "done"
    },
    {
      "t": "2026-11-05T21:34:43+01:00",
      "k": "gate",
      "g": "G2",
      "ok": true,
      "found": 3,
      "fixed": 0,
      "deferred": 3
    },
    {
      "t": "2026-11-05T21:34:43+01:00",
      "k": "gate",
      "g": "G4",
      "ok": true,
      "checked": 14,
      "matched": 14
    },
    {
      "t": "2026-11-05T21:34:44+01:00",
      "k": "finish",
      "result": "Волна 1: отпечатки тасков, accept-edit, запрет git stash у исполнителей, проверка путей и версии Claude Code"
    }
  ],
  "reqList": [
    {
      "id": "R01",
      "text": "«Отпечаток считается по нормализованному тексту: LF, без хвостовых пробелов, без BOM.»",
      "status": "done"
    },
    {
      "id": "R01a",
      "text": "«Совпадение с любым из двух (старый или новый) = таск не менялся, отпечаток молча переписывается на новый.»",
      "status": "done"
    },
    {
      "id": "R01b",
      "text": "«Смена смысла у сданного таска не сбрасывает его молча: останов с сообщением и командой ticket NN accept-edit --note \"...\".»",
      "status": "done"
    },
    {
      "id": "R02",
      "text": "«skills/autopilot/prompts/executor.md и профили: запрещены git stash, git reset, git checkout -- <чужие пути>; коммит только git commit --only <файлы зоны>; перед коммитом git diff --cached --stat.»",
      "status": "done"
    },
    {
      "id": "R02a",
      "text": "«claude_agent_guard.py отклоняет git stash в Bash-вызовах субагентов строгого прогона»",
      "status": "done"
    },
    {
      "id": "R03",
      "text": "«phases/4-plan.md и промпты: образцы — через <scratchpad> и <repo>.»",
      "status": "done"
    },
    {
      "id": "R03a",
      "text": "«Проверка при публикации тасков и спецификации (ap.py): абсолютный путь пользователя (шаблоны из tests/test_no_machine_data.py) = отказ с указанием файла и строки.»",
      "status": "done"
    },
    {
      "id": "R04",
      "text": "«Описать в docs/autopilot/claude-code.md и model-routing.md: советник — серверный инструмент, субагенты наследуют настройку advisorModel, is_allowed_subagent_model его не видит.»",
      "status": "done"
    },
    {
      "id": "R04a",
      "text": "«phases/0-preflight.md: в строгом прогоне предупредить, если advisorModel настроен; предложить CLAUDE_CODE_DISABLE_ADVISOR_TOOL=1 на время сборки.»",
      "status": "done"
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
      "status": "done"
    },
    {
      "id": "R05a",
      "text": "«в сообщение пользователю — время сброса лимита (5-часовое окно и недельное у плана); для Ultra 5-часового лимита нет.»",
      "status": "done"
    },
    {
      "id": "R06",
      "text": "«0-preflight.md: claude --version до init, разбор строки версии, тест на разбор.»",
      "status": "done"
    },
    {
      "id": "R06a",
      "text": "«Жёсткий минимум остаётся 2.1.295 (на нём стоят onFailure и effort на вызов). Версии ниже 2.1.311 — предупреждение с перечнем известных проблем, но не отказ»",
      "status": "done"
    },
    {
      "id": "R00i",
      "text": "«каждое изменение сопровождается тестом и записью в CHANGELOG.md» (§5; Тесты по каждому R)",
      "status": "done"
    }
  ],
  "gates": {
    "G1": {
      "ok": true,
      "at": "2026-11-05T21:34:42+01:00",
      "open": 0,
      "total": 15
    },
    "G3": {
      "ok": true,
      "at": "2026-11-05T21:34:19+01:00",
      "problems": 0
    },
    "G4": {
      "ok": true,
      "at": "2026-11-05T21:34:43+01:00",
      "checked": 14,
      "matched": 14
    },
    "G2": {
      "ok": true,
      "at": "2026-11-05T21:34:43+01:00",
      "found": 3,
      "fixed": 0,
      "deferred": 3
    }
  },
  "result": "Волна 1: отпечатки тасков, accept-edit, запрет git stash у исполнителей, проверка путей и версии Claude Code",
  "gateMark": "1f6627aa79e3665cfe2a92f8893893893c53a417cf4a2aeea74441ed9498b441",
  "skillVersion": "2.7.0",
  "planContractDigest": "657ed42703ba661e31d88406e3846d7c28a028d1888b215176f0a3954fa07094",
  "planValidationDigest": "c7c1cdbe31e38026e92c8320519cbb8449d8b0063305f53620d112ced210bb0c",
  "roleAgents": {
    "reviewer": {
      "agentType": "autopilot-reviewer-2026-11-05-claude-code-wave1",
      "agentFile": ".claude/agents/autopilot-reviewer-2026-11-05-claude-code-wave1.md",
      "model": "sonnet",
      "effort": "high",
      "effortEnforced": true,
      "profileSha": "d55dad410f094412295c928672583c620f5a2c5761e1db6fb6c25bc7ec2723d2"
    },
    "acceptance": {
      "agentType": "autopilot-acceptance-2026-11-05-claude-code-wave1",
      "agentFile": ".claude/agents/autopilot-acceptance-2026-11-05-claude-code-wave1.md",
      "model": "sonnet",
      "effort": "medium",
      "effortEnforced": true,
      "profileSha": "100b6e068a23656cbae5fe621182e44fdd277b7046f9856fe797280c8d03e58b"
    },
    "explorer": {
      "agentType": "autopilot-explorer-2026-11-05-claude-code-wave1",
      "agentFile": ".claude/agents/autopilot-explorer-2026-11-05-claude-code-wave1.md",
      "model": "haiku",
      "effort": "low",
      "effortEnforced": true,
      "profileSha": "04e94c3c80eed0aa66a2e09415a8d23042f969ec0b6673fe05334ceebc302003"
    }
  },
  "repairAgent": {
    "agentType": "autopilot-executor-repair-2026-11-05-claude-code-wave1",
    "agentFile": ".claude/agents/autopilot-executor-repair-2026-11-05-claude-code-wave1.md",
    "model": "sonnet",
    "effort": "high",
    "effortEnforced": true,
    "profileSha": "a69ecdba508d7a66a615237f5ba60d5f018b4f22750a0685bd5251a095ee0f8c"
  },
  "report": [
    "Хук git пропускает git.exe stash, /usr/bin/git stash, bash -c \"git stash\"; в предел хука (docs/autopilot/claude-code.md) эти формы не названы",
    "claude-code-wave1",
    "git restore ., git checkout . и git clean -fd хук пропускает, список запретов их не содержит; расширять ли — решает заказчик",
    "Сданный таск с неосвобождённым worktree после accept-edit проходит публикацию; прежний отказ по worktree срабатывал на любой статус (ap.py:454)",
    "Для codex_dispatch.py нет теста на новый отпечаток и файл с CRLF",
    "Тест test_changed_ticket_resets_previous_acceptance называется наоборот; проверки манифеста при сбросе не сданного таска нет",
    "claude-version печатает весь список известных проблем даже для версии, где часть уже исправлена",
    "parse_claude_version не разбирает строку с точкой после версии",
    "claude-version не находит claude.cmd (npm на Windows), проверка молча пропускается",
    "Хук Bash с onFailure block: сбой хука блокирует все Bash-команды проекта, в docs это не названо"
  ]
}
