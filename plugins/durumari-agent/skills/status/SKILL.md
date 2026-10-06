---
name: status
description: Verify Durumari login, project binding, current Context access and local collection status for this workspace.
---

# Verify connection

Read the current workspace's `durumari.yaml`. When the project's `durumari_project` MCP is loaded, call `durumari_project_status` and check its project ID, pending records, quarantine and server time. Read a current authorized Context to prove live access.

For installation diagnostics, locate this plugin's root (two parents above this SKILL.md), then run its `scripts/durumari_plugin.py status --workspace <absolute current workspace> --client <codex|claude>` with Python 3.12 or newer. Choose the actual host, never the other client's credential profile. The command adopts the existing connection for diagnosis and does not reinstall, log in or rewrite project files.

Distinguish native plugin registration, stored credentials, live MCP access and observed automatic capture. A configuration file or `ready: true` alone does not prove an actual model turn was captured. Report failures without exposing raw credential storage or account data.

`project_repository_mismatch_reconnect` is a paused integration, not a blocked conversation. Status returns local diagnostics with `ready: false` and never reads Context or sends pending records while the repository differs. Ordinary chat/tools, diagnosis and browser reconnect remain available. Do not manually edit `repository_id`, disable hook approvals, or claim local diagnostics verify server access.

Before Git initialization, moving a connected folder, or making an independent repository, run `scripts/durumari_plugin.py preflight --workspace <absolute workspace> --client <codex|claude> --change <git-init|move|detach>`. Preserve connection files and pending records, prepare the final folder/Git structure, then reconnect if indicated. The preflight is read-only and conservative for moves and independent repositories.

For post-connection, post-migration and ongoing-capture checks, run the [automatic host capture verification](references/automatic-capture.md) gate. Inspect effective per-hook state overrides as well as generated definitions; continue through a real host turn, acknowledgement and independent server read when permitted.
