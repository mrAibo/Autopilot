# 02 — Роутер, журнал расхода, ключ подписи и граница Bash

**Требования:** R05, R06, R08, R21, R23, R24, R27, R29
**Зависит от:** —
**Зона:** `skills/autopilot/tools/model_router.py` · `skills/autopilot/tools/retry_policy.py` · `skills/autopilot/tools/run_log.py` · `skills/autopilot/tools/claude_attest.py` · `skills/autopilot/tools/gate_sign.py` · `skills/autopilot/tools/claude_agent_guard.py` · `skills/autopilot/tools/agent_profiles.py` · `skills/autopilot/tools/model-capabilities.json` · `tests/test_model_router.py` · `tests/test_retry_policy.py` · `tests/test_run_log.py` · `tests/test_claude_attest.py` · `tests/test_gate_sign.py` · `tests/test_claude_agent_guard.py` · `tests/test_agent_profiles.py` · `tests/test_audit_routing.py`
**Волна:** 1
**Ревью:** да — риск: подпись гейтов, ключ и граница Bash
**Модель:** сильная

## Что должно заработать

Риск таска считается по зоне и целым словам; планировщик может назвать класс таска; у кода есть профиль Haiku на высоком effort, у чтения — на низком; страховка эскалации Haiku → Sonnet доступна как проверка в политике; в строке расхода журнала есть модель и effort; запись «прогон начат подписанным» атомарна; ключ подписи на Windows защищён DPAPI; `bash_gate` не пускает субагента к `.autopilot/`, `~/.autopilot/`, `.claude/agents/`. Спецификация: истории 5, 6, 8, 21, 23, 24, 27, 29; границы — `interfaces.md` (model_router, retry_policy, run_log/claude_attest, gate_sign).

## Из брифа, дословно

> «риск таска определяется словами в его тексте: «подпись», «ключ», «token», «signature», а подстроки `auth`, `session`, `migration` ловятся даже внутри других слов («author»)» — R05
> «в строках расхода журнала нет модели и effort» — R06
> «запись «прогон начат подписанным» пишется не атомарно» — R08
> «Планировщик пишет в таск класс («механический / обычный / сложный») или шесть баллов и одну строку причины; роутер проверяет границы» — R21
> «Разделить: чтение — `haiku/low`, код — `haiku/high`» — R23
> «одна автоматическая эскалация Haiku → Sonnet, если дешёвый таск вернулся с красной проверкой после первого дозапроса» — R24
> «сбой записи журнала проглатывается по замыслу, но владелец должен видеть, что журнал неполный» — R27 (здесь — запись счётчика сбоев в `.autopilot/run-log.fail`)
> «запретить субагенту в `bash_gate` пути `.autopilot/`, `~/.autopilot/`, `.claude/agents/`, ключ подписи держать в хранилище ОС» — R29

## Разделы спецификации

Истории 5, 6, 8, 21, 23, 24, 27, 29; «Решения по реализации».

## Критерии приёмки

- [ ] `assess_ticket` на тексте таска с зоной `*.md`/`docs/` и словами «подписи», «author», «session» возвращает `risk` 0; на таске с зоной `gate_sign.py` — `risk` 10; «author» не срабатывает на `auth` (тесты, красные до правки)
- [ ] Таск с заголовком `**Класс:** механический` получает баллы профиля cheap, `сложный` — strong; рассчитанный по зоне риск класс не опускает; без заголовка — как раньше; сигнатуры `choose_route` и `assess_ticket` не изменились
- [ ] Профили `cheap_read` (`haiku/low`) и `cheap_code` (`haiku/high`) в политике; исполнитель механического таска получает `cheap_code`, разведчик — `cheap_read`; `model-capabilities.json` объявляет `haiku/high`; Fable и Opus без подтверждения по-прежнему блокируются (тесты)
- [ ] `retry_policy.escalation_allowed(model, retries, cause)` → `True` только для Haiku, не более одного раза и только при причине `tests`; во всех остальных случаях `False`; тесты, включая вторую эскалацию (отказ)
- [ ] `run_log.KINDS["executor"]` включает `model`, `effort`; `claude_attest.log_usage` заполняет их из профиля `.claude/agents/<agent_type>.md`, иначе из `resolvedModel`, иначе пусто; `append` не бросает; при сбое записи увеличивает число в `.autopilot/run-log.fail` (тест: запись в недоступный каталог → `False`, счётчик вырос)
- [ ] Запись «прогон начат подписанным» идёт через временный файл и `replace_with_retry`: тест с обрывом между записью и заменой не оставляет битого файла
- [ ] Windows: `gate.key` хранится как блок `dpapi:` и читается обратно; старый открытый ключ читается и переписывается защищённым; не Windows — прежнее поведение (тест пропускается не на Windows); ошибка DPAPI → прежний файл и одна строка предупреждения
- [ ] `bash_gate` отказывает, когда в аргументах записи/удаления/копирования/переноса есть `.autopilot/`, `~/.autopilot/` или `.claude/agents/` (тесты: `cp x .autopilot/gate.key`, `rm -rf ~/.autopilot`, `mv a .claude/agents/b`); чтение и прочие команды не затронуты
- [ ] `python -m unittest discover -s tests` зелёный; изменённые модули синтаксически чисты (`python -m compileall -q skills/autopilot/tools tests`)
