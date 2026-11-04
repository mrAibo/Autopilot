# Dashboard views (themes)

One dashboard page, eight views of the same `window.STATE`. The switcher sits in the header; the choice is stored in the browser, not in the project.

| id | What it shows |
|----|---------------|
| `overview` | Default: progress ring ("N of M requirements closed") and a forecast, the stage route with minutes, a Gantt chart (up to eight tickets; the wave is named in each row, so there is no second wave list of the same tickets), your words, gates, "needed from you", the live feed, models and isolation; every card of Classic stays, once |
| `timeline` | Hero with the phrase, the forecast and the stage route (`c.tlHero`); up to five cards for requirements, tickets, tests, tokens and work time (`c.tlTiles`, only those with data); the detailed Gantt on the left (every ticket, waves named, model chips); on the right "needed from you", gates and the event feed; your words at the bottom |
| `requirements` | "The path of your requirements": a matrix of each phrase by seven stages (written, spec, ticket, code, tests, review, blind acceptance) with a "how many reached the stage" row; below it the word list with its filters, gates, summary and leftovers |
| `resources` | Key figures, the routes table (ticket state, model chip, tokens per ticket, worktree; a waiting ticket with no route gets a row with 0 tokens and "not created", and no "why" without data), tokens, isolation |
| `summary` | Hero with cards on the right (work time, tests, tokens; no commits card, `state.js` has no commits), a verdict per requirement (where, tests, review, blind acceptance), the acceptance mismatch (text only, no action buttons), review notes, "what to do next", "needed from you" |
| `classic` | The earlier single-page layout, with its own colours |
| `compact` | One column for a narrow panel beside the chat: ring and forecast, tiles, stage strip, mini Gantt, "needed from you" (keys and stubs only), gates, feed; no models, isolation or decided-for-you list, and at 520 px or less a shorter header and title. Chosen by default when the window is 520 px wide or less and nothing is saved; a saved choice wins; the old saved value `focus` is read as `compact` |
| `quality` | Can it be accepted: gates, blind acceptance, review and report notes, requirements with statuses, leftovers |

## Header

Every view except `classic` shows "updated N s ago" in the header, counted live from `updatedAt` by the same timer as the footer; without `updatedAt` it is not drawn.

## Ticket notes in the Gantt rows

Overview, Timeline and Compact put a note under a ticket's Gantt row, built by the same `noteOf`/`redoOf` helpers Classic's ticket list uses: why a failed ticket failed (`concerns`), the review remark of a ticket in review, the last of `repairFindings` for a ticket in repair, and the label "N repairs · M retries" for any ticket whose counts are not zero. No note data, no block. A note longer than 140 characters is cut with a "Show more" button (`data-more="nt:<ticket id>"`, the same toggle as the other lists). Everything comes from `state.js` through `esc()`; there are no new fields.

## Palette

Every view except `classic` uses the palette of the design handoff (`:root[data-view]:not([data-view="classic"])`, light and dark, text at least 4.5:1); `render()` sets `data-view` on the root. The page loads no fonts and makes no requests: system font stacks only. State is always a word or an icon as well as a colour, and the view buttons are 44 px high.

## What a block needs

A block is drawn only when `state.js` has its data; there are no error boxes for a missing field. The requirements matrix reads `reqList[].status`, `tickets[].requirements` (`R03.1` counts as `R03`), ticket statuses and `blind.mismatches`; the forecast needs finished tickets with `startedAt` and `finishedAt`; per-ticket tokens need `usageEvents[].ticket`. The summary has no before/after findings and no "decided for you" block because `state.js` has no such fields. An old project without `blind`, `debt`, `usageEvents` or `startedAt` still draws all eight views.

## Where it lives

Everything is in `skills/autopilot/phases/dashboard-template.html`:

- `VIEW_IDS` — ordered list of ids (first is the default);
- `VIEWS` — registry `id → function` that only joins the blocks `render()` already built (it does not read `STATE` or touch the DOM);
- `I18N.ru.views` and `I18N.en.views` — the button labels;
- `VIEW_KEY = 'autopilot-view'` — the `localStorage` key. An unknown or missing value falls back to the first id.

## Side rail

The rail shows a link only for an anchor (`mission`, `tasks`, `models`, `quality`) that the chosen view really has; a new view therefore needs no rail edits, only those ids on its blocks. The link of the view's own anchor (`VIEW_HOME`) is highlighted with `aria-current="page"` and carries the view's name, so Timeline never lights up "Overview". The version under the logo is `skillVersion` from `state.js`; without it nothing is printed.

## Add a view

1. Add the id to `VIEW_IDS` and its home anchor to `VIEW_HOME`.
2. Add a function with that id to `VIEWS`: it receives the ready blocks (`c.ovHero`, `c.route`, `c.gantt`, `c.matrixCard`, `c.kpiRow`, `c.gatesCard`, …, the keys of the `VIEWS[VIEW]({…})` call in `render()`) and returns an HTML string; put `id="mission"|"tasks"|"models"|"quality"` on the blocks the rail should link to.
3. Add the label to both `I18N.ru.views` and `I18N.en.views`.
4. Run the tests below.

## Update an existing project's dashboard

Projects keep their own copy of the page, so a skill update does not change it. Run:

```bash
python3 skills/autopilot/tools/dashboard_upgrade.py --project <PROJECT_DIR> [--dry-run]
```

It checks the slug, embeds the current `state.js` snapshot (a BOM or a missing `window.STATE =` prefix is fine), backs up the old page and swaps it atomically. The run is not reset.

## Tests

```bash
python -m unittest discover -s tests -p test_dashboard_views.py
python -m unittest discover -s tests -p test_dashboard_upgrade.py
python -m unittest discover -s tests -p test_brand_assets.py
```
