# Evaluation

Memory quality is evaluated as recovery behavior rather than compression ratio.

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

PMP does not prescribe one universal score. Projects should report probe coverage, archive hash
validity, claim-schema validity, context-pack omissions, and the evidence gaps that remain.

