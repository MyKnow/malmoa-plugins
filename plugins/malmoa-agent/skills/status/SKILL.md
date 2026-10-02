---
name: status
description: Verify MALMOA login, project binding, current Context access and local collection status for this workspace.
---

# Verify connection

Read the current workspace's `malmoa.yaml`. When the project's `malmoa_project` MCP is loaded, call `malmoa_project_status` and check its project ID, pending records, quarantine and server time. Read a current authorized Context to prove live access.

For installation diagnostics, locate this plugin's root (two parents above this SKILL.md), then run its `scripts/malmoa_plugin.py status --workspace <absolute current workspace> --client <codex|claude>` with Python 3.12 or newer. Choose the actual host, never the other client's credential profile. The command adopts the existing connection for diagnosis and does not reinstall, log in or rewrite project files.

Distinguish native plugin registration, stored credentials, live MCP access and observed automatic capture. A configuration file or `ready: true` alone does not prove an actual model turn was captured. Report failures without exposing raw credential storage or account data.
