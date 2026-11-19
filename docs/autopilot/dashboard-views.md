# Dashboard views (themes)

One dashboard page that picks what to show by itself (`now`), plus eight older views of the same `window.STATE` under "More" in the header. The page opens on `now`; a view chosen under "More" is stored in the browser, not in the project, and wins on the next open. The production skin is «Aurora»: it only repaints the existing blocks, so every id, text, block and the `state.js` contract stay as they were.

| id | What it shows |
|----|---------------|
| `now` | Default. Four tabs: "Now", "Requirements", "Summary", "Details" (`c.nowTabs`, state in `UI.tab`). "Now" picks its content by the state of the build: waiting for an answer — a pinned bar with the question text and how long it has waited sits on top of every tab (`c.askBar`), then the one-line hero (`c.nowHero`: small ring, the title on one line with a `title` tooltip, time and tests beside it; a landing with caveats keeps its list under the line) and the stage route; development — the hero, the stage route and the list of tickets (a plain list; the ticket board is a separate block); done — the summary hero with "what to do next". "Requirements" — the requirement board whose "Accepted" column shows the first six cards and a "Show all N" / "Collapse" button (`UI.rbOkAll`), the requirements matrix and the word list. Over HTTP without the token the page arrives with `window.STATE=null` and shows one line telling the user to take the address from `ap.py url`. "Summary" — the full Gantt and the summary cards. "Details" — slots for models, spend, checks and build history. Gate codes (G1–G4) are not in the text of this page; service strings such as `score=…; profile=…` are turned into a plain phrase by `humanRoute(route)` ("Sonnet, reinforced mode: the ticket touches signatures and keys"), followed by the planner's phrase from `why=` in `routing.reason` |
| `overview` | Progress ring ("N of M requirements closed") and a forecast, the stage route with minutes, a Gantt chart (up to eight tickets; the wave is named in each row, so there is no second wave list of the same tickets), your words, gates, "needed from you" and the live feed, as in the mockup; no models and isolation blocks (they are in Resources and Classic) and no second list of tickets, so a ticket title shows once, in the Gantt (the hero lead names running tickets by id); there is no `models` anchor, so the rail has no "Models" link here; the other cards of Classic stay, once |
| `timeline` | Hero with the phrase, the forecast and the stage route (`c.tlHero`); up to five cards for requirements, tickets, tests, tokens and work time (`c.tlTiles`, only those with data); the detailed Gantt on the left (every ticket, waves named, model chips); on the right "needed from you", gates and the event feed; your words at the bottom |
| `requirements` | "The path of your requirements": a matrix of each phrase by seven stages (written, spec, ticket, code, tests, review, blind acceptance) with a "how many reached the stage" row; below it the word list with its filters, gates, summary and leftovers |
| `resources` | Key figures, the routes table (ticket state, model chip, tokens per ticket, worktree; a waiting ticket with no route gets a row with 0 tokens and "not created", and no "why" without data), tokens, isolation |
| `summary` | Hero with cards on the right (work time, tests, tokens; no commits card, `state.js` has no commits), a verdict per requirement (where, tests, review, blind acceptance), the acceptance mismatch (text only, no action buttons), review notes, "what to do next", "needed from you" |
| `classic` | The earlier single-page layout, with its own colours |
| `compact` | One column for a narrow panel beside the chat: ring and forecast, tiles, stage strip, mini Gantt, "needed from you" (keys and stubs only), gates, feed; no models, isolation or decided-for-you list, and at 520 px or less a shorter header and title. Chosen by default when the window is 520 px wide or less and nothing is saved; a saved choice wins; the old saved value `focus` is read as `compact` |
| `quality` | Can it be accepted: gates, blind acceptance, review and report notes, requirements with statuses, leftovers |

## Skin «Aurora»

The selected design (concept 01) is a layer of tokens and a few decorative rules, not a rewrite of the nine views: `<html data-skin="aurora">`, then `html[data-skin="aurora"]:not([data-view="classic"]):not([data-theme="light"])` for the dark base and `html[data-skin="aurora"][data-theme="light"][data-view]:not([data-view="classic"])` for the light derivative override the palette of the design handoff. The dark half is the base (it opens dark, like the concept): near-black `#05070D`, radial mint/sky/violet glows behind the page, glass cards (a soft top-surface sheen, 24 px corners, layered shadows), mint/sky/violet accent gradients on active tabs and tile edges, and the same status colours as before — state stays a word and a colour. The light half is a derivative (`[data-theme="light"]`, white cards on a cool pale ground) and is one click away; both satisfy 4.5:1 for text. Classic keeps its own colours: the skin rules are scoped away from it. No iframe, no fonts, no requests: it is still one static self-contained template.

## The view switcher

All nine views are in a searchable combobox in the header (`data-vcombo`): type part of a name in Russian or English (or the id), the list filters; `ArrowDown`/`ArrowUp` move the active option (`ArrowDown` also opens the closed list), `Enter` picks it, `Esc` closes without a choice, and `aria-activedescendant` points at the active option while `role="combobox"`/`role="listbox"` describe the widget. Picking a view goes through the same path as the old buttons: `VIEW`, `localStorage[VIEW_KEY]`, `render()`. The old button strip is still in the markup but folded away (`class="tabs views" hidden`) — it keeps the per-view `data-view` buttons and the "More" button (`data-views-more`) that the tests read. In the narrow panel (700 px and less, the 380–900 px case included) the combobox takes the whole row of the tools and its list opens to the panel width; wider, it sits beside them.

## More

The eight older views stay in the hidden button strip, folded under the "More" button (`data-views-more`); the list opens by itself while one of them is chosen. Below 700 px (`matchMedia`) `render()` sets `data-narrow` on the root and the layout folds into one column; at 520 px or less with nothing saved the page still opens on `compact`.

## Header

Every view except `classic` shows "updated N s ago" in the header, counted live from `updatedAt` by the same timer as the footer; without `updatedAt` it is not drawn. A finished build shows "done <time>" (the date too, if it was another day) instead.

## Stage minutes and the feed

A stage that was sent back keeps `segments: [{startedAt, finishedAt|null}]`; its minutes are the sum of the segments, not first start to last end; without `segments` it is as before. A gate reset by a changed plan (`reason: plan-changed`, no numbers) is one line in the feed, "Check reset: the plan changed", and "reset" in the gates card.

## Server token

The server of `ap.py` serves data only with `?t=<token>` in the address. The page takes the token from `location.search` and sends it with every `state.js` request (`stateUrl()`); opened from `file://` there is no token and the snapshot inside the page is used as before.

## Ticket notes in the Gantt rows

Overview, Timeline and Compact put a note under a ticket's Gantt row, built by the same `noteOf`/`redoOf` helpers Classic's ticket list uses: why a failed ticket failed (`concerns`), the review remark of a ticket in review, the last of `repairFindings` for a ticket in repair, and the label "N repairs · M retries" for any ticket whose counts are not zero. No note data, no block. A note longer than 140 characters is cut with a "Show more" button (`data-more="nt:<ticket id>"`, the same toggle as the other lists). Everything comes from `state.js` through `esc()`; there are no new fields.

## Palette

Every view except `classic` uses the palette of the design handoff (`:root[data-view]:not([data-view="classic"])`, light and dark, text at least 4.5:1); `render()` sets `data-view` on the root. The Aurora skin (`html[data-skin="aurora"]`, see above) overrides those tokens and decorative rules for the same views; without a saved choice the page is dark, and the light theme button switches it to the light derivative. The page loads no fonts and makes no requests: system font stacks only. State is always a word or an icon as well as a colour; the combobox and its options are 44 px high.

## What a block needs

A block is drawn only when `state.js` has its data; there are no error boxes for a missing field. The requirements matrix reads `reqList[].status`, `tickets[].requirements` (`R03.1` counts as `R03`), ticket statuses and `blind.mismatches`; the forecast needs finished tickets with `startedAt` and `finishedAt`; per-ticket tokens need `usageEvents[].ticket`. The summary has no before/after findings and no "decided for you" block because `state.js` has no such fields. An old project without `blind`, `debt`, `usageEvents` or `startedAt` still draws every view.

## Where it lives

Everything is in `skills/autopilot/phases/dashboard-template.html`:

- `VIEW_IDS` — ordered list of ids (first, `now`, is the default; the rest sit under "More" / in the combobox);
- `VIEWS` — registry `id → function` that only joins the blocks `render()` already built (it does not read `STATE` or touch the DOM);
- `I18N.ru.views` and `I18N.en.views` — the labels: the combobox shows the current language and searches both;
- `VIEW_KEY = 'autopilot-view'` — the `localStorage` key. An unknown or missing value falls back to the first id;
- `comboList()`, `comboKey()`, `comboOpen()`, `comboSync()` and `selectView()` — the header combobox: search, arrows/Enter/Esc, aria state, and the one path to `VIEW` + `VIEW_KEY` + `render()`;
- `html[data-skin="aurora"]` in the `<style>` block — the skin's tokens and decorative rules (the handoff palette stays underneath for the light theme and for tests).

## Side rail

The rail shows a link only for an anchor (`mission`, `tasks`, `models`, `quality`) that the chosen view really has; a new view therefore needs no rail edits, only those ids on its blocks. The link of the view's own anchor (`VIEW_HOME`) is highlighted with `aria-current="page"` and carries the view's name, so Timeline never lights up "Overview". The version under the logo is `skillVersion` from `state.js`; without it nothing is printed.

## Add a view

1. Add the id to `VIEW_IDS` and its home anchor to `VIEW_HOME`.
2. Add a function with that id to `VIEWS`: it receives the ready blocks (`c.ovHero`, `c.route`, `c.gantt`, `c.matrixCard`, `c.kpiRow`, `c.gatesCard`, …, the keys of the `VIEWS[VIEW]({…})` call in `render()`) and returns an HTML string; put `id="mission"|"tasks"|"models"|"quality"` on the blocks the rail should link to.
3. Add the label to both `I18N.ru.views` and `I18N.en.views`.
4. Run the tests below.

## Update an existing project's dashboard

Two optional state fields add to the page: `landedWith` (a landing the user accepted with caveats) turns the header into «Сдано с оговорками» / "Landed with caveats" with the list of `problems`; `opusApproval` adds an «Opus включён» / "Opus enabled" line to the models view with the user's quotes, tickets and roles (more expensive than a Sonnet ticket, not measured; the actual cost is in the report via `measure-run.py`). Without these fields the page is as before.

Projects keep their own copy of the page, so a skill update does not change it. Run:

```bash
python3 skills/autopilot/tools/dashboard_upgrade.py --project <PROJECT_DIR> [--dry-run]
```

It checks the slug, embeds the current `state.js` snapshot (a BOM or a missing `window.STATE =` prefix is fine), backs up the old page and swaps it atomically. The run is not reset.

## Tests

```bash
python -m unittest discover -s tests -p test_dashboard_views.py
python -m unittest discover -s tests -p test_dashboard_now.py
python -m unittest discover -s tests -p test_dashboard_upgrade.py
python -m unittest discover -s tests -p test_brand_assets.py
```
