"""Portable native-plugin setup. Credentials stay in the Durumari OS profile store."""

import argparse
import hashlib
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace
from urllib.parse import urlsplit

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
    directory = (
        Path(run([uv_executable(), "tool", "dir"], capture=True)) / "durumari-mcp"
    )
    executable = directory / (
        "Scripts/python.exe" if sys.platform == "win32" else "bin/python3"
    )
    if not executable.is_file():
        raise SetupError("runtime_not_installed_run_plugin_install")
    return str(executable)


def verify_bundle(directory):
    try:
        metadata = json.loads((directory / "bundle.json").read_text(encoding="utf-8"))
        files = metadata["files"]
        version = metadata["version"]
        wheel = f"durumari_mcp-{version}-py3-none-any.whl"
        if (
            metadata.get("schema_version") != 1
            or metadata.get("package") != "durumari-mcp"
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
        if "service" in metadata or tuple(map(int, version.split("."))) >= (0, 2, 9):
            bundled_server(directory)
        return directory / wheel, directory / "requirements.txt"
    except (OSError, ValueError, KeyError, TypeError):
        raise SetupError("invalid_runtime_bundle_build_before_install") from None


def bundled_server(directory=None):
    """Only the installed package supplies a default, never a different repository."""
    try:
        path = (directory or PLUGIN_ROOT / "runtime") / "bundle.json"
        if path.is_symlink() or path.stat().st_size > 16_384:
            raise ValueError
        service = json.loads(path.read_text(encoding="utf-8"))["service"]
        if (
            not isinstance(service, dict)
            or set(service) != {"schema_version", "gateway_origin"}
            or type(service["schema_version"]) is not int
            or service["schema_version"] != 1
        ):
            raise ValueError
        origin = service["gateway_origin"]
        if not isinstance(origin, str) or origin != origin.strip():
            raise ValueError
        parsed = urlsplit(origin)
        if (
            not parsed.hostname
            or parsed.username is not None
            or parsed.password is not None
            or parsed.path not in {"", "/"}
            or parsed.query
            or parsed.fragment
            or any(c.isspace() or ord(c) < 32 for c in origin)
            or (parsed.port is not None and not 1 <= parsed.port <= 65535)
            or not (
                parsed.scheme == "https"
                or (parsed.scheme == "http" and parsed.hostname in {"127.0.0.1", "::1"})
            )
        ):
            raise ValueError
        return origin.rstrip("/")
    except (OSError, ValueError, KeyError, TypeError):
        raise SetupError("invalid_plugin_service") from None


def parser():
    result = PluginParser(description=__doc__)
    commands = result.add_subparsers(
        dest="command", required=True, parser_class=PluginParser
    )
    commands.add_parser(
        "install", help="Install the bundled, locked MCP runtime using uv"
    )
    for name in ("status", "connect", "migrate", "preflight"):
        command = commands.add_parser(name)
        command.add_argument("--workspace", required=True)
        command.add_argument("--client", choices=("codex", "claude"), required=True)
        if name == "preflight":
            command.add_argument(
                "--change", choices=("git-init", "move", "detach"), required=True
            )
            command.add_argument("--target-workspace")
        if name == "connect":
            command.add_argument("--password-login", action="store_true")
            command.add_argument("--server")
            command.add_argument("--project-id")
            command.add_argument("--source-id")
            command.add_argument("--login", action="store_true")
            command.add_argument("--allow-external-context", action="store_true")
            command.add_argument("--for-migration", action="store_true")
            command.add_argument("--trust-workspace", action="store_true")
            command.add_argument("--reauth", action="store_true")
            command.add_argument("--create-workspace", action="store_true")
            command.add_argument("--requested-project")
        if name == "migrate":
            command.add_argument("--paths", nargs="+", default=["docs"])
            command.add_argument("--include-resources", action="store_true")
            command.add_argument("--reference-source-code", action="store_true")
            command.add_argument("--allow-incomplete", action="store_true")
            command.add_argument("--apply", action="store_true")
            command.add_argument("--bundle")
            command.add_argument("--output")
    return result


def require_guided_runtime(command):
    current = run(command + ["--version"], capture=True)
    if not isinstance(current, str) or not re.fullmatch(r"\d+\.\d+\.\d+", current):
        raise SetupError("guided_runtime_unavailable_update_plugin")
    if tuple(map(int, current.split("."))) < (0, 3, 6):
        raise SetupError("guided_runtime_unavailable_update_plugin")


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
                "durumari-mcp",
            ]
        )
        print(json.dumps({"runtime": "installed", "credentials": "not_changed"}))
        return 0
    root = Path(args.workspace).resolve()
    if args.command == "connect" and args.create_workspace and not root.exists():
        try:
            root.mkdir(parents=True, exist_ok=True)
        except OSError:
            raise SetupError("workspace_create_failed") from None
    if not root.is_dir():
        raise SetupError("workspace_directory_required")
    if args.command == "connect":
        guided = not args.project_id and not args.source_id
        supplied = [args.server, args.project_id, args.source_id]
        if not guided and not all(supplied):
            raise SetupError("project_binding_arguments_required")
        if not guided and args.login and not args.allow_external_context:
            raise SetupError("external_context_consent_required")
        if ((guided and args.password_login) or (not guided and args.login)) and not (
            sys.stdin.isatty()
        ):
            raise SetupError("login_requires_human_terminal")
        if args.reauth and not guided:
            raise SetupError("reauth_requires_guided_connection")
        server = args.server
        if guided and not server and not (root / "durumari.yaml").exists():
            server = bundled_server()
    try:
        python = runtime_python()
    except SetupError as error:
        if (
            args.command != "connect"
            or str(error) != "runtime_not_installed_run_plugin_install"
        ):
            raise
        execute(SimpleNamespace(command="install"))
        python = runtime_python()
    command = [python, "-m", "durumari_mcp"]
    if args.command == "status":
        return run(
            command
            + ["project-doctor", "--workspace", str(root), "--client", args.client]
        )
    if args.command == "preflight":
        command += [
            "project-preflight",
            "--workspace",
            str(root),
            "--client",
            args.client,
            "--change",
            args.change,
        ]
        if args.target_workspace:
            command += ["--target-workspace", args.target_workspace]
        return run(command)
    if args.command == "connect":
        if guided:
            try:
                require_guided_runtime(command)
            except SetupError:
                if sys.platform == "win32":
                    # The installed runtime may be in use by the host. Its existing
                    # update workflow hands replacement to a separate installer.
                    raise SetupError(
                        "runtime_update_required_then_restart_host"
                    ) from None
                # An older installed runtime can coexist with a newly installed plugin.
                # Replace only the runtime from the verified bundle; keep all profiles.
                execute(SimpleNamespace(command="install"))
                python = runtime_python()
                command = [python, "-m", "durumari_mcp"]
                try:
                    require_guided_runtime(command)
                except SetupError:
                    raise SetupError(
                        "guided_runtime_unavailable_update_plugin"
                    ) from None
            command += [
                "project-connect",
                "--workspace",
                str(root),
                "--client",
                args.client,
            ]
            if args.requested_project:
                command += ["--requested-project", args.requested_project]
            if not args.password_login:
                command.append("--browser-login")
            if server:
                command += ["--gateway-origin", server]
            for option in (
                "allow_external_context",
                "for_migration",
                "reauth",
                "trust_workspace",
            ):
                if getattr(args, option):
                    command.append("--" + option.replace("_", "-"))
            return run(command)
        command += [
            "project-init",
            "--workspace",
            str(root),
            "--hosts",
            args.client,
            "--apply",
        ]
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
    for option in (
        "include_resources",
        "reference_source_code",
        "allow_incomplete",
        "apply",
    ):
        if getattr(args, option):
            command.append("--" + option.replace("_", "-"))
    for option in ("bundle", "output"):
        if getattr(args, option):
            command += ["--" + option, getattr(args, option)]
    return run(command)


def main():
    try:
        return execute(parser().parse_args())
    except KeyboardInterrupt:
        print(
            "연결을 취소했습니다. 기존 로그인과 작업 기록은 유지됩니다.",
            file=sys.stderr,
        )
        return 130
    except SetupError as error:
        print(json.dumps({"error": str(error)}), file=sys.stderr)
        if str(error) == "runtime_update_required_then_restart_host":
            print(
                "연결 안내를 사용하려면 플러그인 update 절차를 완료한 뒤 "
                "호스트를 다시 시작해 주세요. 기존 로그인과 기록은 유지됩니다.",
                file=sys.stderr,
            )
        return 1
    except (OSError, ValueError):
        print(json.dumps({"error": "plugin_setup_failed"}), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
