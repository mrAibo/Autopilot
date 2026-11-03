# 03 — Подпись гейтов и защита файлов прогона

**Требования:** R17, R05
**Зависит от:** 01
**Зона:** `skills/autopilot/tools/gate_sign.py` · `skills/autopilot/tools/claude_attest.py` · `skills/autopilot/tools/claude_agent_guard.py` · `skills/autopilot/tools/test_evidence.py` · `skills/autopilot/tools/ap.py` · `skills/autopilot/phases/0-instruments.md` · `docs/autopilot/claude-code.md` · `tests/test_gate_sign.py` · `tests/test_claude_attest.py` · `tests/test_claude_agent_guard.py` · `tests/test_test_evidence.py` · `tests/test_ap.py`
**Волна:** 2
**Ревью:** да — ключи и подписи
**Модель:** сильная

## Что должно заработать

В strict-прогоне исполнитель не может подделать маршрут, квитанции и результат тестов правкой файлов проекта: гейты сверяют подпись ключом из домашней папки пользователя, а запись в защищённые файлы через Write/Edit закрыта хуком.

## Из брифа, дословно

> «A05: гард защищает от промахов оркестратора, не от исполнителя» — `state.js`, `model-capabilities.json`, `attestations.jsonl` и `profileSha` лежат в `.autopilot` без подписи; хук стоит только на `Agent|Task`, правила deny на Write/Edit по `.autopilot` и `.claude` нет, у исполнителя Write есть.
> «I02: подписанные квитанции гейтов, ключ вне `.autopilot` — иначе правка `state.js`/`attestations.jsonl` проходит сверку (A05)»
> Решение при брифинге: пользователь «ok» — ключ в `~/.autopilot/gate.key` (0600), вне проекта; нет ключа — strict-прогон останавливается; старые прогоны без подписи принимаются с предупреждением, подписываются только новые.

## Разделы спецификации

Истории 10–13, «Решения по реализации», «Открытые места». Сигнатуры `gate_sign` — `interfaces.md`.

## Критерии приёмки

- [ ] `gate_sign.sign/verify` работают, ключ создаётся `ensure_key()` с правами 0600 только при `init --strict-routing`; путь переопределяется `AUTOPILOT_HOME`; ключ нигде не пишется в проект
- [ ] подписываются: запись `routing.verified` вместе с `profileSha`, каждая строка `attestations.jsonl`, результат `test_evidence`; guard и strict-гейт `ticket done` сверяют подпись; подделка поля или строки без ключа — отказ
- [ ] новый strict-прогон помечается `gateSigned: true`; прогон без метки принимается с предупреждением в выводе
- [ ] нет ключа при `gateSigned: true` → операция останавливается фразой «нет ключа подписи, запусти init заново или восстанови ~/.autopilot/gate.key»; ключ молча не создаётся
- [ ] хук блокирует Write/Edit/MultiEdit/NotebookEdit по `.autopilot/state.js`, `.autopilot/attestations.jsonl`, `.autopilot/model-capabilities.json`, `.claude/settings*.json`, `.claude/agents/*` в strict-прогоне без `finishedAt`; вне strict и после `finishedAt` — разрешено; `install_hook` ставит второй matcher идемпотентно
- [ ] `gate_sign.py` в списке копирования `phases/0-instruments.md`
- [ ] `docs/autopilot/claude-code.md` честно описывает границу: подпись защищает от правки файлов проекта, но не от процесса с доступом к домашней папке; запись через Bash хуком не блокируется
- [ ] `python3 -m unittest discover -s tests` целиком зелёный
