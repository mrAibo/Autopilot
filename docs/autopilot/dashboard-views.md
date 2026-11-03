# Dashboard views (themes)

One dashboard page, eight views of the same `window.STATE`. The switcher sits in the header; the choice is stored in the browser, not in the project.

| id | What it shows |
|----|---------------|
| `overview` | Default: mission hero (with the stage track), key figures, tickets by wave (pending ones too), gates and the live feed; every block once |
| `timeline` | Track, per-ticket timeline, full event feed |
| `requirements` | Requirement words, gates, requirement summary, debt |
| `resources` | Key figures, model routes, tokens, isolation |
| `summary` | Result hero, tiles, summary, blind spots, report, concerns, debt, additions |
| `classic` | The earlier single-page layout |
| `focus` | For a narrow panel beside the chat: state hero, running and waiting tickets, latest events; no tiles or tables |
| `quality` | Can it be accepted: gates, blind acceptance, review and report notes, requirements with statuses, leftovers |

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
2. Add a function with that id to `VIEWS`: it receives the ready blocks (`c.hero`, `c.kpiRow`, `c.tasksCard`, …) and returns an HTML string.
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
