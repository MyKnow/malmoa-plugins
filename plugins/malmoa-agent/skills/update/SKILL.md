---
name: update
description: Check for and install the latest MALMOA plugin release without changing project connections.
---

# Update MALMOA

Use `malmoa-mcp update --check` to check the server declared during installation.
Use `malmoa-mcp update` when the user asks to update. A downloaded standalone
installer also supports `update --server <HTTPS origin> --client codex|claude|both`.

Keep the normal host trust approval. Restart the host or begin a new session after
successful installation. Read the command result before claiming the installed
version. If it reports recovery or a partial installation, show that state.
On Windows, the installed CLI starts a separate installer and reports `started`.
Check `malmoa-mcp update --status` until it reports `completed` or `failed`.
Starting the installer is not proof that an update completed. A downloaded
standalone installer runs synchronously and can recover an older CLI version.
Never remove project profiles, credentials, capture queues or connection files.

If this plugin was installed directly from a Git catalog, use the host's normal
marketplace refresh and plugin update commands. Do not edit its private cache.
