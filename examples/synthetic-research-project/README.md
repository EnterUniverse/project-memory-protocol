# Synthetic research project

This fictional example studies whether a deterministic parser can recover color names from short
sentences. It exists only to demonstrate memory structure; it contains no real user or project data.

Suggested exercise:

```bash
cp -R examples/synthetic-research-project /tmp/color-parser-study
cd /tmp/color-parser-study
pmem init
```

Add the statement “The baseline misses hyphenated color names” to `CURRENT.md`, record it as a
hypothesis, index the memory, and create a recovery probe for “hyphenated colors”.

