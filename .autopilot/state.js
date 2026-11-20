window.STATE =
{
  "schemaVersion": 1,
  "version": 2,
  "slug": "close-known-bugs",
  "dir": "2026-11-20-close-known-bugs",
  "title": "Закрыть известные баги: plan-fact, land_check, blocker confirm, redproof",
  "mode": "semi",
  "depth": "normal",
  "kind": "task",
  "tier": "T1",
  "strictRouting": false,
  "gateSigned": false,
  "sequentialHost": false,
  "spendLedger": [
    {
      "t": "2026-11-20T09:11:51+01:00",
      "run": "2026-11-20-close-known-bugs",
      "source": "orchestrator",
      "origin": "claude-transcript",
      "role": "orchestrator",
      "ticket": null,
      "agent": null,
      "agent_type": null,
      "model": "claude-sonnet-5-5",
      "effort": null,
      "turns": 30,
      "input": 68,
      "output": 19823,
      "cache_read": 5496635,
      "cache_write": 60062,
      "tokens": 19891,
      "hit": 99
    },
    {
      "t": "2026-11-20T09:11:51+01:00",
      "run": "2026-11-20-close-known-bugs",
      "source": "subagent",
      "origin": "claude-subagents",
      "role": "reviewer",
      "ticket": null,
      "agent": "a1bcc831987444e96",
      "agent_type": "autopilot-reviewer",
      "model": "claude-haiku-5-5",
      "effort": null,
      "turns": 2,
      "input": 4,
      "output": 4654,
      "cache_read": 14784,
      "cache_write": 26799,
      "tokens": 4658,
      "hit": 36
    },
    {
      "t": "2026-11-20T09:11:51+01:00",
      "run": "2026-11-20-close-known-bugs",
      "source": "subagent",
      "origin": "claude-subagents",
      "role": "reviewer",
      "ticket": null,
      "agent": "aa9f56edde44bc670",
      "agent_type": "autopilot-reviewer",
      "model": "claude-sonnet-5-5",
      "effort": null,
      "turns": 4,
      "input": 8,
      "output": 3722,
      "cache_read": 78295,
      "cache_write": 35028,
      "tokens": 3730,
      "hit": 69
    },
    {
      "t": "2026-11-20T09:11:51+01:00",
      "run": "2026-11-20-close-known-bugs",
      "source": "subagent",
      "origin": "claude-subagents",
      "role": "acceptance",
      "ticket": null,
      "agent": "ab35ce0357c9b75aa",
      "agent_type": "autopilot-acceptance",
      "model": "claude-sonnet-5-5",
      "effort": null,
      "turns": 8,
      "input": 16,
      "output": 3314,
      "cache_read": 158769,
      "cache_write": 25703,
      "tokens": 3330,
      "hit": 86
    },
    {
      "t": "2026-11-20T09:11:51+01:00",
      "run": "2026-11-20-close-known-bugs",
      "source": "subagent",
      "origin": "claude-subagents",
      "role": "executor",
      "ticket": "01",
      "agent": "af5211987978b5ae3",
      "agent_type": "autopilot-executor",
      "model": "claude-sonnet-5-5",
      "effort": null,
      "turns": 33,
      "input": 66,
      "output": 22593,
      "cache_read": 1990266,
      "cache_write": 87824,
      "tokens": 22659,
      "hit": 96
    }
  ],
  "isolateTickets": false,
  "briefFile": "2026-11-20-brief.md",
  "memoryFile": "AGENTS.md",
  "memoryOwner": "autopilot",
  "skillDir": "C:/Users/crown/.claude/skills/autopilot",
  "baseCommit": "14c198d",
  "startedAt": "2026-11-20T08:59:40+01:00",
  "updatedAt": "2026-11-20T09:11:50+01:00",
  "finishedAt": "2026-11-20T09:11:51+01:00",
  "stages": [
    {
      "id": "preflight",
      "status": "done",
      "startedAt": "2026-11-20T08:59:40+01:00",
      "segments": [
        {
          "startedAt": "2026-11-20T08:59:40+01:00",
          "finishedAt": "2026-11-20T08:59:46+01:00"
        }
      ],
      "finishedAt": "2026-11-20T08:59:46+01:00"
    },
    {
      "id": "manifest",
      "status": "done",
      "segments": [
        {
          "startedAt": "2026-11-20T08:59:46+01:00",
          "finishedAt": "2026-11-20T08:59:57+01:00"
        }
      ],
      "startedAt": "2026-11-20T08:59:46+01:00",
      "finishedAt": "2026-11-20T08:59:57+01:00"
    },
    {
      "id": "briefing",
      "status": "done",
      "segments": [
        {
          "startedAt": "2026-11-20T08:59:57+01:00",
          "finishedAt": "2026-11-20T09:01:19+01:00"
        }
      ],
      "startedAt": "2026-11-20T08:59:57+01:00",
      "finishedAt": "2026-11-20T09:01:19+01:00"
    },
    {
      "id": "spec",
      "status": "done",
      "segments": [
        {
          "startedAt": "2026-11-20T09:01:19+01:00",
          "finishedAt": "2026-11-20T09:01:35+01:00"
        }
      ],
      "startedAt": "2026-11-20T09:01:19+01:00",
      "finishedAt": "2026-11-20T09:01:35+01:00"
    },
    {
      "id": "plan",
      "status": "done",
      "segments": [
        {
          "startedAt": "2026-11-20T09:01:35+01:00",
          "finishedAt": "2026-11-20T09:01:41+01:00"
        }
      ],
      "startedAt": "2026-11-20T09:01:35+01:00",
      "finishedAt": "2026-11-20T09:01:41+01:00"
    },
    {
      "id": "build",
      "status": "done",
      "segments": [
        {
          "startedAt": "2026-11-20T09:01:41+01:00",
          "finishedAt": "2026-11-20T09:09:47+01:00"
        }
      ],
      "startedAt": "2026-11-20T09:01:41+01:00",
      "finishedAt": "2026-11-20T09:09:47+01:00"
    },
    {
      "id": "review",
      "status": "done",
      "segments": [
        {
          "startedAt": "2026-11-20T09:09:47+01:00",
          "finishedAt": "2026-11-20T09:09:47+01:00"
        }
      ],
      "startedAt": "2026-11-20T09:09:47+01:00",
      "finishedAt": "2026-11-20T09:09:47+01:00"
    },
    {
      "id": "final",
      "status": "done",
      "segments": [
        {
          "startedAt": "2026-11-20T09:09:47+01:00",
          "finishedAt": "2026-11-20T09:11:51+01:00"
        }
      ],
      "startedAt": "2026-11-20T09:09:47+01:00",
      "finishedAt": "2026-11-20T09:11:51+01:00"
    }
  ],
  "requirements": {
    "total": 7,
    "done": 7,
    "inTicket": 0,
    "inSpec": 0,
    "placeholder": 0,
    "deferred": 0,
    "dropped": 0
  },
  "tickets": [
    {
      "id": "01",
      "title": "Закрыть известные баги plan-fact, land_check, blocker confirm, redproof",
      "requirements": [
        "R01",
        "R02",
        "R03",
        "R04",
        "R05",
        "R06",
        "R07"
      ],
      "blockedBy": [],
      "wave": 1,
      "zone": [
        "skills/autopilot/tools/plan_items.py",
        "skills/autopilot/tools/land_check.py",
        "skills/autopilot/tools/ap.py",
        "skills/autopilot/phases/kind-bug.md",
        "tests/",
        "CHANGELOG.md",
        "docs/adr/"
      ],
      "review": "нет",
      "model": "обычная",
      "repro": false,
      "testsEdit": null,
      "fingerprint": "5ba4b744963919b5fd865fe3bdacbaa4154e44d8aa864a5d923950818e2c8d14",
      "status": "done",
      "startedAt": "2026-11-20T09:01:41+01:00",
      "finishedAt": "2026-11-20T09:08:58+01:00",
      "retries": 0,
      "repairs": 0,
      "tests": {
        "passed": 1240,
        "failed": 0
      },
      "commit": "5069947",
      "placeholders": [],
      "startHead": "14c198d230f4bdd48590082c2f1d6fd3c283398b"
    }
  ],
  "tests": {
    "passed": 1245,
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
    "found": 0,
    "fixed": 0,
    "deferred": 0,
    "items": []
  },
  "concerns": [
    "plan_items.py:_proved — ::имя ищется подстрокой, слабая проверка",
    "land_check.py — на git старше 2.22 трейлер Autopilot-Ticket не распознаётся (прежнее поведение)",
    "ap.py:cmd_proof — «cannot import name» ловится в любом месте вывода, возможен ложный отказ redproof"
  ],
  "blockingFindings": [],
  "blind": {
    "checked": 7,
    "matched": 7,
    "mismatches": []
  },
  "beats": [
    "2026-11-20T08:59:40+01:00",
    "2026-11-20T08:59:46+01:00",
    "2026-11-20T08:59:56+01:00",
    "2026-11-20T08:59:57+01:00",
    "2026-11-20T09:01:19+01:00",
    "2026-11-20T09:01:34+01:00",
    "2026-11-20T09:01:35+01:00",
    "2026-11-20T09:01:36+01:00",
    "2026-11-20T09:01:40+01:00",
    "2026-11-20T09:01:41+01:00",
    "2026-11-20T09:07:29+01:00",
    "2026-11-20T09:09:45+01:00",
    "2026-11-20T09:09:47+01:00",
    "2026-11-20T09:11:50+01:00"
  ],
  "rev": 22,
  "waiting": null,
  "waits": [],
  "log": [
    {
      "t": "2026-11-20T08:59:40+01:00",
      "k": "init"
    },
    {
      "t": "2026-11-20T08:59:46+01:00",
      "k": "stage",
      "id": "manifest",
      "act": "start"
    },
    {
      "t": "2026-11-20T08:59:57+01:00",
      "k": "stage",
      "id": "briefing",
      "act": "start"
    },
    {
      "t": "2026-11-20T09:01:19+01:00",
      "k": "gate",
      "g": "G1",
      "ok": true,
      "open": 0,
      "total": 7
    },
    {
      "t": "2026-11-20T09:01:19+01:00",
      "k": "stage",
      "id": "spec",
      "act": "start"
    },
    {
      "t": "2026-11-20T09:01:34+01:00",
      "k": "gate",
      "g": "G2",
      "ok": true,
      "found": 0,
      "fixed": 0,
      "deferred": 0
    },
    {
      "t": "2026-11-20T09:01:35+01:00",
      "k": "tier",
      "v": "T1"
    },
    {
      "t": "2026-11-20T09:01:35+01:00",
      "k": "stage",
      "id": "plan",
      "act": "start"
    },
    {
      "t": "2026-11-20T09:01:35+01:00",
      "k": "tickets",
      "n": 1
    },
    {
      "t": "2026-11-20T09:01:36+01:00",
      "k": "gate",
      "g": "G3",
      "ok": true,
      "problems": 0
    },
    {
      "t": "2026-11-20T09:01:41+01:00",
      "k": "stage",
      "id": "build",
      "act": "start"
    },
    {
      "t": "2026-11-20T09:01:41+01:00",
      "k": "ticket",
      "ids": [
        "01"
      ],
      "act": "start"
    },
    {
      "t": "2026-11-20T09:07:29+01:00",
      "k": "ticket",
      "ids": [
        "01"
      ],
      "act": "done",
      "tests": {
        "passed": 1240,
        "failed": 0
      }
    },
    {
      "t": "2026-11-20T09:09:45+01:00",
      "k": "add",
      "key": "concerns",
      "n": 3
    },
    {
      "t": "2026-11-20T09:09:47+01:00",
      "k": "stage",
      "id": "review",
      "act": "start"
    },
    {
      "t": "2026-11-20T09:09:47+01:00",
      "k": "stage",
      "id": "final",
      "act": "start"
    },
    {
      "t": "2026-11-20T09:11:50+01:00",
      "k": "gate",
      "g": "G4",
      "ok": true,
      "checked": 7,
      "matched": 7
    },
    {
      "t": "2026-11-20T09:11:50+01:00",
      "k": "tests",
      "passed": 1245,
      "failed": 0
    },
    {
      "t": "2026-11-20T09:11:50+01:00",
      "k": "finish",
      "result": "Закрыты известные баги plan-fact, land_check, blocker confirm, redproof; R28 и R33–R35 не тронуты",
      "problems": 0
    }
  ],
  "reqList": [
    {
      "id": "R01",
      "text": "«plan-fact (сверять строку в доказательстве «сделано»»",
      "status": "done"
    },
    {
      "id": "R02",
      "text": "«не стирать ручные concerns с префиксом «план: »»",
      "status": "done"
    },
    {
      "id": "R03",
      "text": "«land_check (узнавать свой коммит без префикса темы»",
      "status": "done"
    },
    {
      "id": "R04",
      "text": "«видеть правки через merge-коммиты»",
      "status": "done"
    },
    {
      "id": "R05",
      "text": "«blocker confirm (способ исправить ошибочный confirmed по цитате пользователя)»",
      "status": "done"
    },
    {
      "id": "R06",
      "text": "«redproof (не считать ImportError на отсутствующую функцию красным по существу)»",
      "status": "done"
    },
    {
      "id": "R07",
      "text": "«R28 и R33–R35 не трогай»",
      "status": "done"
    }
  ],
  "gates": {
    "G1": {
      "ok": true,
      "at": "2026-11-20T09:01:19+01:00",
      "open": 0,
      "total": 7
    },
    "G2": {
      "ok": true,
      "at": "2026-11-20T09:01:34+01:00",
      "found": 0,
      "fixed": 0,
      "deferred": 0
    },
    "G3": {
      "ok": true,
      "at": "2026-11-20T09:01:36+01:00",
      "problems": 0
    },
    "G4": {
      "ok": true,
      "at": "2026-11-20T09:11:50+01:00",
      "checked": 7,
      "matched": 7
    }
  },
  "result": "Закрыты известные баги plan-fact, land_check, blocker confirm, redproof; R28 и R33–R35 не тронуты",
  "skillVersion": "2.7.0",
  "spend": {
    "byRole": {
      "reviewer": {
        "n": 2,
        "input": 12,
        "output": 8376,
        "cache_read": 93079,
        "cache_write": 61827,
        "tokens": 8388,
        "hit": 60
      },
      "acceptance": {
        "n": 1,
        "input": 16,
        "output": 3314,
        "cache_read": 158769,
        "cache_write": 25703,
        "tokens": 3330,
        "hit": 86
      },
      "executor": {
        "n": 1,
        "input": 66,
        "output": 22593,
        "cache_read": 1990266,
        "cache_write": 87824,
        "tokens": 22659,
        "hit": 96
      },
      "orchestrator": {
        "n": 1,
        "input": 68,
        "output": 19823,
        "cache_read": 5496635,
        "cache_write": 60062,
        "tokens": 19891,
        "hit": 99
      }
    },
    "byModel": {
      "claude-haiku-5-5": {
        "n": 1,
        "input": 4,
        "output": 4654,
        "cache_read": 14784,
        "cache_write": 26799,
        "tokens": 4658,
        "hit": 36
      },
      "claude-sonnet-5-5": {
        "n": 4,
        "input": 158,
        "output": 49452,
        "cache_read": 7723965,
        "cache_write": 208617,
        "tokens": 49610,
        "hit": 97
      }
    },
    "byTicket": {
      "01": {
        "n": 1,
        "input": 66,
        "output": 22593,
        "cache_read": 1990266,
        "cache_write": 87824,
        "tokens": 22659,
        "hit": 96
      }
    }
  },
  "history": [
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
    },
    {
      "dir": "2026-11-03-audit-fixes",
      "title": "Исправления по аудиту Autopilot 2026-11-03",
      "startedAt": "2026-11-03T16:24:15+00:00",
      "finishedAt": "2026-11-03T20:02:53+01:00",
      "minutes": 147,
      "tickets": 4,
      "repairs": 2,
      "result": "Закрыты 18 пунктов аудита: общий state_io, проверка зон и путей, точный allowlist моделей, подпись гейтов, документация и CI",
      "tokens": 0
    }
  ],
  "logFailures": 0,
  "planContractDigest": "d0e29507f22ddbf865fb99a47c947256b9465267156d3cc8b40e1d12e21a7b0a",
  "planValidationDigest": "38964201cf39a4496e372e5672b0a93639a5fb542b3a981cd9e9ffcd4a6142fd",
  "blindRounds": 1
}
