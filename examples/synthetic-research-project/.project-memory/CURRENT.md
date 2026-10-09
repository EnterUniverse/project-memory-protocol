# Current state

## Findings

The baseline misses a color when it appears next to a hyphen. The current token-boundary rule treats
the hyphenated label as one token.

## Next steps

Test whether splitting on punctuation introduces false positives in product identifiers.
