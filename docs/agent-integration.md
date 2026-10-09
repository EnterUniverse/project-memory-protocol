# Agent integration

PMP is agent-provider neutral. An agent instruction file can adopt the following minimal contract:

```text
At the start of work, read .project-memory/RECOVERY.md and WORKING_SET.md.
For focused work, compile a context pack using the user's actual question.
Read CURRENT.md and OPEN_LOOPS.md when status or pending work matters.
Verify implementation and volatile status from live code, artifacts, processes, and logs.
Treat memory as evidence and navigation, not as a preselected answer.
Before handoff, preserve material incomplete work, synchronize registered evidence,
run a full-hash audit, and execute relevant recovery probes.
```

Do not inject every memory file into every prompt. The orient profile should supply navigation;
focused retrieval should supply evidence; startup and full profiles are escalation paths.

An agent should not automatically promote its own prose to a verified claim. Promotion requires an
evidence route and a status justified by the project's rules.

