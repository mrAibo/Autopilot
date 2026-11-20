window.STATE =
{
  "schemaVersion": 1,
  "version": 2,
  "slug": "tails-and-r28",
  "dir": "2026-11-21-tails-and-r28--wip",
  "title": "Хвосты и R28: решения и пресеты",
  "mode": "semi",
  "depth": "normal",
  "kind": "task",
  "tier": "T2",
  "strictRouting": false,
  "gateSigned": false,
  "sequentialHost": false,
  "spendLedger": [],
  "isolateTickets": false,
  "briefFile": "2026-11-21-brief.md",
  "memoryFile": "AGENTS.md",
  "memoryOwner": "autopilot",
  "skillDir": "C:/Users/crown/Downloads/Projects/Autopilot/skills/autopilot",
  "baseCommit": null,
  "startedAt": "2026-11-21T00:35:02+01:00",
  "updatedAt": "2026-11-21T00:41:30+01:00",
  "finishedAt": null,
  "stages": [
    {
      "id": "preflight",
      "status": "done",
      "startedAt": "2026-11-21T00:35:02+01:00",
      "segments": [
        {
          "startedAt": "2026-11-21T00:35:02+01:00",
          "finishedAt": "2026-11-21T00:35:07+01:00"
        }
      ],
      "finishedAt": "2026-11-21T00:35:07+01:00"
    },
    {
      "id": "manifest",
      "status": "done",
      "segments": [
        {
          "startedAt": "2026-11-21T00:35:07+01:00",
          "finishedAt": "2026-11-21T00:35:53+01:00"
        }
      ],
      "startedAt": "2026-11-21T00:35:07+01:00",
      "finishedAt": "2026-11-21T00:35:53+01:00"
    },
    {
      "id": "briefing",
      "status": "skipped",
      "segments": [
        {
          "startedAt": "2026-11-21T00:35:53+01:00",
          "finishedAt": "2026-11-21T00:35:53+01:00"
        }
      ],
      "startedAt": "2026-11-21T00:35:53+01:00",
      "finishedAt": "2026-11-21T00:35:53+01:00",
      "note": "вопросов не потребовалось: объём задан PROGRESS.md и R28 из брифа"
    },
    {
      "id": "spec",
      "status": "done",
      "segments": [
        {
          "startedAt": "2026-11-21T00:35:53+01:00",
          "finishedAt": "2026-11-21T00:41:25+01:00"
        }
      ],
      "startedAt": "2026-11-21T00:35:53+01:00",
      "finishedAt": "2026-11-21T00:41:25+01:00"
    },
    {
      "id": "plan",
      "status": "active",
      "segments": [
        {
          "startedAt": "2026-11-21T00:41:25+01:00",
          "finishedAt": null
        }
      ],
      "startedAt": "2026-11-21T00:41:25+01:00"
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
    "total": 21,
    "done": 0,
    "inTicket": 17,
    "inSpec": 0,
    "placeholder": 0,
    "deferred": 4,
    "dropped": 0
  },
  "tickets": [
    {
      "id": "01",
      "title": "Подпись кнопки, мёртвый CSS, строка «план: N из M»",
      "requirements": [
        "R01",
        "R10",
        "R11"
      ],
      "blockedBy": [],
      "wave": 1,
      "zone": [
        "skills/autopilot/phases/dashboard-template.html",
        "tests/test_dashboard_buttons.py",
        "tests/test_dashboard_now.py",
        "tests/test_dashboard_boards.py",
        "tests/test_followups_dashboard.py",
        "tests/test_dashboard_views.py",
        "tests/test_dashboard_designs.py",
        "docs/adr/0017-*.md",
        "docs/adr/0019-*.md"
      ],
      "review": "нет",
      "model": "обычная",
      "repro": false,
      "testsEdit": null,
      "fingerprint": "1fda705befa795249710c1d85fa574ceff61847f780b4d71ac4bc8517c00c7b2",
      "status": "pending",
      "retries": 0,
      "repairs": 0,
      "plannedRouting": {
        "ticket": "01",
        "provider": "anthropic",
        "model": "sonnet",
        "effort": "medium",
        "effortEnforced": null,
        "profile": "balanced",
        "score": 51,
        "factors": {
          "algorithm": 10,
          "coupling": 20,
          "uncertainty": 11,
          "context": 5,
          "testing": 5,
          "risk": 0
        },
        "reason": "score=51; profile=balanced; high-risk=False; class=обычный; risk=обычный; why=правка шаблона и тестов по образцу, но с удалением кода, на который ссылаются тесты",
        "requiresReview": false,
        "status": "blocked",
        "fingerprint": "1fda705befa795249710c1d85fa574ceff61847f780b4d71ac4bc8517c00c7b2",
        "hostExecutionVerified": false,
        "error": "No verified host capabilities",
        "applied": false
      }
    },
    {
      "id": "02",
      "title": "`ask accept` только в manual, `::имя`, redproof, git-версия, chore",
      "requirements": [
        "R02",
        "R04",
        "R05",
        "R19",
        "R21"
      ],
      "blockedBy": [],
      "wave": 1,
      "zone": [
        "skills/autopilot/tools/ap.py",
        "skills/autopilot/tools/plan_items.py",
        "tests/test_dashboard_actions.py",
        "tests/test_review_accuracy.py",
        "tests/test_work_kinds.py",
        "tests/test_one_command.py",
        "tests/test_git_version.py"
      ],
      "review": "нет",
      "model": "обычная",
      "repro": false,
      "testsEdit": null,
      "fingerprint": "dc9d63b278c4d7384287993cb2292ef15d33b7786eeae8fe4d34574245dd6be8",
      "status": "pending",
      "retries": 0,
      "repairs": 0,
      "plannedRouting": {
        "ticket": "02",
        "provider": "anthropic",
        "model": "sonnet",
        "effort": "medium",
        "effortEnforced": null,
        "profile": "balanced",
        "score": 51,
        "factors": {
          "algorithm": 10,
          "coupling": 20,
          "uncertainty": 11,
          "context": 5,
          "testing": 5,
          "risk": 0
        },
        "reason": "score=51; profile=balanced; high-risk=False; class=обычный; risk=обычный; why=пять небольших правок CLI с регресс-тестами, без нового протокола",
        "requiresReview": false,
        "status": "blocked",
        "fingerprint": "dc9d63b278c4d7384287993cb2292ef15d33b7786eeae8fe4d34574245dd6be8",
        "hostExecutionVerified": false,
        "error": "No verified host capabilities",
        "applied": false
      }
    },
    {
      "id": "03",
      "title": "Старый сервер перезапускается, ping с nonce, чистый `serve.log`",
      "requirements": [
        "R03",
        "R09"
      ],
      "blockedBy": [
        "02"
      ],
      "wave": 2,
      "zone": [
        "skills/autopilot/tools/ap.py",
        "tests/test_followups_token.py",
        "tests/test_ap_audit.py",
        "tests/test_dashboard_actions.py",
        "docs/adr/0013-server-ping.md"
      ],
      "review": "нет",
      "model": "обычная",
      "repro": false,
      "testsEdit": null,
      "fingerprint": "aae78be6cf28c4e3043c40621462c7870949cbc1a8b006375de16bbe360de598",
      "status": "pending",
      "retries": 0,
      "repairs": 0,
      "plannedRouting": {
        "ticket": "03",
        "provider": "anthropic",
        "model": "sonnet",
        "effort": "high",
        "effortEnforced": null,
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
        "reason": "score=55; profile=strong; high-risk=False; class=сложный; risk=обычный; why=меняет протокол проверки «свой сервер» и поведение перезапуска, где легко получить петлю перезапусков или чужой сервер",
        "requiresReview": true,
        "status": "blocked",
        "fingerprint": "aae78be6cf28c4e3043c40621462c7870949cbc1a8b006375de16bbe360de598",
        "hostExecutionVerified": false,
        "error": "No verified host capabilities",
        "applied": false
      }
    },
    {
      "id": "04",
      "title": "Уроки под замком, расход без дублей и чужих папок, тест без `~/.claude`",
      "requirements": [
        "R06",
        "R07",
        "R08"
      ],
      "blockedBy": [
        "03"
      ],
      "wave": 3,
      "zone": [
        "skills/autopilot/tools/ap.py",
        "skills/autopilot/tools/lessons.py",
        "skills/autopilot/tools/run_log.py",
        "tests/test_lessons.py",
        "tests/test_subagent_spend.py",
        "tests/test_review_accuracy.py",
        "CHANGELOG.md"
      ],
      "review": "нет",
      "model": "обычная",
      "repro": false,
      "testsEdit": null,
      "fingerprint": "5526f6c573e60ae10e57bd766ffa8c5d302f11154909668b39cb349153bf3c47",
      "status": "pending",
      "retries": 0,
      "repairs": 0,
      "plannedRouting": {
        "ticket": "04",
        "provider": "anthropic",
        "model": "sonnet",
        "effort": "medium",
        "effortEnforced": null,
        "profile": "balanced",
        "score": 51,
        "factors": {
          "algorithm": 10,
          "coupling": 20,
          "uncertainty": 11,
          "context": 5,
          "testing": 5,
          "risk": 0
        },
        "reason": "score=51; profile=balanced; high-risk=False; class=обычный; risk=обычный; why=три независимые правки по образцу соседнего кода, с регресс-тестами",
        "requiresReview": false,
        "status": "blocked",
        "fingerprint": "5526f6c573e60ae10e57bd766ffa8c5d302f11154909668b39cb349153bf3c47",
        "hostExecutionVerified": false,
        "error": "No verified host capabilities",
        "applied": false
      }
    },
    {
      "id": "05",
      "title": "R28a: скриншоты для слепой приёмки, прототип за флагом и ADR 0030",
      "requirements": [
        "R12"
      ],
      "blockedBy": [],
      "wave": 1,
      "zone": [
        "skills/autopilot/tools/shots.py",
        "tests/test_shots.py",
        "docs/adr/0030-*.md",
        "skills/autopilot/phases/8-final.md"
      ],
      "review": "нет",
      "model": "обычная",
      "repro": false,
      "testsEdit": null,
      "fingerprint": "157f2b8895945ad698c28b77d79e464ef799fc60d34537025a2166e1fe78ff30",
      "status": "pending",
      "retries": 0,
      "repairs": 0,
      "plannedRouting": {
        "ticket": "05",
        "provider": "anthropic",
        "model": "sonnet",
        "effort": "medium",
        "effortEnforced": null,
        "profile": "balanced",
        "score": 46,
        "factors": {
          "algorithm": 10,
          "coupling": 15,
          "uncertainty": 11,
          "context": 5,
          "testing": 5,
          "risk": 0
        },
        "reason": "score=46; profile=balanced; high-risk=False; class=обычный; risk=обычный; why=новый маленький инструмент по образцу `tools/check-dashboard-browser.py` и ADR",
        "requiresReview": false,
        "status": "blocked",
        "fingerprint": "157f2b8895945ad698c28b77d79e464ef799fc60d34537025a2166e1fe78ff30",
        "hostExecutionVerified": false,
        "error": "No verified host capabilities",
        "applied": false
      }
    },
    {
      "id": "06",
      "title": "R28b–d: три ADR (несколько репозиториев, чат-менеджер, пресеты)",
      "requirements": [
        "R13",
        "R14",
        "R15"
      ],
      "blockedBy": [],
      "wave": 1,
      "zone": [
        "docs/adr/0031-*.md",
        "docs/adr/0032-*.md",
        "docs/adr/0033-*.md"
      ],
      "review": "нет",
      "model": "обычная",
      "repro": false,
      "testsEdit": null,
      "fingerprint": "abe58370fc883aa7c6a6c720b0685c032a0d3caff838309d0a389c2de42c1ea9",
      "status": "pending",
      "retries": 0,
      "repairs": 0,
      "plannedRouting": {
        "ticket": "06",
        "provider": "anthropic",
        "model": "sonnet",
        "effort": "high",
        "effortEnforced": null,
        "profile": "strong",
        "score": 45,
        "factors": {
          "algorithm": 20,
          "coupling": 10,
          "uncertainty": 0,
          "context": 5,
          "testing": 10,
          "risk": 0
        },
        "reason": "score=45; profile=strong; high-risk=False; class=сложный; risk=обычный; why=решения-ADR требуют чтения кода и взвешивания вариантов, не правки по образцу",
        "requiresReview": true,
        "status": "blocked",
        "fingerprint": "abe58370fc883aa7c6a6c720b0685c032a0d3caff838309d0a389c2de42c1ea9",
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
    "found": 3,
    "fixed": 2,
    "deferred": 1,
    "items": [
      "R21 — отказ chore на грязном файле остаётся (защита правок пользователя); улучшено только сообщение"
    ]
  },
  "concerns": [],
  "blockingFindings": [],
  "blind": null,
  "beats": [
    "2026-11-21T00:35:02+01:00",
    "2026-11-21T00:35:07+01:00",
    "2026-11-21T00:35:40+01:00",
    "2026-11-21T00:35:53+01:00",
    "2026-11-21T00:41:25+01:00",
    "2026-11-21T00:41:26+01:00",
    "2026-11-21T00:41:30+01:00"
  ],
  "rev": 12,
  "waiting": null,
  "waits": [],
  "log": [
    {
      "t": "2026-11-21T00:35:02+01:00",
      "k": "init"
    },
    {
      "t": "2026-11-21T00:35:07+01:00",
      "k": "stage",
      "id": "manifest",
      "act": "start"
    },
    {
      "t": "2026-11-21T00:35:53+01:00",
      "k": "stage",
      "id": "briefing",
      "act": "skip",
      "note": "вопросов не потребовалось: объём задан PROGRESS.md и R28 из брифа"
    },
    {
      "t": "2026-11-21T00:35:53+01:00",
      "k": "gate",
      "g": "G1",
      "ok": false,
      "open": 21,
      "total": 21
    },
    {
      "t": "2026-11-21T00:35:53+01:00",
      "k": "stage",
      "id": "spec",
      "act": "start"
    },
    {
      "t": "2026-11-21T00:41:25+01:00",
      "k": "gate",
      "g": "G2",
      "ok": true,
      "found": 3,
      "fixed": 2,
      "deferred": 1
    },
    {
      "t": "2026-11-21T00:41:25+01:00",
      "k": "gate",
      "g": "G1",
      "ok": true,
      "open": 0,
      "total": 21
    },
    {
      "t": "2026-11-21T00:41:25+01:00",
      "k": "stage",
      "id": "plan",
      "act": "start"
    },
    {
      "t": "2026-11-21T00:41:26+01:00",
      "k": "tier",
      "v": "T2"
    },
    {
      "t": "2026-11-21T00:41:26+01:00",
      "k": "tickets",
      "n": 6
    },
    {
      "t": "2026-11-21T00:41:26+01:00",
      "k": "gate",
      "g": "G3",
      "ok": true,
      "problems": 0
    },
    {
      "t": "2026-11-21T00:41:30+01:00",
      "k": "plan-models",
      "provider": "anthropic",
      "applied": false,
      "tickets": 6,
      "blocked": 6
    }
  ],
  "reqList": [
    {
      "id": "R01",
      "text": "«Кнопки: после первого клика с подписи пропадает название действия»",
      "status": "in-ticket"
    },
    {
      "id": "R02",
      "text": "«ADR 0015: ask accept ограничен режимом manual только текстом фаз, CLI пускает его везде»",
      "status": "in-ticket"
    },
    {
      "id": "R03",
      "text": "«Сервер, запущенный старым ap.py, отвечает 501 на POST до перезапуска (finish или новый init)»",
      "status": "in-ticket"
    },
    {
      "id": "R04",
      "text": "«::имя ищется подстрокой»",
      "status": "in-ticket"
    },
    {
      "id": "R05",
      "text": "««cannot import name» в выводе даёт ложный отказ redproof»",
      "status": "in-ticket"
    },
    {
      "id": "R06",
      "text": "«lessons: проверка путей ловит только X:\\, /Users/, /home/; lessons.md, drop, profile refresh пишут без замка»",
      "status": "in-ticket"
    },
    {
      "id": "R07",
      "text": "«test_silence_without_any_transcript_is_not_all_alive читает реальный ~/.claude»",
      "status": "in-ticket"
    },
    {
      "id": "R08",
      "text": "«Расход: поиск папки субагентов по префиксу может взять соседний проект; повторный spend-orchestrator дописывает строки»",
      "status": "in-ticket"
    },
    {
      "id": "R09",
      "text": "«Сервер: управляющие символы подделывают serve.log; /.ap-ping без nonce»",
      "status": "in-ticket"
    },
    {
      "id": "R10",
      "text": "«Мёртвый CSS .nowh .ov3 .tl2 и data-narrow (~3 КБ) — убирать вместе с тестами»",
      "status": "in-ticket"
    },
    {
      "id": "R11",
      "text": "«Строка «план: N из M» на дашборде и отчёт не проверены в браузере»",
      "status": "in-ticket"
    },
    {
      "id": "R12",
      "text": "«R28a. Визуальная проверка агентом в браузере … ADR и минимальный прототип за флагом; по умолчанию выключено.»",
      "status": "in-ticket"
    },
    {
      "id": "R13",
      "text": "«R28b. Несколько репозиториев в одной сборке. ADR: что ломается (baseCommit, зоны, commit_paths, state.js), оценка работ. Кода нет.»",
      "status": "in-ticket"
    },
    {
      "id": "R14",
      "text": "«R28c. Чат-менеджер рядом с прогоном. ADR: нужен ли он при дашборде и ap.py; что даёт сверх. Кода нет.»",
      "status": "in-ticket"
    },
    {
      "id": "R15",
      "text": "«R28d. Пресеты ролей «Экономный / Оптимальный / Максимальный» … если пресет — просто имя для набора существующих настроек, сделать как одну команду ap.py preset <имя>, иначе ADR. Opus и Fable в пресетах не появляются без прежнего подтвержд…",
      "status": "in-ticket"
    },
    {
      "id": "R16",
      "text": "«Замеры R23f и R26d (как считать — docs/autopilot/measuring-cost.md) не сделаны»",
      "status": "deferred",
      "why": "нужны реальные сборки на разных моделях; здесь честно не измерить"
    },
    {
      "id": "R17",
      "text": "«лимит budgetTokens; Firefox/Safari для дашборда; пробная сборка на Haiku»",
      "status": "deferred",
      "why": "Firefox/Safari нет; Haiku-сборка — отдельный прогон; про budgetTokens не сказано, чего не хватает"
    },
    {
      "id": "R18",
      "text": "«scheduler.py/commit_paths/gate_sign: том без жёстких ссылок — пустой ключ не создаётся; брошенная заявка над целым ключом после ухода держателя остаётся до ручного удаления»",
      "status": "deferred",
      "why": "затрагивает подписи гейтов — по «Договорились» без слова пользователя не менять"
    },
    {
      "id": "R19",
      "text": "«трейлер Autopilot-Ticket нужен git ≥ 2.22»",
      "status": "in-ticket"
    },
    {
      "id": "R20",
      "text": "«worktrees.link_deps: копия node_modules на macOS/Linux проверена только подменой платформы»",
      "status": "deferred",
      "why": "нет macOS/Linux для проверки"
    },
    {
      "id": "R21",
      "text": "«chore не принимает грязный AGENTS.md, запускать до правок»",
      "status": "in-ticket"
    }
  ],
  "gates": {
    "G1": {
      "ok": true,
      "at": "2026-11-21T00:41:25+01:00",
      "open": 0,
      "total": 21
    },
    "G2": {
      "ok": true,
      "at": "2026-11-21T00:41:25+01:00",
      "found": 3,
      "fixed": 2,
      "deferred": 1
    },
    "G3": {
      "ok": true,
      "at": "2026-11-21T00:41:26+01:00",
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
  "planContractDigest": "83af169c1b374c961a0b1bddb03171a171046b5414efccb3188686ac5e37b29f",
  "planValidationDigest": "20c73e01b141f2263b28a0b1e8e81e00f42addf8f0311ba98424dbd2b4ab057a"
}
