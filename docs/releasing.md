# Release procedure

1. Run tests and static analysis.
2. Run the built-in privacy scan and a private, project-specific blocklist.
3. Search the complete Git history and object set for forbidden identifiers.
4. Build sdist and wheel in a clean environment.
5. Inspect both archive manifests and extract them into a temporary directory for a second scan.
6. Run `twine check dist/*` and install the wheel into a fresh environment.
7. Confirm version agreement across package metadata, changelog, and citation metadata.
8. Review repository visibility, branch protection, security reporting, and release notes.
9. Create a signed or annotated version tag only after all checks pass.

Do not rewrite a private repository into a public one. Begin with a clean public history so deleted
private files, commit messages, authorship metadata, and paths cannot remain in reachable objects.

