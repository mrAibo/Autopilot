# Dashboard designs

One dashboard page, six designs. The page is a single column ("Ribbon" layout, up to about 1100 px): header, hero, a pinned "waiting for an answer" bar, then collapsible `<details>` sections. A design changes only the look of those same blocks; ids, texts, blocks and the `state.js` contract stay as they were. The choice is stored in the browser, not in the project, and the default is «Aurora».

| id | No | Scheme | Tags | Accent | Special element |
|----|----|--------|------|--------|-----------------|
| `aurora` | 01 | `both` | dark, glass | `#4df0be` | ring |
| `editorial` | 02 | `light` | light, serif | `#bf3a1e` | "Done" stamp |
| `brutal` | 03 | `light` | lime, brutal | `#d8ff3e` | ticker |
| `terminal` | 04 | `dark` | dark, mono | `#70ff9a` | ASCII bars |
| `blueprint` | 05 | `light` | light, technical | `#1849a9` | dimension lines |
| `bento` | 06 | `light` | light, soft | `#5a4bdb` | ring |

Names: Aurora, Report, Pulse, Terminal, Blueprint, Bento (Russian: Аврора, Отчёт, Пульт, Терминал, Чертёж, Бенто). Mockups of each live in `mockups/dashboard-2026/`; screenshots of the production template (six designs, 1440 and 400 px) are in the run folder `.autopilot/2026-11-19-dashboard-designs-wave1--wip/shots/`.

## Registry

Everything is in `skills/autopilot/phases/dashboard-template.html`:

- `DESIGNS` — array of `{id, no, name:{ru,en}, tagline:{ru,en}, accent:'#rrggbb', scheme:'dark'|'light'|'both', tags:[...]}`, in the order of the table above; `DESIGN_IDS = DESIGNS.map(d => d.id)`;
- `DESIGN_KEY = 'autopilot-design'` (the `localStorage` key), `DEFAULT_DESIGN = 'aurora'`;
- `storedDesign()` never throws: an empty, unknown or unreadable value gives `aurora`; `applyDesign(id)` sets `data-design` on `<html>`; `selectDesign(id)` stores, applies and calls `render(CUR.lang)`;
- the header combobox (`data-dcombo`): `comboList(q)` searches by id, number ("05" and "5"), name in ru/en and tags; an empty query lists all six; `comboKey()`, `comboOpen()`, `comboSync()` give `ArrowDown`/`ArrowUp`, `Enter`, `Esc` and `aria-activedescendant`.

The old `autopilot-view` and `autopilot-boardmode` keys are not read and do not affect the page.

## Theme scheme

The light/dark theme buttons (`autopilot-theme`) act only for a design with `scheme: 'both'` (Aurora). Other designs have one fixed scheme and set `data-theme` to it. Design tokens live only in `html[data-design="<id>"]` blocks (a light and a dark half for `both`); shared structure rules do not name designs. The old base `:root` palette stays underneath as a fallback for an unknown `data-design`. Text is at least 4.5:1 in every design and theme; state is a word or an icon as well as a colour.

## Slots

Special elements are pure functions of the state that return `''` when there is no data (so no empty frame is drawn): `dxTicker({S,L})` (stage, done/total, tests, time), `dxAscii({S,L})` (progress of stages, requirements and tickets), `dxDim({S,L})` (dimension lines around the hero with the due time), `dxStamp({S,L})` (only for a finished build, with the date), `dxRing({S,L})` (share of finished tickets, percent in the centre). Classes: `.dx-ticker`, `.dx-ascii`, `.dx-dim`, `.dx-stamp`, `.dx-ring`; shared CSS hides all of them and each design shows its own. The older requirements ring `ringHTML('')` (class `ring`) is hidden in every design by `.ovh>.ring{display:none}` (Aurora and Bento draw `.dx-ring` instead).

## Single page

`page(c)` is the only layout function: it returns the pinned bar, the hero and the sections `<details class="sec" id="mission|reqs|tasks|quality|models|gates|feed">` (summary at least 44 px; open state in `UI.sec`). The rail links `#mission #tasks #models #quality` by the ids really present on the page. The nine earlier layouts and the tabs are gone. Summaries, chips and buttons are at least 44 px in all six designs (one rule, `html:not([hidden]) :is(summary,.vopt,button)`); the rail takes the design's `--hero` (Aurora keeps its own gradient). In `@media print` the rail, pinned bar, ticker and buttons are hidden and every section is shown open on a light ground. The page loads no fonts and makes no requests (system font stacks), honours `prefers-reduced-motion`, and the template stays under 450 KB (a test holds the ceiling). A block is drawn only when `state.js` has its data; an old state without `blind`, `debt`, `usageEvents` or `startedAt` still draws the full page in every design.

## Add a seventh design

1. Add an entry to `DESIGNS` (id, next `no`, names and taglines, accent, scheme, tags).
2. Add a token block `html[data-design="<id>"][data-theme="<scheme>"][lang]:not([hidden])` (`<scheme>` is `light` or `dark`; for `both` one block per half) and a separate accent rule `html[data-design="<id>"][lang]:not([hidden]):not([data-theme="none"]){--accent:#rrggbb}` with the accent of the registry entry. The block must set every shared token: `--bg --card --inset --soft --line --line2 --tx --tx2 --mut --quiet --hero --done* --now* --rev* --fix* --bad* --idle --accent --on-done --on-rev --on-bad --on-fix --warn-*`. The rail takes `--hero` by itself (its text must reach 4.5:1 on it); if the accent is paler than 4.5:1 on `--bg` or `--card`, give `.wordmark b` and `.dopt[aria-selected="true"]` `color:var(--tx)` for the design, as «Pulse» does.
3. Decide which slots the design shows (`.dx-ticker`, `.dx-ascii`, `.dx-dim`, `.dx-stamp`, `.dx-ring`) and add `display` rules for it; no new markup is needed.
4. Add a row to the table above and run the tests: `python -m unittest discover -s tests -p "test_dashboard_*.py"`. The tests read the registry from the template (`DESIGN_IDS` in `test_dashboard_views.py`, `registry()` in `test_dashboard_designs.py`: id, number, accent, scheme, tags) and take each design's scheme from it, so the new design is rendered in both languages and checked for the token set, 4.5:1 contrast (text, filled states, accent as text), the 44 px targets, forbidden external references and size without editing a test. Only the first six designs are pinned, as a prefix, in the golden test.

## Deviations from the mockups

| Mockup | Production template |
|--------|---------------------|
| data baked into each file | live data from `window.STATE` |
| iframe switcher (`dashboard.html`) | combobox in the page header, `data-design` on `<html>` |
| every design has its own light/dark | the theme buttons work only for «Aurora» |
| every design has its own structure | one layout (single column) for all six |
| ticker, stamp, bars, dimension lines, ring are static markup | slots drawn from the state, empty without data |
| no print, no reduced motion | `@media print` and `prefers-reduced-motion` added |

## Header, minutes, token

"Updated N s ago" in the header counts live from `updatedAt` (not drawn without it); a finished build shows "done <time>". A stage that was sent back keeps `segments: [{startedAt, finishedAt|null}]` and its minutes are their sum. The server of `ap.py` serves data only with `?t=<token>`; the page sends the token with every `state.js` request (`stateUrl()`); from `file://` the embedded snapshot is used.

## Update an existing project's dashboard

Two optional state fields add to the page: `landedWith` turns the header into «Сдано с оговорками» / "Landed with caveats" with the list of `problems`; `opusApproval` adds an «Opus включён» / "Opus enabled" line. Without them the page is as before. Projects keep their own copy of the page, so a skill update does not change it. Run:

```bash
python3 skills/autopilot/tools/dashboard_upgrade.py --project <PROJECT_DIR> [--dry-run]
```

It checks the slug, embeds the current `state.js` snapshot, backs up the old page and swaps it atomically. The run is not reset.

## Confirm buttons

Block `.actblock`, one markup for all designs (the design changes only the look). Waits `briefing`, `spec`, `plan`, `accept` (`ACT_KINDS`, the same list as `ALLOWED_ACTIONS` in `ap.py`) get one button on a page opened over `http(s)` with a token: the first click turns the label into "Sure? click again", the second sends `POST /.ap-act` + `location.search` with `{kind, since, answer?}` (`answer` only for `briefing`; an empty one is not sent). Any answer but 200, or a stopped server, returns the button with a line saying why; 200 replaces it with "Answer sent". Without a token or on `file://` there are no buttons, only one line about `ap.py url`; with no wait, or with `action`/`stop`, there is no button either. Commands that need the user's words (`ticket NN reset --by-user`, `finish --by-user`, `opus approve --by-user`, `dropped` in `manifest.md`) are shown with a "copy" button only, on a tokened page when a ticket failed or the wait is `action`/`stop`. The page calls `fetch('/.ap-act' + location.search, …)` directly; the template tests allow exactly that one call and no other `fetch`, XHR, socket or beacon (`forbidden_network` in `tests/test_dashboard_views.py`). Tests: `tests/test_dashboard_buttons.py` (the server is a `fetch` stub).

## Tests

```bash
python -m unittest discover -s tests -p "test_dashboard_*.py"
python -m unittest discover -s tests -p test_brand_assets.py
```
