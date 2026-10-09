# Example: color-name parser

This small fictional project shows a populated `.project-memory/` directory. It studies whether a
deterministic parser can recover color names from short sentences; all content is synthetic.

From this directory, try:

```bash
pmem index
pmem compile --query "What is still wrong with hyphenated color names?"
pmem drill
pmem audit --full-hash
```

The query should recover both the active finding and the decision behind the current parser. The
recovery drill checks that this path remains searchable.
