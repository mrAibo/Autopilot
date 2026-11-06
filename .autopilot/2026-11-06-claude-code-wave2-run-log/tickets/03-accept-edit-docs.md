# 03 — `accept-edit` и worktree, сбой Bash-хука, запись в CHANGELOG

**Требования:** R22b, R22c, R22p
**Зависит от:** 01, 02
**Зона:** `skills/autopilot/tools/ap.py` · `tests/test_ap.py` · `docs/autopilot/claude-code.md` · `CHANGELOG.md`
**Волна:** 2
**Ревью:** нет
**Модель:** обычная

## Что должно заработать

Сданный таск после `accept-edit` с неосвобождённым worktree не проходит публикацию: отказ называет, что сделать (посадить worktree — `worktree NN land`, или снять — `worktree NN release`). Тест с понятным именем покрывает это, а тест `test_changed_ticket_resets_previous_acceptance` назван по тому, что он проверяет. В `docs/autopilot/claude-code.md` описан сбой Bash-хука. В `CHANGELOG.md` записаны R22–R22c.

Читать сначала: `interfaces.md`, `spec.md`, `notes.md` — в папке прогона. Таски 01 и 02 уже сданы: `run_log.py` и новые формы хука существуют, описывать их в `claude-code.md` надо по фактическому коду.

## Из брифа, дословно

> «описать в `docs/autopilot/claude-code.md`, что `onFailure: block` на хуке `Bash` при его сбое блокирует все Bash-команды проекта, и как это снять (удалить запись из `.claude/settings.json`). Менять поведение хука только по решению владельца.»
> «сданный таск после `accept-edit` с неосвобождённым worktree не проходит публикацию (`ap.py:454`): отказ с указанием, что worktree надо посадить или снять.»
> «Тест на этот случай; тест `test_changed_ticket_resets_previous_acceptance` переименовать по тому, что он проверяет на самом деле.»

## Разделы спецификации

«Решение» (R22b, R22c, R22p), «Решения по реализации», «Вне рамок».

## Критерии приёмки

- [ ] Сданный таск с worktree в статусе, отличном от `released`, после `ticket NN accept-edit --note "…"` и `ap.py tickets` завершается ошибкой, в тексте которой есть `worktree NN land` и `worktree NN release`; статус и коммит таска сохранены (тест)
- [ ] Тот же таск с освобождённым worktree (`released`) после `accept-edit` проходит публикацию (тест)
- [ ] `test_changed_ticket_resets_previous_acceptance` переименован по тому, что проверяет (сданный таск не сбрасывается молча, а останавливает публикацию); ссылок на старое имя в репозитории нет
- [ ] `docs/autopilot/claude-code.md` содержит раздел о сбое хука `Bash`: `onFailure: block` блокирует все Bash-команды проекта, включая `ap.py`; как снять — удалить запись хука из `.claude/settings.json`; поведение хука не менялось и меняется только по решению владельца; предел разбора команды назван по фактическому коду (формы из таска 02, что по-прежнему не ловится — `$(...)`, `eval`, скрипты) (тест на документ)
- [ ] `CHANGELOG.md`: в разделе «Unreleased» запись на каждое из R22, R22a, R22b, R22c (тест на документ по образцу уже существующего теста на CHANGELOG)
- [ ] Полный прогон `python3 -m unittest discover -s tests` зелёный
