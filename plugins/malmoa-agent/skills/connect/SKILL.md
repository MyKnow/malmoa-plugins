---
name: connect
description: Install the MALMOA runtime, log in on this device and connect the current local project to its MALMOA server.
---

# Connect MALMOA

Locate this plugin's root: two parents above this SKILL.md. Use its bundled `scripts/malmoa_plugin.py` with Python 3.12 or newer. On Claude Code the host also provides `CLAUDE_PLUGIN_ROOT`. Resolve an absolute path; do not assume the shell starts in the plugin directory.

1. Inspect the current workspace and `malmoa.yaml`. If already connected, use `status --workspace <absolute workspace> --client <codex|claude>` and reuse the existing OS-protected login. Do not recreate healthy profiles or copy another user's credentials.
2. If the runtime is missing, run `install`. This verifies the packaged wheel and lock hashes and installs `malmoa-mcp` using `uv`. Obtain uv from Astral's official instructions if absent; do not run an unreviewed downloaded script.
3. For a new connection, obtain the intended MALMOA server, project ID and source ID from the user or existing manifest. Never infer project identity from its name or a remembered repository. Existing `malmoa.yaml` supplies the complete binding when all three flags are omitted.
4. The human runs this in their own terminal (substitute the actual plugin script, workspace and IDs):

   `python3 <plugin>/scripts/malmoa_plugin.py connect --workspace <workspace> --client <codex|claude> --server <origin> --project-id <id> --source-id <id> --login --allow-external-context`

   The email/password prompt is handled by the runtime with hidden password input. Never ask for, enter or record passwords in the agent conversation, tool arguments, environment variables or plugin settings. Explain that connecting authorizes eligible project Context to be sent to that host provider. Use `--for-migration` for an existing project whose documents will be reviewed and migrated.
5. Project setup writes a secret-free `malmoa.yaml`, managed entrypoint instructions, project-local MCP and supported collection hooks. Inspect generated changes and preserve existing user settings. Follow the host's normal MCP/hook trust approval. Reload the host, run status, then read current Context through MCP.

The native plugin is reusable across repositories. Credentials belong to this device and host; MCP and collection hooks bind to this workspace. Installing the native plugin alone does not grant access to any project or prove automatic collection. Use the migrate workflow for historical documents and the context workflow for ongoing server-authoritative work.
