# F1 — Ремонт по ревью ветки

**Требования:** R05, R17, R06, R12, R18
**Зависит от:** —
**Зона:** `skills/autopilot/tools/gate_sign.py` · `skills/autopilot/tools/claude_agent_guard.py` · `skills/autopilot/tools/ap.py` · `skills/autopilot/tools/model_router.py` · `skills/autopilot/tools/process_containment.py` · `docs/autopilot/*.md` · `skills/autopilot/phases/0-resume.md` · `tests/test_gate_sign.py` · `tests/test_claude_agent_guard.py` · `tests/test_ap.py` · `tests/test_model_router.py` · `tests/test_process_containment.py` · `tests/test_skill_allowed_tools.py`
**Волна:** 3
**Ревью:** да — ремонт ветки
**Модель:** сильная

## Что должно заработать

Закрыты находки ревью ветки «исправить сейчас». Каждый пункт — критерий приёмки, у каждого красный тест до правки.

## Критерии приёмки

- [ ] (B02, безопасность) признак «прогон начат подписанным» хранится вне проекта: `init --strict-routing` пишет запись в `$AUTOPILOT_HOME/runs/<хэш realpath корня проекта>` с `sign(slug|startedAt)`; `run_status` и guard читают её первой. Запись есть, а state.js не совпадает (strict выключен, метки нет, `finishedAt` без записи о finish) — стоп (forged), не предупреждение; записи нет — unsigned. `finish` и не-strict `init` обновляют запись. Guard не возвращает «No active strict run» раньше проверки подписи (claude_agent_guard.py:109). Это же закрывает «ключ общий на машину: strict-прогон в проекте B жёстко останавливает старый неподписанный прогон в проекте A» (gate_sign.py:84 срабатывает по наличию ключа). Доки называют остаточный предел: Bash с доступом к домашней папке
- [ ] (spec) `run_mark` подписывает `slug|startedAt` без `dir`; тест: подписанный прогон → finish (переименование `--wip`) → `ticket done` → reopen проходит
- [ ] (безопасность) `is_allowed_subagent_model("claude-opus-4-1/haiku")`, `"anthropic.opus/sonnet"` отклоняются: opus/fable ищутся и в сыром `name.casefold()`; табличные тесты; `choose_route` использует ту же проверку (model_router.py ~237)
- [ ] (безопасность) `is_protected` сравнивает `.autopilot`/`.claude` без учёта регистра; тест с `.Autopilot/state.js` и `.CLAUDE/settings.json`
- [ ] (история 18) `py -3.13` убран из `docs/autopilot/*.md` и `skills/autopilot/phases/0-resume.md` (заменить на `py -3`); `tests/test_skill_allowed_tools.py` ищет по всем `docs/autopilot/*.md` и `skills/**/*.md`, а не по списку из 7 файлов
- [ ] `docs/autopilot/worktrees.md:191`: в примере `land` есть `--zone <path>`
- [ ] `process_containment.py:157-159`: `try: job.terminate() finally: proc.kill()`; исходный `TimeoutExpired` не теряется; тест
- [ ] `gate_sign.ensure_key` считает пустой `gate.key` отсутствующим и пересоздаёт; тест
- [ ] `state.gateSigned` (ap.py:~214) либо читается, либо убран, доки согласованы с кодом
- [ ] тест граничного случая: проект переименован или перенесён — запись по хэшу не найдена, прогон читается как unsigned (не как forged), в доках одна строка об этом
- [ ] доки `claude-code.md`: ключ принадлежит машине, а признак прогона — проекту

Не входит: scheduler.py/dashboard_upgrade.py (отчёт), `-latest` алиас, `__pycache__`, мелочи ap.py:1925/925, chmod в /tmp.
