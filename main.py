import argparse
import time


from nicegooey.argparse import nice_gooey_argparse_main, ArgumentParserConfig, NgArgumentParser


def process(parser: argparse.ArgumentParser, args: argparse.Namespace):
    print(args)
    time.sleep(1)
    print("wake up!")


@nice_gooey_argparse_main(patch_argparse=False)
def main1(*args, **kwargs):
    parser = NgArgumentParser()
    parser.add_argument("--name", type=str, help="Your name", required=True)
    parser.add_argument("--email", type=str, help="Your email", required=True)
    parser.add_argument("--age", type=int, help="Your age", required=True)
    # parser=uv_parser()
    ns = parser.parse_args()
    print(ns)


def uv_parser() -> NgArgumentParser:
    parser = NgArgumentParser(description="An extremely fast Python package manager")

    # ========== Root Parser: Global Argument Groups ==========

    # Cache Options Group
    cache_group = parser.add_argument_group(title="Cache Options")
    cache_group.add_argument(
        "--no-cache", action="store_true", help="Avoid reading from or writing to the cache"
    )
    cache_group.add_argument("--cache-dir", type=str, help="Path to the cache directory")

    # Python Options Group (mutually exclusive)
    python_group = parser.add_argument_group(title="Python Options")
    me_python = python_group.add_mutually_exclusive_group()
    me_python.add_argument(
        "--managed-python",
        action="store_true",
        dest="managed_python",
        help="Require use of uv-managed Python versions",
    )
    me_python.add_argument(
        "--no-managed-python",
        action="store_false",
        dest="managed_python",
        help="Disable use of uv-managed Python versions",
    )

    # Global Options Group
    global_group = parser.add_argument_group(title="Global Options")
    global_group.add_argument(
        "--verbose",
        "-v",
        action="count",
        default=0,
        required=True,
        help="Use verbose output (can be repeated)",
    )
    global_group.add_argument("--quiet", "-q", action="store_true", help="Do not print any output")
    global_group.add_argument(
        "--color",
        choices=["auto", "always", "never"],
        default="auto",
        required=True,
        help="Control colors in output",
    )
    global_group.add_argument(
        "--native-tls", action="store_true", help="Use platform's native TLS certificates"
    )
    global_group.add_argument("--offline", action="store_true", help="Run without network access")

    # ========== Top-Level Subcommands ==========

    subparsers = parser.add_subparsers(dest="command", help="Commands", required=True)

    # ===== 1. PIP COMMAND (with nested subparsers) =====

    parser_pip = subparsers.add_parser("pip", help="Manage Python packages with pip-compatible interface")
    pip_subparsers = parser_pip.add_subparsers(dest="pip_command", help="pip commands", required=True)

    # pip install
    parser_install = pip_subparsers.add_parser("install", help="Install packages")
    parser_install.add_argument("packages", nargs="*", type=str, help="Packages to install")
    parser_install.add_argument(
        "--requirement",
        "-r",
        action="append",
        dest="requirements",
        type=str,
        help="Install from requirements file",
    )
    parser_install.add_argument(
        "--editable",
        "-e",
        action="append",
        dest="editables",
        type=str,
        help="Install package in editable mode",
    )
    install_system_group = parser_install.add_mutually_exclusive_group()
    install_system_group.add_argument(
        "--system", action="store_true", dest="system", help="Install into system Python environment"
    )
    install_system_group.add_argument(
        "--no-system", action="store_false", dest="system", help="Do not install into system Python"
    )
    parser_install.add_argument("--extra", action="append", type=str, help="Include optional dependencies")

    # pip uninstall
    parser_uninstall = pip_subparsers.add_parser("uninstall", help="Uninstall packages")
    parser_uninstall.add_argument("packages", nargs="+", type=str, help="Packages to uninstall")
    parser_uninstall.add_argument("--yes", "-y", action="store_true", help="Skip confirmation prompt")

    # pip freeze
    parser_freeze = pip_subparsers.add_parser("freeze", help="List installed packages in requirements format")
    parser_freeze.add_argument(
        "--exclude-editable", action="store_true", help="Exclude editable package from output"
    )

    # pip list
    parser_list = pip_subparsers.add_parser("list", help="List packages in tabular format")
    parser_list.add_argument(
        "--format",
        choices=["columns", "freeze", "json"],
        default="columns",
        required=True,
        help="Select output format",
    )

    # ===== 2. PYTHON COMMAND (with nested subparsers) =====

    parser_python = subparsers.add_parser("python", help="Manage Python versions and installations")
    python_subparsers = parser_python.add_subparsers(
        dest="python_command", help="python commands", required=True
    )

    # python list
    parser_py_list = python_subparsers.add_parser("list", help="List available Python installations")
    parser_py_list.add_argument("--all", action="store_true", help="List all Python versions")
    parser_py_list.add_argument("--only-installed", action="store_true", help="Only show installed versions")

    # python install
    parser_py_install = python_subparsers.add_parser("install", help="Download and install Python")
    parser_py_install.add_argument("version", type=str, help="Python version to install")
    parser_py_install.add_argument(
        "--force", "-f", action="store_true", help="Force reinstall if already installed"
    )

    # python find
    parser_py_find = python_subparsers.add_parser("find", help="Search for Python installation")
    parser_py_find.add_argument("version", type=str, help="Python version to find")

    # python pin
    parser_py_pin = python_subparsers.add_parser("pin", help="Pin to specific Python version")
    parser_py_pin.add_argument("version", type=str, help="Python version to pin")

    # ===== 3. VENV COMMAND =====

    parser_venv = subparsers.add_parser("venv", help="Create a virtual environment")
    parser_venv.add_argument("path", nargs="?", type=str, default=".venv", help="Path to virtual environment")
    parser_venv.add_argument("--python", "-p", type=str, help="Python version to use")
    parser_venv.add_argument("--seed", action="store_true", help="Install seed packages")
    parser_venv.add_argument(
        "--system-site-packages", action="store_true", help="Give venv access to system site packages"
    )

    # ===== 4. RUN COMMAND =====

    parser_run = subparsers.add_parser("run", help="Run a command or script")
    parser_run.add_argument("command", type=str, help="Command to run")
    parser_run.add_argument("args", nargs="*", type=str, help="Arguments for the command")
    parser_run.add_argument(
        "--with", action="append", dest="with_packages", type=str, help="Run with additional packages"
    )
    parser_run.add_argument("--isolated", action="store_true", help="Run in isolated environment")

    # ===== 5. SYNC COMMAND =====

    parser_sync = subparsers.add_parser("sync", help="Update the project environment")

    # Sync Options Group
    sync_group = parser_sync.add_argument_group(title="Sync Options")
    sync_group.add_argument("--extra", action="append", type=str, help="Include extra dependencies")
    sync_group.add_argument("--dev", action="store_true", help="Include dev dependencies")
    sync_group.add_argument("--all-extras", action="store_true", help="Include all extras")

    # Mutually exclusive frozen group
    sync_me_group = parser_sync.add_mutually_exclusive_group()
    sync_me_group.add_argument(
        "--frozen", action="store_true", dest="frozen", help="Use exact versions from lockfile"
    )
    sync_me_group.add_argument(
        "--no-frozen", action="store_false", dest="frozen", help="Allow version resolution"
    )

    return parser


@nice_gooey_argparse_main(patch_argparse=False)
def main2(required: bool = False, nargs: int | str | None = None):
    config = ArgumentParserConfig(argument_vp_width="w-4xl")
    parser = NgArgumentParser()
    parser.nicegooey_config = config

    parser.add_argument("--name", type=str, default="World", help="Your name", required=required, nargs=nargs)
    parser.add_argument("--age", "-a", type=int, help="Your age", required=required, nargs=nargs)
    parser.add_argument("--disable-meme", "-dm", action="store_true", help="Disable memes", required=required)
    parser.add_argument("--favorite-food", choices=["banana", "apple"], required=required, nargs=nargs)
    group1 = parser.add_argument_group(title="gruppo")
    group1.add_argument(
        "--level",
        type=int,
        choices=range(1, 6),
        help="Pick a level from 1 to 5",
        required=required,
        nargs=nargs,
    )
    parser.add_argument(
        "--append_const",
        action="append_const",
        const="NiceGooey",
        help="Append a constant value",
        required=required,
    )
    parser.add_argument(
        "--append", action="append", type=str, help="Append multiple values", required=required, nargs=nargs
    )
    group2 = parser.add_mutually_exclusive_group(required=required)
    group2.add_argument("--asdf", nargs=nargs)
    group3 = group1.add_mutually_exclusive_group(required=required)

    def validate_xxx(v: str) -> str:
        if len(v) < 3:
            raise ValueError()
        else:
            return v

    group3.add_argument("--xxx", type=validate_xxx, nargs=nargs)
    group3.add_argument("--yyy", nargs=nargs)

    subps = parser.add_subparsers(required=required)
    subp1 = subps.add_parser("sub1")
    subp1.add_argument("--sub1a", required=required, nargs=nargs)
    subp1.add_argument("--sub1b", type=float, required=required, nargs=nargs)
    subp2 = subps.add_parser("sub2")
    subp2.add_argument("--sub2a", type=str, required=required, nargs=nargs)

    args = parser.parse_args()
    process(parser, args)


if __name__ in {"__main__", "__mp_main__"}:
    main1(required=False, nargs="*")
