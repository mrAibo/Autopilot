# Phase 9 — Project memory

The file the **next** session reads first. Chosen in Phase 0 (`phases/0-memory.md`); this file is read in Phase 5 (Moment 2) and Phase 8 (Moments 3, 4).

| File | Answers | Lifetime |
|---|---|---|
| `.autopilot/<dir>/` | what was promised and delivered **in this run** | history |
| `interfaces.md` | what earlier tickets built, for later ones | dies with the run |
| the memory file | what an agent needs to work here **tomorrow** | present tense |
| `docs/adr/` | **why** it is this way, and what was rejected | past tense on purpose |
| `CONTEXT.md` | what the project's words **mean**, and which synonyms to avoid | present tense, no code |
| `.autopilot/PROGRESS.md` | what is left **open** (not done, known bugs, what the user settled) and fixes made without Autopilot | rewritten at each landing (`phases/8-final.md`) |

Everything in the memory file must be true of the repository as it stands, not of the plan.

**Memory is how to work here; the progress file is where the work stands.** Trap, command, pointer → memory. Unfinished work, a shipped bug, «пользователь сказал: без SMS» → progress file, which memory points to and never retells.

## Whose file it is

`memoryOwner` in `state.js`:

- **`autopilot`** — its content lives between `<!-- autopilot:start -->` and `<!-- autopilot:end -->`; updating replaces what is between them. Text outside them is the user's, never touched. Markers missing but Autopilot's sections recognisably there → wrap them, never append a second copy.
- **`user`** — nothing is written into the file during the run. Moments 2 and 3 write `.autopilot/<dir>/memory-proposal.md` instead; the file changes only on the user's word.

## Moment 2 — during the build

Only facts that cost something to discover, a line each: the real check command and how to run one test file; a trap that ate time (ordering dependency, version pin, platform quirk); a new variable in `.env.example`; a decision the next ticket must not re-litigate. Most tickets add nothing.

Never: generic advice, restated names, commit history, standard-technology explanations, anything `interfaces.md` holds during the run.

One line appended: between the markers (Autopilot's file) or to `memory-proposal.md` (the user's).

## Moment 3 — the description (Phase 8)

**A subagent on a verified cheaper permitted model (route before dispatch), launched with the blind acceptance**, neither seeing the other. It receives the repository, the current memory file, `interfaces.md`, the tier, and the commands already verified: your full-suite run and the blind checker's commands. **Not `spec.md`, not the tickets** — memory from the plan documents intentions, and the next session trusts it.

**Pointers and traps, not a retelling** — no directory tree, no paraphrase of `package.json`, no «what a module does»: every future session reads every line, and those go stale first.

| Section | What |
|---|---|
| Заголовок | one line: what this is, for whom |
| Команды | install, run, check (tests + types + lint), one test file — every one verified |
| Где что | 3–8 pointers to entry points and the places most edits land — not a tree |
| Подводные камни | what is not obvious and has already bitten someone |
| Окружение | variable names and what each is for — **never values** |
| Как здесь работает Autopilot | from the skeleton, unchanged |

**At tier T2+ the architecture goes to `docs/architecture.md`** — data flow, module boundaries, settled conventions, from `interfaces.md` minus per-ticket framing — with one pointer line from the memory file.

Its brief:

> Опиши проект так, чтобы агент, впервые открывший этот репозиторий, начал
> работать без разведки. Источник — код, который ты видишь, и приложенный
> `interfaces.md`; больше ничего в `.autopilot/` не открывай. Не вызывай скиллы
> и слэш-команды и не запускай своих агентов.
>
> Пиши указателями, строка на мысль: где что лежит, как запустить, где
> больно. Не пересказывай очевидное из имён и известные технологии.
> Каждая команда должна запускаться копипастом, каждый путь — существовать.
> Чего в коде нет — того раздела нет.
>
> Пиши только между метками `<!-- autopilot:start -->` и `<!-- autopilot:end -->`;
> всё вне их не трогай. <Для T2+: архитектуру — в `docs/architecture.md`,
> в памяти — одна строка-указатель на него.> <Если файл пользователя: не трогай
> его вовсе, а напиши предложение в `.autopilot/<папка>/memory-proposal.md`.>
>
> Итог — одна-три строки: какие файлы записаны, без содержимого.

Before the block is written:

1. **Commands are verified** — install, run, check: what you were handed counts as run (name it); verify only what nobody covered. A failing command does not go in.
2. **Every path exists.**
3. **No secret values** — the redaction gate from `phases/1-manifest.md` applies here too.
4. **Length fits the tier** — a landing page gets no two-page memory file.

### When the file is the user's

The same agent writes `memory-proposal.md` instead: what is missing (commands, variables, traps, pointers) and what in their text is now false, each a ready-to-paste line. **The «Правка без автопилота» and «История git» subsections from `phases/0-memory.md` are always among them** when their file lacks them — else plain sessions never find `PROGRESS.md` and their commits trace to no requirement. Nothing else.

In semi, interview and manual the report asks once, at the end: «Предлагаю дополнить твой `CLAUDE.md`: 4 пункта — команды запуска и две переменные `.env`. Применить?» **In full nothing is asked**; the report names the file. On a yes, the additions go into a marked Autopilot block at the end of their file; a line of their own text changes only as they approved it.

## Moment 4 — the ADRs and the glossary (Phase 8, tier T2+)

ADRs answer «почему так» — what was chosen, what was rejected and why; `spec.md` dies with the run, so what deserves to survive goes to `docs/adr/`.

Sources, only: **every `D##` row** (the plan proved wrong — most valuable); **load-bearing implementation decisions** (data model, module boundaries, an external service — anything whose reversal means rebuilding). Vocabulary goes to the glossary. Not: a decision with no alternative, what a linter or framework decided, the obvious default. 3–6 files on T2, 5–12 on T3.

**A subagent, in parallel with the other two, routed to a verified cheaper permitted model.** It receives `spec.md`, `manifest.md`, `interfaces.md` and `notes.md` when it exists — **not the repository**: it documents decisions and words, not code.

> По приложенным спецификации, манифесту, `interfaces.md` и `notes.md` напиши по одному ADR на каждое решение,
> которое дорого отменять, и на каждую строку `D##`. Не вызывай скиллы
> и не запускай своих агентов.
>
> Формат — `docs/adr/NNNN-<краткое-название>.md`, нумерация с `0001`, по файлу
> на решение. Внутри четыре раздела и больше ничего:
>
> **Контекст** — что было известно на момент решения. Одна-две строки.
> **Решение** — что решили, в настоящем времени: «Заявки хранятся в SQLite».
> **Почему** — и, главное, что рассмотрели и отвергли, и чем именно
> отвергнутое не подошло.
> **Последствия** — с чем теперь придётся жить, включая неприятное.
>
> Для `D##` контекст — что план предполагал, решение — что код доказал.
> Не пиши ADR на решение без альтернативы, не пересказывай спецификацию
> и не описывай код — ты его не видел.
>
> Затем словарь — `CONTEXT.md` в корне. Только слова этого проекта, которые
> новичок назовёт иначе или поймёт не так: «заявка», «смена», «бронь» — да;
> «пользователь», «API», «таймаут» — нет. Термин — на языке брифа, тем словом,
> которым его называют спецификация и код (`notes.md`, `interfaces.md`), а не
> синоним. Таких слов нет — файла нет. Формат:
>
> ```
> <!-- autopilot:glossary -->
> # <Название проекта>
>
> <Одна-две строки: что это за область.>
>
> ## Язык
>
> **Заявка**:
> Обращение клиента, которое ждёт ответа менеджера.
> _Избегать_: запрос, тикет, лид
> ```
>
> Определение — одна-две строки: что это, а не что с ним делает код.
> Разные слова для одного понятия — выбери одно, остальные — в «_Избегать_».
> Без путей, полей и стека.
>
> Итог — список записанных файлов, без содержимого.

If `docs/adr/` exists, **continue its numbering and format**; never renumber. ADRs join the final commit with the memory file and get one report line.

**The next run looks up the project's words in the glossary first** (`phases/0-preflight.md`, `phases/3-spec.md`). Usually 3–15 terms. The agent does not see the repo, so an existing glossary is handed to it with one brief line saying whose it is.

**Whose glossary it is** — by the marker on its first line, like the memory file:

- **`<!-- autopilot:glossary -->` — Autopilot's.** Kept true, not only added to — the next run trusts it over the code. Each run answers for what **it** changed: a term whose meaning this run's spec changed gets its definition rewritten; a term whose concept this run removed — by the user's word or a `D##` — is deleted. A term this run never touched stays — «not in my spec» is not «gone from the project». The brief line: «Это словарь Autopilot: перепиши определения, смысл которых эта спецификация изменила, и удали термины, которые она убрала; остальные не трогай».
- **No marker — the user's.** A `GLOSSARY.md` is continued in its own format; a `CONTEXT.md` gets the new terms and **none of the old ones changes** — a term now used differently goes into the report as a question, not into the file.
- **A `CONTEXT-MAP.md`** means several contexts — the brief drops the glossary paragraph; the report says so in a line.

**Past ~40 terms the project has outgrown one glossary.** Autopilot does not split it: the report suggests it in one line; the split is the user's call. The glossary goes into the final commit with the ADRs.

## On resume

The memory file is read **first**, before `state.js`. Missing or plainly stale against the code (and Autopilot's) → fix it in this run. `docs/adr/` is not read on resume; open one only when a decision is about to be reversed.
