window.STATE =
{
  "version": 2,
  "slug": "upstream-port-opus",
  "dir": "2026-11-08-upstream-port-opus--wip",
  "title": "Порт апстрима 2.2.2/2.2.3 и точечный Opus",
  "mode": "interview",
  "depth": "strict",
  "tier": "T1",
  "strictRouting": true,
  "gateSigned": true,
  "sequentialHost": false,
  "isolateTickets": false,
  "briefFile": "2026-11-08-brief.md",
  "memoryFile": "AGENTS.md",
  "memoryOwner": "autopilot",
  "skillDir": "C:/Users/crown/Downloads/Projects/Autopilot/skills/autopilot",
  "baseCommit": null,
  "startedAt": "2026-11-08T14:16:44+01:00",
  "updatedAt": "2026-11-08T14:30:56+01:00",
  "finishedAt": null,
  "stages": [
    {
      "id": "preflight",
      "status": "done",
      "startedAt": "2026-11-08T14:16:44+01:00",
      "finishedAt": "2026-11-08T14:17:01+01:00"
    },
    {
      "id": "manifest",
      "status": "done",
      "startedAt": "2026-11-08T14:17:01+01:00",
      "finishedAt": "2026-11-08T14:17:06+01:00"
    },
    {
      "id": "briefing",
      "status": "done",
      "startedAt": "2026-11-08T14:17:06+01:00",
      "finishedAt": "2026-11-08T14:19:23+01:00"
    },
    {
      "id": "spec",
      "status": "done",
      "startedAt": "2026-11-08T14:19:23+01:00",
      "finishedAt": "2026-11-08T14:30:45+01:00"
    },
    {
      "id": "plan",
      "status": "active",
      "startedAt": "2026-11-08T14:30:45+01:00"
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
    "total": 33,
    "done": 0,
    "inTicket": 33,
    "inSpec": 0,
    "placeholder": 0,
    "deferred": 0,
    "dropped": 0
  },
  "tickets": [
    {
      "id": "01",
      "title": "Порт: лимиты, G1, слепая приёмка, finish с оговорками, git-check",
      "requirements": [
        "R01",
        "R02",
        "R03",
        "R04",
        "R06",
        "R09",
        "R10",
        "R11",
        "R12",
        "R13",
        "R14",
        "R23",
        "R26",
        "R27",
        "R29",
        "R30"
      ],
      "blockedBy": [],
      "wave": 1,
      "zone": [
        "skills/autopilot/tools/ap.py",
        "skills/autopilot/tools/retry_policy.py",
        "tests/test_ap.py",
        "tests/test_retry_policy.py"
      ],
      "review": "нет",
      "model": null,
      "fingerprint": "ff8b4a3c5550b21d47482e8584469beac7da3b9cca12ccf49a400df379dcf73e",
      "status": "pending",
      "retries": 0,
      "repairs": 0
    },
    {
      "id": "02",
      "title": "Opus: политика роутера, допуск guard и профили",
      "requirements": [
        "R16",
        "R18",
        "R20",
        "R21",
        "R23",
        "R26",
        "R27",
        "R29",
        "R30"
      ],
      "blockedBy": [],
      "wave": 1,
      "zone": [
        "skills/autopilot/tools/model_router.py",
        "skills/autopilot/tools/claude_agent_guard.py",
        "skills/autopilot/tools/agent_profiles.py",
        "tests/test_model_router.py",
        "tests/test_claude_agent_guard.py",
        "tests/test_agent_profiles.py"
      ],
      "review": "да — риск: допуск дорогой модели в строгом прогоне",
      "model": null,
      "fingerprint": "3a687c89eb9cc29dafcbd36a80d3fd391644351099b6946c3aa5fcaafb4ee2f7",
      "status": "pending",
      "retries": 0,
      "repairs": 0
    },
    {
      "id": "03",
      "title": "Opus: команда opus, подтверждение и plan-models",
      "requirements": [
        "R17",
        "R18",
        "R19",
        "R21",
        "G01",
        "R23",
        "R24",
        "R25",
        "R26",
        "R27",
        "R29",
        "R30"
      ],
      "blockedBy": [
        "01",
        "02"
      ],
      "wave": 2,
      "zone": [
        "skills/autopilot/tools/ap.py",
        "tests/test_ap.py"
      ],
      "review": "да — риск: подпись подтверждения и цитата пользователя",
      "model": null,
      "fingerprint": "dba8570d8e53bb1ce4ff65598029011e6be4cc7457817caa9d449590c0bd5215",
      "status": "pending",
      "retries": 0,
      "repairs": 0
    },
    {
      "id": "04",
      "title": "Дашборд, фазы и документы",
      "requirements": [
        "R05",
        "R06",
        "R07",
        "R08",
        "R14",
        "R15",
        "R22",
        "R28",
        "R31",
        "R32"
      ],
      "blockedBy": [
        "03"
      ],
      "wave": 3,
      "zone": [
        "skills/autopilot/phases/",
        "skills/autopilot/SKILL.md",
        "docs/autopilot/",
        "CHANGELOG.md",
        "README.md",
        "README.ru.md",
        "README.de.md",
        "tests/test_dashboard_views.py"
      ],
      "review": "нет",
      "model": null,
      "fingerprint": "67b50270e08b2de24afa9b81f089ce2e3ce6e4909c5ae302392a9965eecde78f",
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
    "found": 25,
    "fixed": 21,
    "deferred": 4,
    "items": [
      "бриф: порядок запуска после PR 81, режим/глубина — условия запуска, не содержимое спецификации",
      "бриф: слепая приёмка по брифу — процесс прогона (R31 в §4.9)",
      "бриф: источники (коммиты апстрима) — справка, не требование",
      "бриф: свежая ветка от main — уже выполнено (feat/upstream-port-opus)"
    ]
  },
  "concerns": [],
  "blockingFindings": [],
  "blind": null,
  "beats": [
    "2026-11-08T14:16:44+01:00",
    "2026-11-08T14:17:00+01:00",
    "2026-11-08T14:17:01+01:00",
    "2026-11-08T14:17:06+01:00",
    "2026-11-08T14:17:35+01:00",
    "2026-11-08T14:19:17+01:00",
    "2026-11-08T14:19:23+01:00",
    "2026-11-08T14:19:55+01:00",
    "2026-11-08T14:21:53+01:00",
    "2026-11-08T14:27:30+01:00",
    "2026-11-08T14:29:07+01:00",
    "2026-11-08T14:30:45+01:00",
    "2026-11-08T14:30:46+01:00",
    "2026-11-08T14:30:47+01:00",
    "2026-11-08T14:30:56+01:00"
  ],
  "rev": 16,
  "waiting": null,
  "waits": [
    {
      "kind": "briefing",
      "from": "2026-11-08T14:17:35+01:00",
      "to": "2026-11-08T14:19:17+01:00"
    },
    {
      "kind": "briefing",
      "from": "2026-11-08T14:19:55+01:00",
      "to": "2026-11-08T14:21:53+01:00"
    }
  ],
  "log": [
    {
      "t": "2026-11-08T14:16:44+01:00",
      "k": "init"
    },
    {
      "t": "2026-11-08T14:17:01+01:00",
      "k": "stage",
      "id": "manifest",
      "act": "start"
    },
    {
      "t": "2026-11-08T14:17:06+01:00",
      "k": "stage",
      "id": "briefing",
      "act": "start"
    },
    {
      "t": "2026-11-08T14:17:35+01:00",
      "k": "ask",
      "kind": "briefing",
      "note": "раунд 1: подтверждение, риск-таски Opus, момент вопроса, цена"
    },
    {
      "t": "2026-11-08T14:19:17+01:00",
      "k": "answered",
      "kind": "briefing"
    },
    {
      "t": "2026-11-08T14:19:23+01:00",
      "k": "gate",
      "g": "G1",
      "ok": false,
      "open": 32,
      "total": 32
    },
    {
      "t": "2026-11-08T14:19:23+01:00",
      "k": "stage",
      "id": "spec",
      "act": "start"
    },
    {
      "t": "2026-11-08T14:19:55+01:00",
      "k": "ask",
      "kind": "briefing",
      "note": "две вещи: Opus против «Договорились», вопрос про остатки прошлой сборки"
    },
    {
      "t": "2026-11-08T14:21:53+01:00",
      "k": "answered",
      "kind": "briefing"
    },
    {
      "t": "2026-11-08T14:27:30+01:00",
      "k": "gate",
      "g": "G1",
      "ok": true,
      "open": 0,
      "total": 33
    },
    {
      "t": "2026-11-08T14:27:30+01:00",
      "k": "stage",
      "id": "spec",
      "act": "start"
    },
    {
      "t": "2026-11-08T14:29:07+01:00",
      "k": "gate",
      "g": "G2",
      "ok": true,
      "found": 25,
      "fixed": 21,
      "deferred": 4
    },
    {
      "t": "2026-11-08T14:30:45+01:00",
      "k": "stage",
      "id": "plan",
      "act": "start"
    },
    {
      "t": "2026-11-08T14:30:46+01:00",
      "k": "tickets",
      "n": 4
    },
    {
      "t": "2026-11-08T14:30:47+01:00",
      "k": "gate",
      "g": "G3",
      "ok": true,
      "problems": 0
    },
    {
      "t": "2026-11-08T14:30:56+01:00",
      "k": "tier",
      "v": "T1"
    }
  ],
  "reqList": [
    {
      "id": "R01",
      "text": "«Портировать нужно не копированием: наш ap.py разошёлся с апстримом (подписанные гейты, блокеры, маршрутизация). Каждый фикс переписывается под наш код с одним регрессионным тестом (как в порте 2.2.1, коммиты a436a78).»",
      "status": "in-ticket"
    },
    {
      "id": "R02",
      "text": "«A1. ap.py отказывает в третьем ticket NN repair и третьем ticket NN retry (лимит 2 на каждый). Отказ даёт команду, а не только текст фазы.»",
      "status": "in-ticket"
    },
    {
      "id": "R03",
      "text": "«A2. Упавший таск (failed) снова идёт в работу только через ticket NN reset --by-user \"<цитата пользователя>\". Цитата пишется в таск (reopenedByUser) и в журнал, счётчики repairs и retries обнуляются. reset без --by-user на упавшем таске о…",
      "status": "in-ticket"
    },
    {
      "id": "R04",
      "text": "«A3. Слепая приёмка: не больше двух кругов за прогон (проверка, таск F2, одна перепроверка). Счётчик blindRounds, сбрасывается в reopen. Третий blind отказывает с подсказкой add report для остатка.»",
      "status": "in-ticket"
    },
    {
      "id": "R05",
      "text": "«A4. В phases/4-plan.md: таски, которые только проверяют («подтвердить готовность», «прогнать полную проверку»), запрещены.»",
      "status": "in-ticket"
    },
    {
      "id": "R06",
      "text": "«A5. В phases/5-repair.md: сбой окружения (таймаут, не грузится нативный модуль, порт, неработающий сервис, путь только на этой машине) это fail с вопросом пользователю, а не ремонт.»",
      "status": "in-ticket"
    },
    {
      "id": "R07",
      "text": "«A6. В phases/8-final.md: «один круг исправлений, потом отчёт, третьего взгляда нет».»",
      "status": "in-ticket"
    },
    {
      "id": "R08",
      "text": "«A7. После сжатия контекста оркестратор перечитывает и 5-repair.md (правка в SKILL.md).»",
      "status": "in-ticket"
    },
    {
      "id": "R09",
      "text": "«B1. G1 идёт за манифестом: вычисляется функцией от таблицы манифеста при каждой записи, а не только на этапе спецификации. Правка манифеста после spec не оставляет G1 красным или зелёным по устаревшим данным. (Именно это остановило R22d н…",
      "status": "in-ticket"
    },
    {
      "id": "R10",
      "text": "«B2. ticket NN done без --commit (и без ранее записанного коммита) отказывает. Отказ git при коммите это сбой машины: ticket NN fail --note, вопрос пользователю, не ремонт.»",
      "status": "in-ticket"
    },
    {
      "id": "R11",
      "text": "«B3. finish отказывает при: незакрытом G1–G4, таске не в done, таске без коммита, коммите не из HEAD. Это добавляется к уже существующим проверкам блокеров, подписи и отпечатка плана, а не заменяет их.»",
      "status": "in-ticket"
    },
    {
      "id": "R12",
      "text": "«B4. Сдать с отказами можно только finish --result \"…\" --by-user \"<цитата>\". В state.js пишется landedWith, строка реестра «сдан с оговорками», шапка дашборда «Сдано с оговорками».»",
      "status": "in-ticket"
    },
    {
      "id": "R13",
      "text": "«B5. Расхождения слепой приёмки, оставшиеся после двух кругов, сдаются с той же оговоркой, а не блокируют finish.»",
      "status": "in-ticket"
    },
    {
      "id": "R14",
      "text": "«B6. В preflight git проверяется до брифинга (git add -- .gitignore или эквивалент без побочных эффектов). Отказ записи останавливает прогон сразу, с понятной причиной, а не на первом таске.»",
      "status": "in-ticket"
    },
    {
      "id": "R15",
      "text": "«B7. Дашборд (phases/dashboard-template.html) показывает «Сдано с оговорками». Живые проекты обновляются dashboard_upgrade.py, .autopilot/dashboard.html не копируется вручную.»",
      "status": "in-ticket"
    },
    {
      "id": "R16",
      "text": "«C1. По умолчанию ничего не меняется: Opus выключен, поведение и тесты «Opus не проходит» остаются, пока нет подтверждения.»",
      "status": "in-ticket"
    },
    {
      "id": "R17",
      "text": "«C2. Включение явное и на прогон: на этапе плана Autopilot показывает список тасков, где Opus уместен, и цену, пользователь отвечает да или нет. Ответ записывается в state.js вместе с цитатой, подписанно, как гейты.»",
      "status": "in-ticket"
    },
    {
      "id": "R18",
      "text": "«C3. В роутере отдельный уровень выше «сильной». Выбирается только для тасков с высоким риском (безопасность, конкурентность, миграции данных) или с явной пометкой в файле таска, и только при подтверждении по C2.»",
      "status": "in-ticket"
    },
    {
      "id": "R19",
      "text": "«C4. Кандидаты помимо рискованных тасков: ремонт, дважды вернувшийся с ревью; общее ревью ветки на большом диффе.»",
      "status": "in-ticket"
    },
    {
      "id": "R20",
      "text": "«C5. Нужно согласовать с claude_agent_guard.py, claude_attest.py и закреплёнными профилями в .claude/agents/: что в attest считается допустимой моделью, как guard проверяет подтверждение.»",
      "status": "in-ticket"
    },
    {
      "id": "R21",
      "text": "«C6. Тесты переписываются из «Opus не проходит» в «Opus не проходит без подтверждения, и проходит только для помеченного таска при подписанном подтверждении». Отдельный тест на поддельное подтверждение.»",
      "status": "in-ticket"
    },
    {
      "id": "R22",
      "text": "«C7. Дашборд и отчёт показывают, какие таски шли на Opus и сколько это стоило по measure-run.py.»",
      "status": "in-ticket"
    },
    {
      "id": "R23",
      "text": "«Все 669 тестов остаются зелёными, добавленные тесты идут вместе с кодом.»",
      "status": "in-ticket"
    },
    {
      "id": "R24",
      "text": "«Требование из manifest.md снимает только пользователь.»",
      "status": "in-ticket"
    },
    {
      "id": "R25",
      "text": "«Секреты не запрашиваются и не пишутся.»",
      "status": "in-ticket"
    },
    {
      "id": "R26",
      "text": "«Поведение по умолчанию (без --by-user, без подтверждения Opus) в рабочих прогонах не меняется, кроме новых отказов из A1, A3, B2 и B3: они и есть смысл брифа.»",
      "status": "in-ticket"
    },
    {
      "id": "R27",
      "text": "«state.js пишется только через state_io.py; харнессы, копирующие ap.py, копируют state_io.py, process_containment.py, run_log.py.»",
      "status": "in-ticket"
    },
    {
      "id": "R28",
      "text": "«README и документацию правим только там, где поведение изменилось (CHANGELOG.md, docs/autopilot/, три языка там, где нужно).»",
      "status": "in-ticket"
    },
    {
      "id": "R29",
      "text": "«python3 -m unittest discover -s tests зелёный на 3.11 и 3.13.»",
      "status": "in-ticket"
    },
    {
      "id": "R30",
      "text": "«По одному регрессионному тесту на каждый пункт A1–A3, B1–B5 и C6.»",
      "status": "in-ticket"
    },
    {
      "id": "R31",
      "text": "«Слепая приёмка по этому брифу, не по спецификации.»",
      "status": "in-ticket"
    },
    {
      "id": "R32",
      "text": "«В CHANGELOG.md запись о порте и об Opus, с честной пометкой, что экономия Opus-субагентов не измерена.»",
      "status": "in-ticket"
    },
    {
      "id": "G01",
      "text": "«Опус должен использоваться для суперсложных или суперответственных задач, или где, по твоему мнению, Zoned не справится.»",
      "status": "in-ticket"
    }
  ],
  "gates": {
    "G1": {
      "ok": true,
      "at": "2026-11-08T14:27:30+01:00",
      "open": 0,
      "total": 33
    },
    "G2": {
      "ok": true,
      "at": "2026-11-08T14:29:07+01:00",
      "found": 25,
      "fixed": 21,
      "deferred": 4
    },
    "G3": {
      "ok": true,
      "at": "2026-11-08T14:30:47+01:00",
      "problems": 0
    }
  },
  "result": null,
  "gateMark": "075edaa32264ebc925f7ec2fc549a2a7aa56c34b22c9b77395aeb0faa1558b3d",
  "skillVersion": "2.7.0",
  "planContractDigest": "c445d2803ad8f12e457664c37a13fe1198978e2d0db7b695b463464bb2b119db",
  "planValidationDigest": "b62b5bbfcf226ab280799de970a595c554d25fe4dfaec25fcb7884e9fdbbee97"
}
