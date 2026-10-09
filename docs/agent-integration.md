# Using `pmem` with an AI agent

`pmem` does not depend on a particular agent. A project can add the following to its agent
instructions:

```text
At the start of a session, read `.project-memory/RECOVERY.md` and
`.project-memory/WORKING_SET.md`. Use `pmem compile --query "..."` for the current task.
Read `CURRENT.md` and `OPEN_LOOPS.md` when recent or unfinished work matters.
Check live code, data, artifacts, processes, and logs before making current-state claims.
Before handoff, update the relevant notes, run `pmem archive sync` for registered sources,
and run `pmem audit --full-hash`.
```

Do not inject every memory file into every prompt. Start with orientation and focused retrieval; use
the startup and full profiles only when the task needs broader history.

Agent-written notes should not automatically become verified claims. A verified claim needs an
evidence link that another session can inspect.
