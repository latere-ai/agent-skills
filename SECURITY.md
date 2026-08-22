# Security policy

## Supported versions

Security fixes are applied to the latest `main` branch. The project does not
currently maintain release branches.

## Report a vulnerability

Do not open a public issue for a vulnerability that could put users or their
repositories at risk.

Use [GitHub private vulnerability reporting](https://github.com/latere-ai/agent-skills/security/advisories/new)
to send the maintainers:

- the affected skill, script, or installation path;
- the conditions needed to reproduce the problem;
- the likely impact on a user's machine, credentials, or repository;
- a minimal proof of concept when it is safe to share; and
- any mitigation or fix you have already identified.

Relevant reports include unsafe installer behavior, path traversal,
unintentional credential exposure, instructions that can cause destructive
actions without consent, and supply-chain risks in distributed skill content.

Please allow maintainers to investigate before publishing details. We will
coordinate disclosure based on the severity and availability of a fix. This
project does not promise a fixed response or resolution time.

For non-sensitive defects, use the
[bug report form](https://github.com/latere-ai/agent-skills/issues/new?template=bug.yml).
