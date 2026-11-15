# 03 — Эскалация Haiku → Sonnet в ap.py, документы фаз и счётчик тестов

**Требования:** R21, R22, R23, R24, R25, R28
**Зависит от:** 01, 02
**Зона:** `skills/autopilot/tools/ap.py` · `skills/autopilot/tools/test_count.py` · `skills/autopilot/phases/3-spec.md` · `skills/autopilot/phases/4-plan.md` · `skills/autopilot/phases/5-subagents.md` · `skills/autopilot/prompts/` · `docs/autopilot/model-routing.md` · `docs/autopilot/retry-policy.md` · `docs/autopilot/run-log.md` · `docs/autopilot/claude-code.md` · `README.md` · `README.ru.md` · `README.de.md` · `AGENTS.md` · `tests/test_audit_docs.py` · `tests/test_ap_escalation.py`
**Волна:** 2
**Ревью:** нет
**Модель:** обычная

## Что должно заработать

`ap.py ticket NN retry --cause tests --escalate` один раз переводит таск с Haiku на Sonnet и записывает это; документы фаз велят планировщику писать класс таска и нарезать «Haiku-таски», разведчику — собирать пакет контекста; число тестов в `AGENTS.md` и README подставляет скрипт. Спецификация: истории 21–25, 28.

## Из брифа, дословно

> «Сейчас `phases/4-plan.md:55` велит считать пометку планировщика «только описанием», хотя путь `--scores` в роутере уже есть» — R21
> «механическую работу планировщик выносит в отдельные маленькие таски — чёткая постановка появляется не сама, её нужно нарезать» — R22
> «Дешёвый профиль для кода — Haiku на высоком effort, а не на низком» — R23
> «Это меняет действующее правило `docs/autopilot/retry-policy.md` («не повышать модель только из-за упавшей команды»)» — R24
> «Haiku собирает «пакет контекста» для Sonnet-исполнителя: нужные выдержки из файлов и интерфейсы одним файлом» — R25
> «Число тестов в `AGENTS.md` и README подставлять скриптом — сейчас там «730», прогон даёт 750» — R28

## Разделы спецификации

Истории 21–25, 28; `interfaces.md` (retry_policy · эскалация, Документы, Счётчик тестов).

## Критерии приёмки

- [ ] `ap.py ticket NN retry --cause tests --escalate` на таске с профилем Haiku, после первого дозапроса, вызывает `retry_policy.escalation_allowed`, записывает в таск `escalatedFrom` (исходная модель) и новый маршрут Sonnet, пишет строку в журнал; вторая эскалация и эскалация таска не на Haiku — отказ с понятной строкой; тесты в `tests/test_ap_escalation.py`
- [ ] `phases/4-plan.md` описывает `**Класс:**`/`**Причина класса:**`, признаки Haiku-таска (одна зона, до ~150 строк, критерии — команды, интерфейсы записаны), порог холодного старта, и больше не велит считать пометку планировщика «только описанием»; `grep -n "только описанием" skills/autopilot/phases/4-plan.md` пусто
- [ ] `phases/3-spec.md` и `prompts/` описывают `context-pack.md`: разведчик пишет его, исполнитель читает первым, дочитывает сам при пропуске
- [ ] `docs/autopilot/retry-policy.md` описывает единственную явную эскалацию Haiku → Sonnet и сохраняет правило «не повышать» для остальных случаев; `model-routing.md` — профили `cheap_read`/`cheap_code` и класс таска; `claude-code.md` — запрет путей в `bash_gate` и ключ под DPAPI на Windows
- [ ] `tools/test_count.py` печатает число тестов `unittest` и с флагом `--write` подставляет его между маркерами `<!-- tests:count -->…<!-- /tests:count -->` в `AGENTS.md` и трёх README; тест на маркеры и на отсутствие маркеров (без маркеров — файл не меняется)
- [ ] В `AGENTS.md` и README стоят маркеры и число, равное фактическому (`python skills/autopilot/tools/test_count.py` совпадает)
- [ ] `python -m unittest discover -s tests` зелёный
