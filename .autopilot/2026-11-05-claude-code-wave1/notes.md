# Заметки по коду (составлены оркестратором: агент-разведчик этого прогона до нового чата недоступен)

- Навык — `skills/autopilot/` (фазы `phases/`, промпты `prompts/`, инструменты `tools/`); в проекте `.autopilot/*.py` — копии инструментов, правятся только в `skills/autopilot/tools/`.
- Отпечаток таска: `tools/ap.py` `publish_tickets` (строка ~420: `hashlib.sha256(open(p,"rb").read())`; сравнение ~422), `plan-models` (~1375), `tools/codex_dispatch.py:131`. Тесты-образцы: `tests/test_ap.py:1293`, `tests/test_codex_dispatch.py:53` (отпечаток по сырым байтам — должен остаться принятым как старый).
- Подкоманды `ap.py`: `main()` ~2333, ветвление по `cmd` (`ticket` → `cmd_ticket` ~1510, `tickets`, `check-plan`, `init` и т.д.).
- Хук: `tools/claude_agent_guard.py` — `decision(payload, root)` (Agent|Task и `WRITE_TOOLS`), `install_hook(root)` ставит два PreToolUse-хука (`Agent|Task` и запись) и `permissions.deny Agent(fork)`; активен только пока есть незавершённый строгий прогон. Bash в нём не рассматривается; `claude_attest.py` ставится на `*` и в полезной нагрузке субагента получает `agent_type`/`agent_id`.
- Шаблоны путей машины: `tests/test_no_machine_data.py` (`PATTERNS`).
- Документы: `docs/autopilot/claude-code.md`, `docs/autopilot/model-routing.md`; журнал изменений `CHANGELOG.md` (раздел сверху — 2.7.0).
- Проверено по changelog (code.claude.com, 2026-11-05), отличия 2.1.302 → 2.1.311, важные для нас: 2.1.310 — Windows: PreToolUse-хук пропускал вызов, если нет Git Bash и команда хука состоит только из строк в кавычках; 2.1.305 — Windows: на части томов отказ любого вызова инструмента, и пути scratchpad росли с длиной пути проекта (лимит 260 символов). Записи 2.1.297 и 2.1.298 на странице отсутствуют.
