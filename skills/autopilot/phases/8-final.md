# Phase 8 — Acceptance

`ap.py stage final`. Three isolated subagents, one question each. The blind checker and the ADR agent go out **in one message**; the memory agent after the blind checker returns — it needs the commands the checker proved.

**Model authorization applies to all three.** For each, write a small role-specific Markdown routing brief outside `tickets/` and call `model_router.py` with verified host capabilities (and explicit six-factor scores if needed). Never spawn without a ready verdict or let the host inherit Astra/Fable from the main session. Memory/ADR normally need a cheap model; blind acceptance may need balanced or strong by risk.

| Agent | Question | Receives | Never receives |
|---|---|---|---|
| blind checker | что из брифа сделано | the brief files, the repository | `spec.md`, `manifest.md`, tickets |
| ADR *(T2+)* | почему сделано именно так и как здесь называются вещи | `spec.md`, `manifest.md`, `interfaces.md`, `notes.md` | the repo |
| memory | как этим пользоваться завтра | the repo, the memory file, `interfaces.md`, the tier, the commands the checker ran | `spec.md`, tickets |

## 1. Blind acceptance — gate G4

Every earlier check measured the build against the spec — your paraphrase of the brief. **So this check does not get the spec.**

It receives every `*-brief.md` in `dir`, oldest first, **whole, `## Дополнения` included**, and the repository. `.autopilot/` is committed and sits right there, so **the prohibition goes in the prompt**:

> Прочитай приложенные файлы брифа — это задача, которую поставил заказчик,
> по порядку дат. Разделы «Дополнения» — сказанное по ходу работы, часть задачи
> наравне с основным текстом; при расхождении верно более позднее. Не открывай
> `.autopilot/` — ни спецификацию, ни манифест, ни таски. Не вызывай скиллы
> и не запускай своих агентов. Ничего не отправляй наружу: ни писем, ни
> сообщений реальным людям, ни оплат, ни публикаций — если сценарий до этого
> доходит, остановись на шаге перед отправкой и запиши, что дальше не проверял.
>
> **Склонируй репозиторий во временную папку** (`git clone <репозиторий> <tmp>`)
> и работай там: поставь зависимости с нуля по тому, что лежит в репозитории.
> Если для запуска нужен `.env`, скопируй его в клон, не открывая. Всё, что
> в клоне не поднимается, а в рабочей папке поднималось бы, — находка:
> незаписанная зависимость, незакоммиченный файл, шаг, который знает только эта машина.
>
> **Запусти проект** и пройди основной сценарий так, как прошёл бы заказчик.
> Не поднимается или сценарий обрывается — главная находка, первым пунктом.
> Запустить нельзя вообще (нужен аккаунт, ключ, внешний сервис) — скажи прямо,
> что помешало, и не выдавай чтение кода за проверку.
>
> По каждому требованию из брифа: реализовано / частично / нет — и одна строка,
> где это видно. Выполнено формально, а по сути не работает (данные
> сохраняются, но пользователю не показываются) — «частично».
>
> Отдельно верни **команды, которыми ты поднимал проект, и их результат** — дословно:
> их ждёт агент, который пишет память проекта.
>
> Не оценивай качество кода, не предлагай улучшений, не ищи оправданий — только факт.

**Then compare its verdict with the manifest:**

| Manifest | Blind | Meaning |
|---|---|---|
| `done` | реализовано | agreed |
| `done` | **частично / нет** | 🔴 **drift** — the manifest is wrong. A ticket, or a line in the report; never an edit of your own |
| `placeholder` | частично | expected — confirm the stub is visible, not an invented fact |
| `dropped` / `deferred` | нет | expected — in the report as not built |
| — | реализовано, но не из брифа | scope that grew without a parent — reported |

Record it in one call — `ap.py blind checked=N matched=M --mismatch "…" --mismatch "…"`, one `--mismatch` per 🔴. Hiding a drift is the failure. **A build nobody has launched is a build nobody has seen work** — if it cannot run here at all, that goes to «Что нужно от тебя», not into the accepted column.

## 2. Memory and ADRs

**Read `phases/9-memory.md` before spawning them** — Moments 3 and 4 there are their whole brief, glossary included. When the memory file is the user's own, the memory agent writes `memory-proposal.md` instead of touching it.

## 3. The final report

Run the check once more first, truncated, and record it — `ap.py tests N/M`. Then write in the user's language, plain, no jargon.

**Build it from the files, re-read now, never from memory** — your context is now the most polluted of the run: a `deferred` requirement turns «done», a placeholder vanishes, an unordered `A##` looks asked for.

| Section | Read from |
|---|---|
| Решения, принятые за тебя *(full: first in the report)* | `manifest.md` — every `ASSUMPTION` |
| Готово | **the blind checker's verdict**, not the manifest's `done` rows |
| Что нужно от тебя | `placeholder` rows + `state.js` → `debt` |
| Что не вошло | `deferred` and `dropped` rows, with their quotes |
| Что я добавил сверх заказанного | `state.js` → `additions`, checked against the spec's `A##` |
| Что пошло не по плану | every `D##` row, every failed ticket |
| Что осталось после ревью | `state.js` → `report` |
| Открытые вопросы | `state.js` → `blind`, and `coverage` → `items` that ended up not built |
| Память проекта *(only when the file is the user's)* | `memory-proposal.md` — one question: «Предлагаю дополнить твой `CLAUDE.md`: N пунктов — применить?»; in full, only a line naming the file |
| Запустить / Где что лежит | `memoryFile`, `briefFile`, the commands the memory agent verified |

```markdown
## Готово

<Что теперь работает — 3–6 строк обычным языком, от лица пользователя.>

**Запустить:**
    npm install && npm run dev
Открыть http://localhost:3000

## Что нужно от тебя

1. Впиши в `.env` — `TELEGRAM_BOT_TOKEN`, `GOOGLE_SHEETS_ID`. Образец — `.env.example` рядом.
2. Замени заглушки: цены и тексты писем. Сейчас там видимые метки `[ВПИШИ]`, не выдуманные значения.

## Что не вошло

| Что | Почему |
|---|---|
| Уведомления на SMS | ты сказал «SMS не надо, только телега» |

## Что я добавил сверх заказанного  ← таблица «Что добавил | Ради чего»
## Что пошло не по плану  ← таблица «Что не сработало | Как сделано»

## Открытые вопросы

<Расхождения слепой приёмки — прямо, без смягчения.>

## Где что лежит

- Описание проекта для следующего раза — `AGENTS.md` в корне
- Что осталось и о чём договорились — `.autopilot/PROGRESS.md`: мелкие правки можно делать в обычной сессии, она прочитает его сама
- Почему сделано именно так — `docs/adr/`, словарь проекта — `CONTEXT.md` (если проект крупный)
- Прогресс и цифры — `.autopilot/dashboard.html`
- Твоя задача, требования, спецификация — `.autopilot/<папка сборки>/`
```

- **Заглушки и пустые переменные — обязательный раздел**, даже пустой: «всё заполнено».
- **«Что не вошло» пишется всегда**, даже когда вошло всё — одной строкой.
- **Секреты — только именами.**
- **Не приукрашивать.** Упавшее, недоделанное, найденное расхождение — прямо, с тем, что нужно для починки.
- Без диффов, имён файлов кода и названий тестов. Any other empty section is omitted.

## 4. The progress file

`.autopilot/PROGRESS.md` — where the work stands at landing: the next run reads it first (`phases/0-preflight.md` §5), a plain session because the memory file says to (`phases/0-memory.md`). **You write it, from files re-read now**, never from memory of the dialogue. Rewritten whole at every landing; preflight already read the previous one into `carried.md`.

```markdown
<!-- autopilot:progress -->
# <Название проекта> — что осталось

Последняя сборка: `.autopilot/<папка>/` — <итог одной строкой>.

## Договорились — не пересматривать

- «SMS не надо, только телега» — R03, отказ пользователя

## Не доделано

- Корзина — отложена: «корзину потом» (R08)

## Известные баги

- Даты в уведомлениях в двух форматах — `src/notify.ts`

## Правки без автопилота

<!-- дата — что — почему; пишет обычная сессия, следующая сборка разбирает -->
```

| Section | From |
|---|---|
| Договорились | `dropped` rows with their quotes; lasting preferences from the briefs' `## Дополнения`; assumptions the user confirmed; `carried.md` → «Договорились» still true. **Not** what an ADR already holds — a pointer at most |
| Не доделано | `deferred` rows with their quotes, failed tickets, `coverage` items not built; from `carried.md`, everything this run did not take |
| Известные баги | 🔴 blind mismatches, `state.js` → `concerns` and `report` left unfixed; from `carried.md`, those this run did not fix |
| Правки без автопилота | empty: each entry from `carried.md` moved to «Договорились» or «Не доделано», or is gone (a fix git holds needs no line) |

Placeholders and empty variables are not repeated here (they are in «Что нужно от тебя» and `.env.example`). An empty section reads «—». One thought per line, with the requirement number where there is one; the whole file under about sixty lines — past that it is a tracker backlog, and the report says so in one line.

## 5. Landing

**Before landing:** `finish` refuses any open `blockingFindings` (including those from `ticket NN repair --note`), legacy `repairFindings` without blocker reconciliation, and resolved fixes whose commits left Git history. Resolve with `ap.py blocker resolve --id BNN --commit SHA --tests N/0 --note "independent re-review verdict"` — only when the fix commit, passing tests and independent review really exist. Nonblocking `concerns` and `report` entries stay reportable, not blocking. `finish` also checks requirements and tickets against the verified G3 plan and all gates, and independently revalidates the plan. If it reports a stale or missing G3 contract (including an unfinished 2.3-dev run resumed from before this check existed), run `ap.py check-plan`, investigate unowned/duplicate requirements or changed tickets, and redo G1/G2/G4 if the plan changed. Never just rewrite `state.js` or mark a new requirement `done` to bypass this gate.

In this order, so the report names paths that exist:

1. The memory file (or its proposal), the ADRs, the glossary and the progress file are written.
2. `python3 .autopilot/ap.py finish --result "<одна строка: что теперь есть>"` — closes every stage, sets `finishedAt`, renames `<dir>--wip` to `<dir>` with `git mv`, closes the run's row in `.autopilot/README.md`, and stops the server twelve seconds later, after the page fetched the final picture. A `!` line about the rename (name taken, index dirty): leave it — the suffix is cosmetic.
3. **The final commit** — exactly what this skill wrote since the plan commit, never the rest of the tree, where the user may have work of their own:

   ```bash
   git add -A -- .autopilot AGENTS.md CLAUDE.md docs/architecture.md docs/adr CONTEXT.md GLOSSARY.md .env.example .gitignore \
     && git commit -qm "Autopilot: сборка сдана" --trailer "Autopilot-Run: <папка>" -- .autopilot AGENTS.md CLAUDE.md docs/architecture.md docs/adr CONTEXT.md GLOSSARY.md .env.example .gitignore
   ```

   Omit from both lists any missing path, and the memory file if it is the user's own. **The subject stays exactly «Autopilot: сборка сдана»** — the next run and every plain session find the landing by it. `git status` afterwards: a changed file outside everything any ticket owned is not committed by you — it goes in the report as «осталось незакоммиченным».
4. The report.

The dashboard freezes the final numbers inside the page and reopens by double-click. Say nothing about any of this.
