# Phase 3 — Spec

`ap.py stage spec`. Turn the manifest and the answers into `.autopilot/<dir>/spec.md` — the contract for executors and reviewers. The user sees two lines; the file is the spec.

**An existing codebase is explored first.** When Phase 0 found code, one subagent on a verified cheaper permitted model reads the repository once and writes `.autopilot/<dir>/notes.md`: where things live, conventions, the commands that run it, and **the exact names of the entities, fields and functions the work will touch** — so boundaries match the existing code and two parallel tickets do not call one field `blockedSince` and `blockedOn`. Every executor reads it instead of exploring.

**After a landed run, `carried.md` comes in twice** (`phases/0-preflight.md` §5). Its «Изменено после сборки» goes to the exploring subagent with the brief «эти места менялись после прошлой сборки — опиши их по коду, как они есть сейчас». Its «Договорились» goes into `interfaces.md` under the project rules, word for word: a spec section that would break one is rewritten or, if the new brief asks for exactly that, put to the user as one line — never decided by you.

**This phase does not reopen the interview.** Anything unresolved becomes a `placeholder`. One narrow exception: a genuine fork the briefing missed, where the branches are different projects — ask it once, in one line, with a recommendation. In full there is no exception: decide it and record the `ASSUMPTION`.

## Depth — the brief is a silhouette

The user describes the happy path — not the empty list, the dropped network, the double submit, the first launch with no data. **Working those out is this phase's main value**; a spec restating the brief in tidier words produced nothing.

How far is the user's setting:

| Depth | The depth pass | `A##` new capabilities |
|---|---|---|
| **strict** | only *Wrong input* and *Failure*, and only where the requirement plainly breaks without them | forbidden — not written at all |
| **normal** | by judgement — the dimensions that plainly matter for that requirement | allowed, with a parent and in proportion |
| **deep** | every dimension of every requirement, or an explicit «не применимо» | encouraged, same limits |

| Dimension | The question the brief never answered |
|---|---|
| **First run** | what does this look like before any data exists? |
| **Empty** | zero items, zero results — what is on screen, and what invites the next step? |
| **Wrong input** | what does the user see, in their language, and what survives of what they typed? |
| **Failure** | network, service, disk — what breaks, what is said, what is retried, what is lost? |
| **Interruption** | closed halfway, refreshed, sent twice — resume, restart or duplicate? |
| **Growth** | ten items versus ten thousand — what has to change, now or later? |
| **Boundaries** | who may do this, and what happens to someone who may not? |
| **Aftermath** | where does the result go, who learns about it, can it be undone? |

Each answer becomes an `R##.n` story with its own acceptance line; the count is an output — padding is as bad as skipping.

**Two roads.** *Propose* when the answer is the user's (a briefing question). *Decide* craft — error text, retry policy, limits, defaults — write it in and say so in the summary. In full, everything is decided and listed in the report; at strict, nothing is offered beyond what was asked.

## Keeping depth attached

| Mark | Origin | Rule |
|---|---|---|
| `R##` | the brief | untouchable |
| `R##.n` | **deepening** a brief requirement | uncapped — the main work of the phase |
| `G##` | **the user's own words**, later | untouchable, like `R##` |
| `A##` | a **new capability** the brief never implied | names a parent `R##` |
| `D##` | a constraint the **build** proved | only via `phases/5-repair.md` |

Retry, resume and validation for «принимает заявки» are `R01.n`; a loyalty programme is `A`. At every depth:

- **Parenthood** — every `A##` names the `R##` it serves; an orphan is a different project and is cut.
- **Proportion** — `A` stories never outnumber `R` + `G` combined.
- **Precedence** — tickets closing `R` fly before tickets closing only `A`, so a cut-short run leaves your additions unfinished, never the user's request.

## Boundaries — decided here, written to `interfaces.md`

Fresh-context executors build one project only if **module boundaries are already decided** — else ticket 01 decides them from an eighth of the задача.

For every unit: **what it owns**, **what it exposes** (signatures other units call — names and shapes, not implementations; names in English, never transliterated Russian, unless the existing code does otherwise), **what it hides**. Then the **test seams** — a subset of those boundaries, the fewer the better, existing ones preferred. Boundaries follow the depth pass, not the requirement list; a boundary no ticket crosses is not a boundary; a few deep modules beat many shallow ones.

**Write this straight into `.autopilot/<dir>/interfaces.md`** under «Границы, решённые в спецификации» (every executor reads it first); the spec keeps only a pointer. In manual this is the part of the spec gate worth discussing — expensive to change later.

## The file

**A small product** (one surface, one feature; Phase 4's T0/T1) gets a short spec: Задача; Решение with one line per live requirement saying what the user gets, depth included; Решения по реализации; Вне рамок; Открытые места. No stories table — acceptance criteria are written once, in the ticket.

**Otherwise:**

```markdown
# Спецификация: <название>

## Задача
Проблема пользователя его словами — от лица того, кто ей страдает.

## Решение
Что у него появится, когда всё будет готово. Без техники.

## Истории
Каждое живое требование — хотя бы одна история; проработка и добавления — свои строки.

| # | Метка | История | Приёмка |
|---|-------|---------|---------|
| 1 | R01 | Как клиент, я оставляю заявку боту, чтобы не звонить | бот принял и подтвердил |
| 2 | A01 → R01 | …и получаю номер заявки, чтобы на него ссылаться | номер в подтверждении |

## Решения по реализации
Стек, схема данных, контракты, внешние сервисы — каждое с одной строкой «почему».
Без путей и кода, кроме структуры, которую код выражает точнее прозы.

## Границы и швы
См. `interfaces.md`.

## Вне рамок
| Требование | Почему не сейчас |
|---|---|
| R06i — админка | заявки видны в таблице; отдельный экран — следующий заход |

## Открытые места
Каждый `placeholder`: что стоит заглушкой, где, что нужно от пользователя.
```

Which section covers which requirement lives in the manifest's «Где» column only.

**Vocabulary:** if `CONTEXT.md`, `GLOSSARY.md` or `docs/adr/` exist, the spec uses their terms, not synonyms; a contradiction with a recorded decision is said out loud.

## Gate G2 — before leaving

**1. Your own pass.** Every manifest row: `open` → `in-spec` with its section in «Где», or → `deferred` with its «Вне рамок» line. **Zero `open`**, or the spec is incomplete — write the missing section.

**2. The independent coverage check** — you cannot see what you did not write. After an approved routing decision (verified provider capabilities; restricted models forbidden), spawn a subagent with **exactly the named files** — every `*-brief.md` in `dir`, oldest first, and `spec.md` — never the manifest, the conversation or a summary; and forbid looking further — the files sit in `.autopilot/` beside the manifest:

> Открой только названные файлы и больше ничего — ни `manifest.md`,
> ни остальное содержимое `.autopilot/`. Твоя ценность в том, что ты
> не видел, как автор спецификации читал задачу. Не вызывай скиллы
> и не запускай своих агентов.
>
> Файлы брифа — задача словами заказчика, по порядку дат. Разделы «Дополнения»
> в них — сказанное позже, и при расхождении верно более позднее.
> Последний файл — спецификация.
>
> Найди всё, что заказчик просил, а спецификация не покрывает: цитата из брифа
> и одна строка, чего нет. Отдельно — покрытое наполовину, так что по нему нельзя
> собрать. Отдельно — то, чего в брифе не было, а в спецификации есть.
>
> Не оценивай качество и не предлагай улучшений. Только факт расхождения,
> по строке на находку. Расхождений нет — так и скажи.

Act on it before leaving: *missing* or *half-covered* → write what is missing; *not in the brief* → attach to a parent as `A##` or cut. Record it in one call — `ap.py coverage found=N fixed=N deferred=N --item "…"` with an `--item` for each finding not fixed in the spec. A finding here costs a paragraph; at G4 it costs the build.

## Showing it

**full, semi, interview** — two lines: what will be built, what deliberately will not, where the file is. Then start; in interview too — they chose questions, not gates.

**manual** — the spec is a gate: `ap.py ask spec`, show it in full, wait for an explicit «ок», rewrite on every objection. Silence is not agreement; nor is work already started.
