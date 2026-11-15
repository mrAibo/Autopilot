window.STATE =
{
  "version": 2,
  "slug": "dashboard-token-fixes",
  "dir": "2026-11-15-dashboard-token-fixes--wip",
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
  "baseCommit": null,
  "startedAt": "2026-11-15T20:36:48+01:00",
  "updatedAt": "2026-11-15T20:52:31+01:00",
  "finishedAt": null,
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
      "status": "active",
      "segments": [
        {
          "startedAt": "2026-11-15T20:47:02+01:00",
          "finishedAt": null
        }
      ],
      "startedAt": "2026-11-15T20:47:02+01:00"
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
    "total": 7,
    "done": 0,
    "inTicket": 6,
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
      "status": "pending",
      "retries": 0,
      "repairs": 0,
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
    "found": 6,
    "fixed": 2,
    "deferred": 2,
    "items": [
      "компактность досок, панели таска и «нужен твой ответ» — вне рамок: выбрано A+B",
      "выбор моделей ролей — вне рамок: R07 про маршрут таска"
    ]
  },
  "concerns": [],
  "blockingFindings": [],
  "blind": null,
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
    "2026-11-15T20:52:31+01:00"
  ],
  "rev": 17,
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
    }
  ],
  "reqList": [
    {
      "id": "R01",
      "text": "«По второму пункту – да, надо доделать» — dashboard.html отдаётся без токена и несёт снимок состояния",
      "status": "in-ticket"
    },
    {
      "id": "R02",
      "text": "«По второму пункту – да, надо доделать» — адрес с ?t= печатается при каждой команде ap.py",
      "status": "in-ticket"
    },
    {
      "id": "R03",
      "text": "«По второму пункту – да, надо доделать» — ключ gate.key создаётся не атомарно",
      "status": "in-ticket"
    },
    {
      "id": "R04",
      "text": "«По второму пункту – да, надо доделать» — противоречие в спеке: R24 «снимает только пользователь» и finish --by-user снимает открытые строки цитатой",
      "status": "in-ticket"
    },
    {
      "id": "R05",
      "text": "«Под первым пунктом я бы хотел что-то более компактное, но в принципе так тоже пойдет»",
      "status": "in-ticket"
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
      "status": "in-ticket"
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
      "ok": false,
      "at": "2026-11-15T20:47:00+01:00",
      "found": 6,
      "fixed": 2,
      "deferred": 2
    },
    "G3": {
      "ok": true,
      "at": "2026-11-15T20:52:22+01:00",
      "problems": 0
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
  "planValidationDigest": "01b19cefcb29b7eeeb6401674458ea147c3b214e811dc2be361c1ec08a5e824d"
}
