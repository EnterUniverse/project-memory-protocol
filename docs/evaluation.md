# Recovery checks

A useful memory system should help a new session recover the right information. A context file is
not useful merely because it is small.

Useful probes ask whether a fresh agent can recover:

- the current objective and binding constraints;
- active blockers and unfinished commitments;
- why a consequential decision was made;
- a bounded negative result and what remains untested;
- the evidence locator for an implementation claim;
- the fact that live state must still be checked.

Each project can encode representative questions in `recovery_probes.json`. A retrieval change
should preserve or improve these probes. The orient profile should remain materially smaller than
startup, while full recovery should remain complete over curated sources.

There is no universal score. Useful signals include probe coverage, valid archive hashes, valid
claim records, explicit context-pack omissions, and any evidence gaps that remain.
