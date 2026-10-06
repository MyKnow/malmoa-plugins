---
name: update
description: Check for and install the latest Durumari plugin release without changing project connections.
---

# Update Durumari

Use `durumari-mcp update --check` to check the server declared during installation.
Use `durumari-mcp update` when the user asks to update. A downloaded standalone
installer also supports `update --server <HTTPS origin> --client codex|claude|both`.

Keep the normal host trust approval. Restart the host or begin a new session after
successful installation. Read the command result before claiming the installed
version. If it reports recovery or a partial installation, show that state.
On Windows, the installed CLI starts a separate installer and reports `started`.
Check `durumari-mcp update --status` until it reports `completed` or `failed`.
Starting the installer is not proof that an update completed. A downloaded
standalone installer runs synchronously and can recover an older CLI version.
Never remove project profiles, credentials, capture queues or connection files.

If this plugin was installed directly from a Git catalog, use the host's normal
marketplace refresh and plugin update commands. Do not edit its private cache.

Use the returned independent `completion_command` or read `status_file` while Windows replaces the runtime. The regular CLI can be temporarily unavailable. Current install-diagnostic.json describes the latest completed or failed attempt; last-install-failure.json retains the previous failure. Safe reason codes classify recognized command output without disclosing it; unclassified failures require opt-in local debug diagnostics.
