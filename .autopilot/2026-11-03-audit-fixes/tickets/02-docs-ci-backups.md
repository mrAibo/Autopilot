# 02 — Документация, CI и бэкапы дашборда

**Требования:** R11, R12, R13, R14, R15
**Зависит от:** —
**Зона:** `STATUS.md` · `README.md` · `README.ru.md` · `README.de.md` · `docs/autopilot/gui-clients.md` · `docs/autopilot/worktrees.md` · `docs/autopilot/controller.md` · `docs/autopilot/model-routing.md` · `skills/autopilot/SKILL.md` · `.github/workflows/python-tests.yml` · `skills/autopilot/tools/dashboard_upgrade.py` · `tests/test_skill_allowed_tools.py` · `tests/test_documentation_locales.py` · `tests/test_dashboard_upgrade.py`
**Волна:** 1
**Ревью:** нет
**Модель:** обычная

## Что должно заработать

Новый чат, читающий STATUS.md и README, видит версию 2.6.0 и верные команды; команды из доков не вызывают запрос разрешения на каждый шаг; таблица моделей описывает все тиры; бэкапы дашборда не читаются чужими пользователями и не копятся; CI ловит синтаксическую ошибку в корневом `tools/`.

## Из брифа, дословно

> «A11: версии не сходятся» — `STATUS.md` называет «Current release v2.3.0» рядом с «2.4.0-rc.1» и «2.4.0», при том что `SKILL.md` = 2.6.0; README обещает «поставит Autopilot 2.3.0» и содержит dev-заметку про `<HOST>` и Windows Junctions в публичном тексте.
> «A12: доки велят `py -3.13 …` и `controller.py`, а `allowed-tools` пропускает только `py -3 .autopilot/ap.py *`»
> «A13: в таблице и скоринге нет tier `critical`»
> «A14: бэкап HTML со снимком `state.js` в общем tempdir»
> «A15: `compileall` только `skills/autopilot/tools` и `tests`»

## Разделы спецификации

Истории 17–21.

## Критерии приёмки

- [ ] `STATUS.md` начинается с текущего состояния 2.6.0; прежние записи сохранены как история
- [ ] в трёх README нет обещания установить 2.3.0 и нет `<HOST>`/Junction; заметка перенесена в `docs/autopilot/gui-clients.md`; существующий тест симметрии README зелёный
- [ ] в `docs/` и README нет `py -3.13`; `SKILL.md` allowed-tools покрывает `controller.py` для `python`, `python3`, `py -3`; тест проверяет, что запуски `ap.py`/`controller.py` из доков покрыты правилами
- [ ] `model-routing.md` описывает tier critical (sonnet/xhigh при risk≥10 и algorithm≥20) и правило risk≥8 → минимум balanced; сверено с `DEFAULT_POLICY`
- [ ] каталог бэкапов дашборда 0700, файлы 0600 (POSIX); остаются 5 последних на slug; тест на права и очистку
- [ ] CI запускает `python -m compileall -q skills/autopilot/tools tests tools`
- [ ] `python3 -m unittest discover -s tests` целиком зелёный
