# Privacy and limitations

## Sensitive material

- conversations and tool traces;
- names, email addresses, usernames, hostnames, and absolute paths;
- credentials and access tokens;
- unpublished code, research results, datasets, and decisions;
- information retained in Git history after deletion from the working tree.

## Common risks

1. Publishing a filtered copy of a private repository while sensitive history remains reachable.
2. Including real memory content in examples or tests.
3. Committing the local source registry or raw archive.
4. Leaking identifiers through fixtures, screenshots, package metadata, or generated artifacts.
5. Treating automated scanning as proof of privacy.

## Safeguards

- Build public distributions in a clean-room repository.
- Require explicit evidence-source registration; never scan a home directory by default.
- Ignore the archive, index, source registry, and private blocklist by default.
- Use synthetic fixtures with reserved example names and domains.
- Run built-in pattern checks plus a project-specific blocklist.
- Inspect the complete Git object set and the built source/wheel archives before release.
- Publish only after a human reviews the release diff and repository settings.

## Non-goals

The privacy scanner is not a data-loss-prevention system. It cannot recognize every confidential
concept, infer contractual restrictions, or prove that prose is anonymized. It is a final check for
common leaks and project-specific terms, not a substitute for review.
