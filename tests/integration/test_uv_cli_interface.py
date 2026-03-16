"""
Comprehensive integration test for UV CLI interface.

This test implements a representative subset of the `uv` tool interface to exercise
many argparse features working together:
- Root parser with multiple argument groups
- 2 levels of nested subparsers (pip/python -> their subcommands)
- All action types: store, store_true, store_false, append, count, choices
- Various nargs: *, +, ?
- Mutually exclusive groups at multiple levels
- Both required and optional arguments
- Positional and optional arguments
- Default values
- Argument groups for organization
"""

import pytest
from nicegui import ui
from nicegui.testing import User

from nicegooey.argparse import nice_gooey_argparse_main, NgArgumentParser
from nicegooey.argparse.main import main_instance


@pytest.mark.nicegui_main_file(__file__)
async def test_uv_cli_interface(user: User) -> None:
    """
    Comprehensive integration test that verifies complex argparse structures work correctly in NiceGooey.

    Tests a realistic CLI tool interface with nested subparsers, various action types,
    mutually exclusive groups, and both required and optional arguments.
    """

    await user.open("/")

    # === PART 1: Verify root-level global options ===

    # Verify all argument groups are visible
    await user.should_see("Cache Options")
    await user.should_see("Python Options")
    await user.should_see("Global Options")

    # Verify initial namespace values for global options
    assert main_instance.namespace.verbose == 0
    assert main_instance.namespace.color == "auto"
    assert main_instance.namespace.no_cache is False
    assert main_instance.namespace.quiet is False
    assert main_instance.namespace.offline is False
    assert main_instance.namespace.native_tls is False

    # Test count action (verbose)
    verbose_input = user.find(ui.number)
    verbose_input.type("3")
    assert main_instance.namespace.verbose == 3

    # Test boolean flags
    no_cache_checkbox = user.find(ui.checkbox)
    no_cache_checkbox.click()
    assert main_instance.namespace.no_cache is True

    # === PART 2: Verify top-level subparser tabs ===

    # All top-level subparser tabs should be visible
    await user.should_see("pip")
    await user.should_see("python")
    await user.should_see("venv")
    await user.should_see("run")
    await user.should_see("sync")

    # === PART 3: Test nested pip subparsers ===

    # Click on pip tab
    pip_tab = user.find(marker="ng-subparser-tab-pip")
    pip_tab.click()

    # Verify nested pip subparser tabs are visible
    await user.should_see("install")
    await user.should_see("uninstall")
    await user.should_see("freeze")
    await user.should_see("list")

    # === PART 4: Test nested python subparsers ===

    # Click on python tab
    python_tab = user.find(marker="ng-subparser-tab-python")
    python_tab.click()

    # Verify nested python subparser tabs
    await user.should_see("list")
    await user.should_see("install")
    await user.should_see("find")
    await user.should_see("pin")

    # === PART 5: Test venv command ===

    venv_tab = user.find(marker="ng-subparser-tab-venv")
    venv_tab.click()

    # Verify venv command is selected
    assert main_instance.namespace.command == "venv"

    # Verify venv-specific options are visible
    await user.should_see("path")
    await user.should_see("seed")
    await user.should_see("system-site-packages")

    # === PART 6: Test run command ===

    run_tab = user.find(marker="ng-subparser-tab-run")
    run_tab.click()

    assert main_instance.namespace.command == "run"
    await user.should_see("command")
    await user.should_see("args")
    await user.should_see("isolated")

    # === PART 7: Test sync command ===

    sync_tab = user.find(marker="ng-subparser-tab-sync")
    sync_tab.click()

    assert main_instance.namespace.command == "sync"

    # Verify sync argument group
    await user.should_see("Sync Options")
    await user.should_see("dev")
    await user.should_see("all-extras")


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
def main():
    """Build the UV CLI interface using argparse."""
    parser = uv_parser()
    parser.parse_args()


if __name__ == "__main__":
    main()
