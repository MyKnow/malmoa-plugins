"""Portable native-plugin setup. Credentials stay in the MALMOA OS profile store."""

import argparse
import hashlib
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

PLUGIN_ROOT = Path(__file__).resolve().parents[1]


class SetupError(Exception):
    pass


class PluginParser(argparse.ArgumentParser):
    def error(self, message):
        # Invalid command lines can contain accidentally pasted credentials.
        raise SetupError("invalid_plugin_arguments")


def run(command, *, capture=False):
    # Inherit stdin only for the human's interactive login. Never collect its output.
    result = subprocess.run(
        command, encoding="utf-8", errors="replace", capture_output=capture, check=False
    )
    if result.returncode:
        raise SetupError("setup_command_failed")
    return result.stdout.strip() if capture else result.returncode


def uv_executable():
    executable = shutil.which("uv")
    if not executable:
        raise SetupError("uv_required_install_from_astral_documentation")
    return executable


def runtime_python():
    directory = Path(run([uv_executable(), "tool", "dir"], capture=True)) / "malmoa-mcp"
    executable = directory / ("Scripts/python.exe" if sys.platform == "win32" else "bin/python3")
    if not executable.is_file():
        raise SetupError("runtime_not_installed_run_plugin_install")
    return str(executable)


def verify_bundle(directory):
    try:
        metadata = json.loads((directory / "bundle.json").read_text(encoding="utf-8"))
        files = metadata["files"]
        version = metadata["version"]
        wheel = f"malmoa_mcp-{version}-py3-none-any.whl"
        if (
            metadata.get("schema_version") != 1
            or metadata.get("package") != "malmoa-mcp"
            or not isinstance(version, str)
            or not re.fullmatch(r"\d+\.\d+\.\d+", version)
            or not isinstance(files, dict)
            or set(files) != {wheel, "requirements.txt"}
        ):
            raise SetupError("invalid_runtime_bundle")
        for name, expected in files.items():
            path = directory / name
            if (
                not isinstance(expected, str)
                or not re.fullmatch(r"[0-9a-f]{64}", expected)
                or path.is_symlink()
                or hashlib.sha256(path.read_bytes()).hexdigest() != expected
            ):
                raise SetupError("runtime_bundle_integrity_failed")
        return directory / wheel, directory / "requirements.txt"
    except (OSError, ValueError, KeyError, TypeError):
        raise SetupError("invalid_runtime_bundle_build_before_install") from None


def parser():
    result = PluginParser(description=__doc__)
    commands = result.add_subparsers(dest="command", required=True, parser_class=PluginParser)
    commands.add_parser("install", help="Install the bundled, locked MCP runtime using uv")
    for name in ("status", "connect", "migrate"):
        command = commands.add_parser(name)
        command.add_argument("--workspace", required=True)
        command.add_argument("--client", choices=("codex", "claude"), required=True)
        if name == "connect":
            command.add_argument("--server")
            command.add_argument("--project-id")
            command.add_argument("--source-id")
            command.add_argument("--login", action="store_true")
            command.add_argument("--allow-external-context", action="store_true")
            command.add_argument("--for-migration", action="store_true")
        if name == "migrate":
            command.add_argument("--paths", nargs="+", default=["docs"])
            command.add_argument("--include-resources", action="store_true")
            command.add_argument("--apply", action="store_true")
            command.add_argument("--bundle")
            command.add_argument("--output")
    return result


def execute(args):
    if args.command == "install":
        wheel, constraints = verify_bundle(PLUGIN_ROOT / "runtime")
        run(
            [
                uv_executable(),
                "tool",
                "install",
                str(wheel),
                "--python",
                "3.12",
                "--constraints",
                str(constraints),
                "--reinstall-package",
                "malmoa-mcp",
            ]
        )
        print(json.dumps({"runtime": "installed", "credentials": "not_changed"}))
        return 0
    root = Path(args.workspace).resolve(strict=True)
    if not root.is_dir():
        raise SetupError("workspace_directory_required")
    if args.command == "connect":
        supplied = [args.server, args.project_id, args.source_id]
        if not all(supplied) and (any(supplied) or not (root / "malmoa.yaml").is_file()):
            raise SetupError("project_binding_arguments_required")
        if args.login and not args.allow_external_context:
            raise SetupError("external_context_consent_required")
        if args.login and not sys.stdin.isatty():
            raise SetupError("login_requires_human_terminal")
    command = [runtime_python(), "-m", "malmoa_mcp"]
    if args.command == "status":
        return run(command + ["project-doctor", "--workspace", str(root), "--client", args.client])
    if args.command == "connect":
        command += ["project-init", "--workspace", str(root), "--hosts", args.client, "--apply"]
        for option, value in (
            ("--gateway-origin", args.server),
            ("--project-id", args.project_id),
            ("--source-id", args.source_id),
        ):
            if value:
                command += [option, value]
        for option in ("login", "allow_external_context", "for_migration"):
            if getattr(args, option):
                command.append("--" + option.replace("_", "-"))
        return run(command)
    command += [
        "project-import",
        "--workspace",
        str(root),
        "--client",
        args.client,
        "--paths",
        *args.paths,
    ]
    for option in ("include_resources", "apply"):
        if getattr(args, option):
            command.append("--" + option.replace("_", "-"))
    for option in ("bundle", "output"):
        if getattr(args, option):
            command += ["--" + option, getattr(args, option)]
    return run(command)


def main():
    try:
        return execute(parser().parse_args())
    except SetupError as error:
        print(json.dumps({"error": str(error)}), file=sys.stderr)
        return 1
    except (OSError, ValueError):
        print(json.dumps({"error": "plugin_setup_failed"}), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
