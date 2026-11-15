# F1 — Правки по код-ревью ветки

**Требования:** R02, R05, R24, R29
**Зависит от:** —
**Зона:** `skills/autopilot/tools/model_router.py` · `skills/autopilot/tools/ap.py` · `skills/autopilot/tools/claude_agent_guard.py` · `tests/test_audit_routing.py` · `tests/test_ap_audit.py` · `tests/test_ap_escalation.py`
**Волна:** 4
**Ревью:** да — ремонт ветки
**Модель:** сильная

## Что должно заработать

Четыре небольших исправления, найденных общим код-ревью ветки. Больше ничего не менять.

## Из брифа, дословно

> «риск таска определяется словами в его тексте: «подпись», «ключ», «token», «signature», а подстроки `auth`, `session`, `migration` ловятся даже внутри других слов («author»)» — R05
> «одна автоматическая эскалация Haiku → Sonnet, если дешёвый таск вернулся с красной проверкой после первого дозапроса» — R24
> «сервер дашборда отдаёт весь каталог .autopilot без проверки Host/Origin и без токена» — R02
> «запретить субагенту в `bash_gate` пути `.autopilot/`, `~/.autopilot/`, `.claude/agents/`» — R29

## Критерии приёмки (находки ревью, дословно)

- [ ] **model_router.py (WORD_RISK_RE, ~стр. 223):** `\b` не режет по `_`, поэтому `session_id`, `password_hash`, `auth_token`, `run_migration` в таске с кодовой зоной дают риск 0. Границей слова считается не латинская буква и не цифра (подчёркивание — граница); `author` по-прежнему не ловится. Тесты в `tests/test_audit_routing.py` на `session_id` (риск ловится) и `author` (не ловится).
- [ ] **ap.py (escalate_ticket, ~стр. 2198–2200):** целевая модель эскалации проверяется через `model_router.is_allowed_subagent_model(model)` без `premium_ok`, а не подстрокой `"sonnet" in model`; Opus и Fable не проходят в любом написании. Тест в `tests/test_ap_escalation.py`: эскалация на Opus и на Fable отказывает.
- [ ] **tests/test_ap_audit.py (~стр. 130):** `"/"` в списке путей, дающих 403, проходит только потому, что нет `index.html`, а в коде `/` открыта (OPEN_PAGES). Убрать `/` из списка 403 или проверять 200 при наличии `index.html`.
- [ ] **claude_agent_guard.py (docstring `mask_quotes`, ~стр. 307):** фраза «`$(...)` stays live» вводит в заблуждение: `bash_gate` подстановки не разбирает. Docstring говорит «не разбирается, принятое ограничение».
- [ ] `python -m unittest discover -s tests` зелёный; `python -m compileall -q skills/autopilot/tools tests` чисто.
