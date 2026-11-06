# 02 — Хук `git`: пути к git, `bash -c`, `restore`, `checkout .`, `clean`

**Требования:** R22a, R22o
**Зависит от:** —
**Зона:** `skills/autopilot/tools/claude_agent_guard.py` · `tests/test_guard_forms.py`
**Волна:** 1
**Ревью:** нет
**Модель:** обычная

## Что должно заработать

Хук строгого прогона отклоняет в Bash-вызовах субагентов не только `git stash`, но и `git.exe stash`, `/usr/bin/git stash`, `bash -c "git stash"`, `git restore .`, `git checkout .`, `git clean -fd`. Обычные `git commit --only`, `git status`, `git diff` проходят, слово `stash` в кавычках и в сообщении коммита не срабатывает.

Читать сначала: `interfaces.md` («claude_agent_guard.py»), `spec.md`, `notes.md` — в папке прогона. Существующие случаи (`git stash`, `git stash pop`, `git reset --hard`, кавычки, комментарии `#`, экранирование) остаются как были.

## Из брифа, дословно

> «Хук отклоняет также `git.exe stash`, `/usr/bin/git stash`, `bash -c "git stash"`, `git restore .`, `git checkout .`, `git clean -fd` (по границам команды вне кавычек, как уже сделано для `git stash`).»
> «Тесты: каждая форма отклоняется; `git commit --only`, `git status`, `git diff` проходят; слово `stash` в кавычках и в сообщении коммита не срабатывает.»

## Разделы спецификации

«Решение» (R22a, R22o), «Решения по реализации» (хук `git`), «Вне рамок».

## Критерии приёмки

- [ ] `bash_decision` отклоняет `git.exe stash`, `GIT.EXE stash`, `/usr/bin/git stash`, `C:/Program Files/Git/cmd/git.exe stash` (тест на каждую форму)
- [ ] `bash_decision` отклоняет `bash -c "git stash"`, `sh -c 'git reset --hard'`, `bash -lc "git stash"`, вложенный `bash -c "sh -c 'git stash'"` (тест); `echo "bash -c git"` и `bash script.sh` не отклоняются
- [ ] Отклоняются `git restore .`, `git restore --staged .`, `git checkout .`, `git clean -fd`, `git clean -df`, `git clean -xdf`, `git clean --force` (тест на каждую форму); `git clean -n` и `git clean --dry-run` проходят
- [ ] Проходят `git commit --only a.py -m x`, `git status`, `git diff`, `git diff --cached --stat`, `git log --oneline -3`, `git restore a.py`, `git checkout main` (тест)
- [ ] Слово `stash` и фразы `git stash` / `git restore .` внутри кавычек, в сообщении коммита и в `#`-комментарии не срабатывают: `git commit -m "no git stash here"`, `echo "git clean -fd"` проходят (тест)
- [ ] Формы после разделителей вне кавычек отклоняются: `echo a && git.exe stash`, `ls; bash -c "git restore ."`, `git status | git clean -fd` (тест)
- [ ] Полный прогон `python3 -m unittest discover -s tests` зелёный
