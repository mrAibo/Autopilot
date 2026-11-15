window.STATE =
{
  "version": 2,
  "slug": "audit-dashboard-haiku",
  "dir": "2026-11-15-audit-dashboard-haiku--wip",
  "title": "Правки аудита 2026-11-15: дашборд, маршрутизация, Haiku",
  "mode": "semi",
  "depth": "normal",
  "tier": "T2",
  "strictRouting": true,
  "gateSigned": true,
  "sequentialHost": false,
  "isolateTickets": false,
  "briefFile": "2026-11-15-brief.md",
  "memoryFile": "AGENTS.md",
  "memoryOwner": "autopilot",
  "skillDir": "C:/Users/crown/Downloads/Projects/Autopilot/skills/autopilot",
  "baseCommit": null,
  "startedAt": "2026-11-15T03:30:28+01:00",
  "updatedAt": "2026-11-15T03:35:53+01:00",
  "finishedAt": null,
  "stages": [
    {
      "id": "preflight",
      "status": "done",
      "startedAt": "2026-11-15T03:30:28+01:00",
      "finishedAt": "2026-11-15T03:30:46+01:00"
    },
    {
      "id": "manifest",
      "status": "done",
      "startedAt": "2026-11-15T03:30:46+01:00",
      "finishedAt": "2026-11-15T03:30:59+01:00"
    },
    {
      "id": "briefing",
      "status": "done",
      "startedAt": "2026-11-15T03:30:59+01:00",
      "finishedAt": "2026-11-15T03:31:31+01:00"
    },
    {
      "id": "spec",
      "status": "done",
      "startedAt": "2026-11-15T03:31:31+01:00",
      "finishedAt": "2026-11-15T03:33:59+01:00"
    },
    {
      "id": "plan",
      "status": "active",
      "startedAt": "2026-11-15T03:33:59+01:00"
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
    "total": 29,
    "done": 0,
    "inTicket": 29,
    "inSpec": 0,
    "placeholder": 0,
    "deferred": 0,
    "dropped": 0
  },
  "tickets": [
    {
      "id": "01",
      "title": "ap.py: пути, сервер, этапы, данные для дашборда и отчёт по моделям",
      "requirements": [
        "R01",
        "R02",
        "R03",
        "R04",
        "R07",
        "R12",
        "R19",
        "R20",
        "R26",
        "R27"
      ],
      "blockedBy": [],
      "wave": 1,
      "zone": [
        "skills/autopilot/tools/ap.py",
        "tests/test_ap_audit.py",
        ".gitignore"
      ],
      "review": "да — риск: сервер дашборда отдаёт данные сборки",
      "model": "обычная",
      "fingerprint": "0a6d6cfcfe7af98ec4240620362dc3d404f58082ee5f350f92988fd280c2e4f4",
      "status": "pending",
      "retries": 0,
      "repairs": 0,
      "plannedRouting": {
        "ticket": "01",
        "provider": "anthropic",
        "model": "sonnet",
        "effort": "high",
        "effortEnforced": null,
        "profile": "strong",
        "score": 40,
        "factors": {
          "algorithm": 5,
          "coupling": 10,
          "uncertainty": 0,
          "context": 5,
          "testing": 10,
          "risk": 10
        },
        "reason": "score=40; profile=strong; high-risk=True",
        "requiresReview": true,
        "status": "blocked",
        "fingerprint": "0a6d6cfcfe7af98ec4240620362dc3d404f58082ee5f350f92988fd280c2e4f4",
        "hostExecutionVerified": false,
        "error": "No verified host capabilities",
        "applied": false
      }
    },
    {
      "id": "02",
      "title": "Роутер, журнал расхода, ключ подписи и граница Bash",
      "requirements": [
        "R05",
        "R06",
        "R08",
        "R21",
        "R23",
        "R24",
        "R27",
        "R29"
      ],
      "blockedBy": [],
      "wave": 1,
      "zone": [
        "skills/autopilot/tools/model_router.py",
        "skills/autopilot/tools/retry_policy.py",
        "skills/autopilot/tools/run_log.py",
        "skills/autopilot/tools/claude_attest.py",
        "skills/autopilot/tools/gate_sign.py",
        "skills/autopilot/tools/claude_agent_guard.py",
        "skills/autopilot/tools/agent_profiles.py",
        "skills/autopilot/tools/model-capabilities.json",
        "tests/test_model_router.py",
        "tests/test_retry_policy.py",
        "tests/test_run_log.py",
        "tests/test_claude_attest.py",
        "tests/test_gate_sign.py",
        "tests/test_claude_agent_guard.py",
        "tests/test_agent_profiles.py",
        "tests/test_audit_routing.py"
      ],
      "review": "да — риск: подпись гейтов, ключ и граница Bash",
      "model": "сильная",
      "fingerprint": "f1151379fd6bb5942f1e94f4cf93b047e0a764b13b0c08ce733be8b52de7eb46",
      "status": "pending",
      "retries": 0,
      "repairs": 0,
      "plannedRouting": {
        "ticket": "02",
        "provider": "anthropic",
        "model": "sonnet",
        "effort": "high",
        "effortEnforced": null,
        "profile": "strong",
        "score": 50,
        "factors": {
          "algorithm": 5,
          "coupling": 20,
          "uncertainty": 0,
          "context": 5,
          "testing": 10,
          "risk": 10
        },
        "reason": "score=50; profile=strong; high-risk=True",
        "requiresReview": true,
        "status": "blocked",
        "fingerprint": "f1151379fd6bb5942f1e94f4cf93b047e0a764b13b0c08ce733be8b52de7eb46",
        "hostExecutionVerified": false,
        "error": "No verified host capabilities",
        "applied": false
      }
    },
    {
      "id": "03",
      "title": "Эскалация Haiku → Sonnet в ap.py, документы фаз и счётчик тестов",
      "requirements": [
        "R21",
        "R22",
        "R23",
        "R24",
        "R25",
        "R28"
      ],
      "blockedBy": [
        "01",
        "02"
      ],
      "wave": 2,
      "zone": [
        "skills/autopilot/tools/ap.py",
        "skills/autopilot/tools/test_count.py",
        "skills/autopilot/phases/3-spec.md",
        "skills/autopilot/phases/4-plan.md",
        "skills/autopilot/phases/5-subagents.md",
        "skills/autopilot/prompts/",
        "docs/autopilot/model-routing.md",
        "docs/autopilot/retry-policy.md",
        "docs/autopilot/run-log.md",
        "docs/autopilot/claude-code.md",
        "README.md",
        "README.ru.md",
        "README.de.md",
        "AGENTS.md",
        "tests/test_audit_docs.py",
        "tests/test_ap_escalation.py"
      ],
      "review": "нет",
      "model": "обычная",
      "fingerprint": "826ba928799ae53c9505d5d7135accbad9d5c749f94d7716e371386752bb0897",
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
        "score": 50,
        "factors": {
          "algorithm": 5,
          "coupling": 20,
          "uncertainty": 0,
          "context": 5,
          "testing": 10,
          "risk": 10
        },
        "reason": "score=50; profile=strong; high-risk=True",
        "requiresReview": true,
        "status": "blocked",
        "fingerprint": "826ba928799ae53c9505d5d7135accbad9d5c749f94d7716e371386752bb0897",
        "hostExecutionVerified": false,
        "error": "No verified host capabilities",
        "applied": false
      }
    },
    {
      "id": "04",
      "title": "Дашборд: страница «Сейчас», исправления ленты и этапов, человеческий язык",
      "requirements": [
        "R03",
        "R04",
        "R09",
        "R10",
        "R11",
        "R13",
        "R17"
      ],
      "blockedBy": [],
      "wave": 1,
      "zone": [
        "skills/autopilot/phases/dashboard-template.html",
        "docs/autopilot/dashboard-views.md",
        "tests/test_dashboard_views.py",
        "tests/test_dashboard_now.py"
      ],
      "review": "нет",
      "model": "сильная",
      "fingerprint": "3ec5d553a60661f0a69aa91c3c95a2c41de6a8a28e18adee054994e3dfc01cc5",
      "status": "pending",
      "retries": 0,
      "repairs": 0,
      "plannedRouting": {
        "ticket": "04",
        "provider": "anthropic",
        "model": "sonnet",
        "effort": "high",
        "effortEnforced": null,
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
        "status": "blocked",
        "fingerprint": "3ec5d553a60661f0a69aa91c3c95a2c41de6a8a28e18adee054994e3dfc01cc5",
        "hostExecutionVerified": false,
        "error": "No verified host capabilities",
        "applied": false
      }
    },
    {
      "id": "05",
      "title": "Дашборд: доска тасков, доска требований, панель таска, «нужен твой ответ»",
      "requirements": [
        "R14",
        "R15",
        "R16",
        "R18"
      ],
      "blockedBy": [
        "04"
      ],
      "wave": 2,
      "zone": [
        "skills/autopilot/phases/dashboard-template.html",
        "tests/test_dashboard_boards.py"
      ],
      "review": "нет",
      "model": "сильная",
      "fingerprint": "1f39dd3cd036ad8ad93dc9764fc1952555fc2f453df9621b877ff57de9e0db05",
      "status": "pending",
      "retries": 0,
      "repairs": 0,
      "plannedRouting": {
        "ticket": "05",
        "provider": "anthropic",
        "model": "sonnet",
        "effort": "high",
        "effortEnforced": null,
        "profile": "strong",
        "score": 30,
        "factors": {
          "algorithm": 5,
          "coupling": 5,
          "uncertainty": 0,
          "context": 0,
          "testing": 10,
          "risk": 10
        },
        "reason": "score=30; profile=strong; high-risk=True",
        "requiresReview": true,
        "status": "blocked",
        "fingerprint": "1f39dd3cd036ad8ad93dc9764fc1952555fc2f453df9621b877ff57de9e0db05",
        "hostExecutionVerified": false,
        "error": "No verified host capabilities",
        "applied": false
      }
    },
    {
      "id": "06",
      "title": "Дашборд: расход, история сборок, неполный журнал, эскалация",
      "requirements": [
        "R19",
        "R20",
        "R24",
        "R27"
      ],
      "blockedBy": [
        "01",
        "05"
      ],
      "wave": 3,
      "zone": [
        "skills/autopilot/phases/dashboard-template.html",
        "tests/test_dashboard_details.py"
      ],
      "review": "нет",
      "model": "обычная",
      "fingerprint": "ef8b4319b736dff36d6272677408bff03711c995b1516482fa5fa7b227e5928f",
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
        "score": 30,
        "factors": {
          "algorithm": 5,
          "coupling": 5,
          "uncertainty": 0,
          "context": 0,
          "testing": 10,
          "risk": 10
        },
        "reason": "score=30; profile=strong; high-risk=True",
        "requiresReview": true,
        "status": "blocked",
        "fingerprint": "ef8b4319b736dff36d6272677408bff03711c995b1516482fa5fa7b227e5928f",
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
  "coverage": null,
  "concerns": [],
  "blockingFindings": [],
  "blind": null,
  "beats": [
    "2026-11-15T03:30:28+01:00",
    "2026-11-15T03:30:45+01:00",
    "2026-11-15T03:30:46+01:00",
    "2026-11-15T03:30:59+01:00",
    "2026-11-15T03:31:00+01:00",
    "2026-11-15T03:31:30+01:00",
    "2026-11-15T03:31:31+01:00",
    "2026-11-15T03:33:59+01:00",
    "2026-11-15T03:35:49+01:00",
    "2026-11-15T03:35:50+01:00",
    "2026-11-15T03:35:53+01:00"
  ],
  "rev": 15,
  "waiting": null,
  "waits": [
    {
      "kind": "briefing",
      "from": "2026-11-15T03:31:00+01:00",
      "to": "2026-11-15T03:31:30+01:00"
    }
  ],
  "log": [
    {
      "t": "2026-11-15T03:30:28+01:00",
      "k": "init"
    },
    {
      "t": "2026-11-15T03:30:46+01:00",
      "k": "stage",
      "id": "manifest",
      "act": "start"
    },
    {
      "t": "2026-11-15T03:30:59+01:00",
      "k": "stage",
      "id": "briefing",
      "act": "start"
    },
    {
      "t": "2026-11-15T03:31:00+01:00",
      "k": "ask",
      "kind": "briefing",
      "note": "два вопроса — судьба восьми тем дашборда (I01), ключ подписи в хранилище ОС (I17)"
    },
    {
      "t": "2026-11-15T03:31:30+01:00",
      "k": "answered",
      "kind": "briefing"
    },
    {
      "t": "2026-11-15T03:31:31+01:00",
      "k": "gate",
      "g": "G1",
      "ok": false,
      "open": 29,
      "total": 29
    },
    {
      "t": "2026-11-15T03:31:31+01:00",
      "k": "stage",
      "id": "spec",
      "act": "start"
    },
    {
      "t": "2026-11-15T03:31:31+01:00",
      "k": "gate",
      "g": "G1",
      "ok": true,
      "open": 0,
      "total": 29
    },
    {
      "t": "2026-11-15T03:33:59+01:00",
      "k": "stage",
      "id": "plan",
      "act": "start"
    },
    {
      "t": "2026-11-15T03:35:49+01:00",
      "k": "tier",
      "v": "T2"
    },
    {
      "t": "2026-11-15T03:35:50+01:00",
      "k": "tickets",
      "n": 6
    },
    {
      "t": "2026-11-15T03:35:50+01:00",
      "k": "gate",
      "g": "G3",
      "ok": true,
      "problems": 0
    },
    {
      "t": "2026-11-15T03:35:53+01:00",
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
      "text": "«A01: skills/autopilot/tools/ap.py:402,555,700,1615,1848,2024,2222,2243 — пути к таскам собираются через glob.glob от абсолютного пути проекта; [ и ] в пути читаются как шаблон, и файлы тасков не находятся»",
      "status": "in-ticket"
    },
    {
      "id": "R02",
      "text": "«A02: skills/autopilot/tools/ap.py:865-866 — сервер дашборда отдаёт весь каталог .autopilot без проверки Host/Origin и без токена; state.js — это обычный скрипт window.STATE = {...}»",
      "status": "in-ticket"
    },
    {
      "id": "R03",
      "text": "«A03: skills/autopilot/phases/dashboard-template.html:1137-1140, 1265-1268, 1912 и skills/autopilot/tools/ap.py:270-278, 3091 — при сбросе гейта из-за смены плана в ленту пишется запись без чисел, а дашборд рисует её обычным шаблоном»",
      "status": "in-ticket"
    },
    {
      "id": "R04",
      "text": "«A04: skills/autopilot/tools/ap.py:1279-1289 и skills/autopilot/phases/dashboard-template.html:1683, 2214-2216 — при возврате этапа время начала остаётся старым, а время конца переписывается; минуты этапа считаются по этим двум меткам»",
      "status": "in-ticket"
    },
    {
      "id": "R05",
      "text": "«A05: skills/autopilot/tools/model_router.py:200-219 — риск таска определяется словами в его тексте: «подпись», «ключ», «token», «signature», а подстроки auth, session, migration ловятся даже внутри других слов («author»)»",
      "status": "in-ticket"
    },
    {
      "id": "R06",
      "text": "«A06: skills/autopilot/tools/run_log.py:24, skills/autopilot/tools/claude_attest.py:84-86 — в строках расхода журнала нет модели и effort»",
      "status": "in-ticket"
    },
    {
      "id": "R07",
      "text": "«A07: skills/autopilot/tools/ap.py:734-737 — снимок дашборда пишется голым os.replace, без повтора, который есть в state_io.replace_with_retry»",
      "status": "in-ticket"
    },
    {
      "id": "R08",
      "text": "«A08: skills/autopilot/tools/gate_sign.py:98 — запись «прогон начат подписанным» пишется не атомарно (в коде помечено shortcut: not atomic)»",
      "status": "in-ticket"
    },
    {
      "id": "R09",
      "text": "«A09: skills/autopilot/phases/dashboard-template.html:2460 — «обновлено N назад» в шапке рисуется и у сданной сборки»",
      "status": "in-ticket"
    },
    {
      "id": "R10",
      "text": "«A10: skills/autopilot/phases/dashboard-template.html:1820 — в теме «Классика» счётчик повторов и починок виден только у сданного таска»",
      "status": "in-ticket"
    },
    {
      "id": "R11",
      "text": "«A11: skills/autopilot/phases/dashboard-template.html:1764, 2120 — полоса этапов объявлена списком (role=\"list\"), а её элементы — без role=\"listitem\"»",
      "status": "in-ticket"
    },
    {
      "id": "R12",
      "text": "«A12: .gitignore:2-8 — игнорируется только .autopilot/state.lock, а skills/autopilot/tools/state.lock лежит неотслеживаемым»",
      "status": "in-ticket"
    },
    {
      "id": "R13",
      "text": "«I01: — Одна страница, которая сама показывает нужное по состоянию сборки, вместо восьми переключаемых тем — пользователь не должен выбирать, куда смотреть»",
      "status": "in-ticket"
    },
    {
      "id": "R14",
      "text": "«I02: — Kanban-доска тасков как живой вид этапа «Разработка» — с одного взгляда видно, где всё сейчас и что застряло»",
      "status": "in-ticket"
    },
    {
      "id": "R15",
      "text": "«I03: — Доска требований: твои фразы как карточки, которые идут «Разбирается → В плане → Делается → Проверяется → Принято» — ты видишь судьбу каждого своего слова, а не внутренние таски»",
      "status": "in-ticket"
    },
    {
      "id": "R16",
      "text": "«I04: — Клик по таску открывает его историю в боковой панели — сейчас подробности одного таска разбросаны по четырём темам»",
      "status": "in-ticket"
    },
    {
      "id": "R17",
      "text": "«I05: — Человеческий язык вместо служебного — навык обещает, что пользователь не читает спецификаций»",
      "status": "in-ticket"
    },
    {
      "id": "R18",
      "text": "«I06: — «Нужен твой ответ» нельзя пропустить — пока сборка ждёт, время идёт впустую»",
      "status": "in-ticket"
    },
    {
      "id": "R19",
      "text": "«I07: — Расход на виду: токены по ролям и моделям, «сколько стоил этот таск», сравнение с прошлыми сборками — это первый вопрос после «готово ли»»",
      "status": "in-ticket"
    },
    {
      "id": "R20",
      "text": "«I08: — Лента прошлых сборок на дашборде: длительность, число тасков и починок, расход, итог — видно, становится ли быстрее и дешевле»",
      "status": "in-ticket"
    },
    {
      "id": "R21",
      "text": "«I09: — Сложность таска оценивает планировщик, а не регулярное выражение — он прочитал спецификацию и понимает, что «документация про подписи» не опасна»",
      "status": "in-ticket"
    },
    {
      "id": "R22",
      "text": "«I10: — «Haiku-таски» по замыслу плана: механическую работу планировщик выносит в отдельные маленькие таски — чёткая постановка появляется не сама, её нужно нарезать»",
      "status": "in-ticket"
    },
    {
      "id": "R23",
      "text": "«I11: — Дешёвый профиль для кода — Haiku на высоком effort, а не на низком — сейчас cheap один на разведчика и исполнителя: haiku/low»",
      "status": "in-ticket"
    },
    {
      "id": "R24",
      "text": "«I12: — Страховка: одна автоматическая эскалация Haiku → Sonnet, если дешёвый таск вернулся с красной проверкой после первого дозапроса — без неё расширять Haiku рискованно»",
      "status": "in-ticket"
    },
    {
      "id": "R25",
      "text": "«I13: — Haiku собирает «пакет контекста» для Sonnet-исполнителя: нужные выдержки из файлов и интерфейсы одним файлом — чтение и есть основной расход»",
      "status": "in-ticket"
    },
    {
      "id": "R26",
      "text": "«I14: — Замер вместо веры: report-run показывает по каждой модели долю тасков, сданных с первого раза, число починок и токены на таск; затем одна пробная сборка, где механические таски идут на Haiku»",
      "status": "in-ticket"
    },
    {
      "id": "R27",
      "text": "«I15: — Счётчик «строк журнала не записано» в state.js и на дашборде — сбой записи журнала проглатывается по замыслу, но владелец должен видеть, что журнал неполный»",
      "status": "in-ticket"
    },
    {
      "id": "R28",
      "text": "«I16: — Число тестов в AGENTS.md и README подставлять скриптом — сейчас там «730», прогон даёт 750»",
      "status": "in-ticket"
    },
    {
      "id": "R29",
      "text": "«I17: — Сузить принятую границу Bash: запретить субагенту в bash_gate пути .autopilot/, ~/.autopilot/, .claude/agents/, ключ подписи держать в хранилище ОС — сейчас это задокументированное ограничение (docs/autopilot/claude-code.md:55), по…",
      "status": "in-ticket"
    }
  ],
  "gates": {
    "G1": {
      "ok": true,
      "at": "2026-11-15T03:31:31+01:00",
      "open": 0,
      "total": 29
    },
    "G3": {
      "ok": true,
      "at": "2026-11-15T03:35:50+01:00",
      "problems": 0
    }
  },
  "result": null,
  "gateMark": "8d230a14c24d3c889f3dc86d9c6ed82684958693d10ceebb316c1022e15c1ff7",
  "skillVersion": "2.7.0",
  "planContractDigest": "9ef5e9d687b2299109a1996bbcd919803ce06f2c82bf7da740fa17c38f467d5e",
  "planValidationDigest": "3384d03dc720b52d3465cad0bdbbe0a08a61d3f148294153c59d48e4862fb33d"
}
