#!/usr/bin/env python3
"""
uv CLI Interface Example
Replicates the uv command-line interface using argparse.
Does not implement actual functionality.
"""

import argparse


def create_uv_parser() -> argparse.ArgumentParser:
    """Create the main uv argument parser with all subcommands."""

    parser = argparse.ArgumentParser(
        prog="uv",
        description="An extremely fast Python package manager",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    # Global options
    parser.add_argument("-v", "--verbose", action="count", default=0, help="Enable verbose output")
    parser.add_argument("-q", "--quiet", action="count", default=0, help="Reduce output verbosity")
    parser.add_argument(
        "--color", choices=["auto", "always", "never"], default="auto", help="Control color output"
    )
    parser.add_argument("--no-progress", action="store_true", help="Hide progress outputs")
    parser.add_argument("--offline", action="store_true", help="Disable network access")
    parser.add_argument("--no-cache", action="store_true", help="Avoid cache operations")
    parser.add_argument("--directory", type=str, help="Change working directory")
    parser.add_argument("--project", type=str, help="Discover project in given directory")
    parser.add_argument("--config-file", type=str, help="Path to uv.toml configuration file")
    parser.add_argument("--managed-python", action="store_true", help="Require uv-managed Python versions")
    parser.add_argument("--no-managed-python", action="store_true", help="Disable uv-managed Python")

    subparsers = parser.add_subparsers(dest="subcommand", help="Available commands")

    # auth command
    auth_parser = subparsers.add_parser("auth", help="Authentication management")
    auth_subparsers = auth_parser.add_subparsers(dest="auth_command", help="Authentication commands")

    auth_login = auth_subparsers.add_parser("login", help="Login to a service")
    auth_login.add_argument("service", type=str, help="Service to login to")
    auth_login.add_argument("--username", type=str, help="Username")

    auth_logout = auth_subparsers.add_parser("logout", help="Logout of a service")
    auth_logout.add_argument("service", type=str, help="Service to logout from")

    auth_token = auth_subparsers.add_parser("token", help="Show the authentication token for a service")
    auth_token.add_argument("service", type=str, help="Service to show token for")

    auth_dir = auth_subparsers.add_parser("dir", help="Show the path to the uv credentials directory")

    # run command
    run_parser = subparsers.add_parser("run", help="Run a command or script")
    run_parser.add_argument("command", type=str, nargs="*", help="Command or script to run")
    run_parser.add_argument(
        "--with", dest="with_packages", type=str, action="append", help="Run with additional packages"
    )
    run_parser.add_argument("--isolated", action="store_true", help="Run in isolated environment")
    run_parser.add_argument("--python", type=str, help="Python version to use")

    # init command
    init_parser = subparsers.add_parser("init", help="Create a new project")
    init_parser.add_argument("path", type=str, nargs="?", help="Path for new project")
    init_parser.add_argument("--name", type=str, help="Project name")
    init_parser.add_argument("--package", action="store_true", help="Create a package project")
    init_parser.add_argument("--app", action="store_true", help="Create an application project")
    init_parser.add_argument("--lib", action="store_true", help="Create a library project")
    init_parser.add_argument("--python", type=str, help="Minimum Python version")

    # add command
    add_parser = subparsers.add_parser("add", help="Add dependencies to the project")
    add_parser.add_argument("packages", type=str, nargs="+", help="Packages to add")
    add_parser.add_argument("--dev", action="store_true", help="Add as development dependency")
    add_parser.add_argument("--optional", type=str, help="Add to optional dependency group")
    add_parser.add_argument("--editable", action="store_true", help="Add as editable dependency")
    add_parser.add_argument("--raw-sources", action="store_true", help="Add raw source strings")

    # remove command
    remove_parser = subparsers.add_parser("remove", help="Remove dependencies from the project")
    remove_parser.add_argument("packages", type=str, nargs="+", help="Packages to remove")
    remove_parser.add_argument("--dev", action="store_true", help="Remove from development dependencies")
    remove_parser.add_argument("--optional", type=str, help="Remove from optional dependency group")

    # sync command
    sync_parser = subparsers.add_parser("sync", help="Update the project's environment")
    sync_parser.add_argument("--frozen", action="store_true", help="Don't update lockfile")
    sync_parser.add_argument("--locked", action="store_true", help="Assert lockfile is up-to-date")
    sync_parser.add_argument("--inexact", action="store_true", help="Allow inexact lockfile resolution")
    sync_parser.add_argument("--no-dev", action="store_true", help="Exclude development dependencies")
    sync_parser.add_argument("--extra", type=str, action="append", help="Include optional dependency groups")
    sync_parser.add_argument("--all-extras", action="store_true", help="Include all optional dependencies")

    # lock command
    lock_parser = subparsers.add_parser("lock", help="Update the project's lockfile")
    lock_parser.add_argument("--frozen", action="store_true", help="Assert lockfile is up-to-date")
    lock_parser.add_argument("--locked", action="store_true", help="Don't update lockfile")
    lock_parser.add_argument("--upgrade", action="store_true", help="Allow package upgrades")
    lock_parser.add_argument("--upgrade-package", type=str, action="append", help="Upgrade specific packages")

    # export command
    export_parser = subparsers.add_parser(
        "export", help="Export the project's lockfile to an alternate format"
    )
    export_parser.add_argument(
        "--format",
        choices=["requirements-txt", "requirements.txt"],
        default="requirements-txt",
        help="Export format",
    )
    export_parser.add_argument("--output-file", "-o", type=str, help="Output file path")
    export_parser.add_argument("--no-dev", action="store_true", help="Exclude development dependencies")
    export_parser.add_argument(
        "--extra", type=str, action="append", help="Include optional dependency groups"
    )
    export_parser.add_argument("--all-extras", action="store_true", help="Include all optional dependencies")
    export_parser.add_argument("--no-hashes", action="store_true", help="Omit hashes")

    # tree command
    tree_parser = subparsers.add_parser("tree", help="Display the project's dependency tree")
    tree_parser.add_argument("--depth", type=int, help="Maximum display depth")
    tree_parser.add_argument("--prune", type=str, action="append", help="Prune the given packages")
    tree_parser.add_argument("--package", type=str, action="append", help="Display only specified packages")
    tree_parser.add_argument(
        "--no-dedupe", action="store_true", help="Don't de-duplicate repeated dependencies"
    )
    tree_parser.add_argument(
        "--invert", action="store_true", help="Invert the tree to show who depends on each package"
    )

    # version command
    version_parser = subparsers.add_parser("version", help="Read or update the project's version")
    version_parser.add_argument("version", type=str, nargs="?", help="New version to set")
    version_parser.add_argument("--bump", choices=["major", "minor", "patch"], help="Bump version component")

    # format command
    format_parser = subparsers.add_parser("format", help="Format Python code in the project")
    format_parser.add_argument("paths", type=str, nargs="*", help="Paths to format")
    format_parser.add_argument("--check", action="store_true", help="Check formatting without making changes")
    format_parser.add_argument("--exclude", type=str, action="append", help="Exclude paths from formatting")

    # tool command
    tool_parser = subparsers.add_parser("tool", help="Tool management")
    tool_subparsers = tool_parser.add_subparsers(dest="tool_command", help="Tool commands")

    tool_run = tool_subparsers.add_parser("run", help="Run a command provided by a Python package")
    tool_run.add_argument("command", type=str, help="Command to run")
    tool_run.add_argument("args", type=str, nargs="*", help="Arguments to pass to command")
    tool_run.add_argument("--from", dest="from_package", type=str, help="Package to run command from")
    tool_run.add_argument(
        "--with", dest="with_packages", type=str, action="append", help="Additional packages"
    )
    tool_run.add_argument("--python", type=str, help="Python version to use")
    tool_run.add_argument("--isolated", action="store_true", help="Run in isolated environment")

    tool_install = tool_subparsers.add_parser("install", help="Install commands provided by a Python package")
    tool_install.add_argument("packages", type=str, nargs="+", help="Packages to install")
    tool_install.add_argument("--from", dest="from_package", type=str, help="Package to install from")
    tool_install.add_argument(
        "--with", dest="with_packages", type=str, action="append", help="Additional packages"
    )
    tool_install.add_argument("--python", type=str, help="Python version to use")
    tool_install.add_argument("--force", action="store_true", help="Force reinstall")

    tool_upgrade = tool_subparsers.add_parser("upgrade", help="Upgrade installed tools")
    tool_upgrade.add_argument("tools", type=str, nargs="*", help="Tools to upgrade")
    tool_upgrade.add_argument("--all", action="store_true", help="Upgrade all tools")

    tool_list = tool_subparsers.add_parser("list", help="List installed tools")
    tool_list.add_argument("--show-paths", action="store_true", help="Show installation paths")

    tool_uninstall = tool_subparsers.add_parser("uninstall", help="Uninstall a tool")
    tool_uninstall.add_argument("tools", type=str, nargs="+", help="Tools to uninstall")

    tool_update_shell = tool_subparsers.add_parser(
        "update-shell", help="Ensure tool executable directory is on PATH"
    )
    tool_update_shell.add_argument("--shell", type=str, help="Shell to update")

    tool_dir = tool_subparsers.add_parser("dir", help="Show path to uv tools directory")

    # python command
    python_parser = subparsers.add_parser("python", help="Python version management")
    python_subparsers = python_parser.add_subparsers(dest="python_command", help="Python commands")

    python_list = python_subparsers.add_parser("list", help="List available Python installations")
    python_list.add_argument("--all-versions", action="store_true", help="Show all available versions")
    python_list.add_argument("--only-installed", action="store_true", help="Only show installed versions")

    python_install = python_subparsers.add_parser("install", help="Download and install Python versions")
    python_install.add_argument("versions", type=str, nargs="+", help="Python versions to install")
    python_install.add_argument("--force", action="store_true", help="Force reinstall")

    python_upgrade = python_subparsers.add_parser("upgrade", help="Upgrade installed Python versions")
    python_upgrade.add_argument("versions", type=str, nargs="*", help="Python versions to upgrade")
    python_upgrade.add_argument("--all", action="store_true", help="Upgrade all installed versions")

    python_find = python_subparsers.add_parser("find", help="Search for a Python installation")
    python_find.add_argument("version", type=str, nargs="?", help="Python version to find")

    python_pin = python_subparsers.add_parser("pin", help="Pin to a specific Python version")
    python_pin.add_argument("version", type=str, help="Python version to pin")
    python_pin.add_argument("--resolved", action="store_true", help="Write resolved version")

    python_dir = python_subparsers.add_parser("dir", help="Show uv Python installation directory")

    python_uninstall = python_subparsers.add_parser("uninstall", help="Uninstall Python versions")
    python_uninstall.add_argument("versions", type=str, nargs="+", help="Python versions to uninstall")

    python_update_shell = python_subparsers.add_parser(
        "update-shell", help="Ensure Python executable directory is on PATH"
    )
    python_update_shell.add_argument("--shell", type=str, help="Shell to update")

    # pip command
    pip_parser = subparsers.add_parser("pip", help="Package management (pip-compatible)")
    pip_subparsers = pip_parser.add_subparsers(dest="pip_command", help="Pip commands")

    pip_compile = pip_subparsers.add_parser("compile", help="Compile requirements.in to requirements.txt")
    pip_compile.add_argument("input_files", type=str, nargs="*", help="Input requirement files")
    pip_compile.add_argument("-o", "--output-file", type=str, help="Output file path")
    pip_compile.add_argument("--upgrade", "-U", action="store_true", help="Allow package upgrades")
    pip_compile.add_argument(
        "--upgrade-package", "-P", type=str, action="append", help="Upgrade specific packages"
    )
    pip_compile.add_argument("--generate-hashes", action="store_true", help="Generate hashes")
    pip_compile.add_argument("--no-header", action="store_true", help="Omit header comment")
    pip_compile.add_argument("--annotation-style", choices=["line", "split"], help="Annotation style")
    pip_compile.add_argument("--index-url", "-i", type=str, help="Base URL of package index")
    pip_compile.add_argument(
        "--extra-index-url", type=str, action="append", help="Extra URLs of package indexes"
    )
    pip_compile.add_argument(
        "--find-links", "-f", type=str, action="append", help="Path to search for distributions"
    )
    pip_compile.add_argument("--no-index", action="store_true", help="Ignore package index")
    pip_compile.add_argument("--constraint", "-c", type=str, action="append", help="Constrain versions")
    pip_compile.add_argument(
        "--resolution", choices=["highest", "lowest", "lowest-direct"], help="Resolution strategy"
    )
    pip_compile.add_argument(
        "--prerelease", choices=["allow", "if-necessary", "explicit", "disallow"], help="Pre-release handling"
    )
    pip_compile.add_argument("--python", type=str, help="Python version")
    pip_compile.add_argument("--python-platform", type=str, help="Target platform")

    pip_sync = pip_subparsers.add_parser("sync", help="Sync environment with requirements file")
    pip_sync.add_argument("files", type=str, nargs="*", help="Requirements files")
    pip_sync.add_argument("--constraint", "-c", type=str, action="append", help="Constrain versions")
    pip_sync.add_argument("--reinstall", action="store_true", help="Reinstall all packages")
    pip_sync.add_argument(
        "--reinstall-package", type=str, action="append", help="Reinstall specific packages"
    )
    pip_sync.add_argument("--index-url", "-i", type=str, help="Base URL of package index")
    pip_sync.add_argument(
        "--extra-index-url", type=str, action="append", help="Extra URLs of package indexes"
    )
    pip_sync.add_argument(
        "--find-links", "-f", type=str, action="append", help="Path to search for distributions"
    )
    pip_sync.add_argument("--no-index", action="store_true", help="Ignore package index")
    pip_sync.add_argument("--python", type=str, help="Python interpreter")
    pip_sync.add_argument("--system", action="store_true", help="Install into system Python")
    pip_sync.add_argument(
        "--break-system-packages", action="store_true", help="Allow breaking system packages"
    )

    pip_install = pip_subparsers.add_parser("install", help="Install packages into environment")
    pip_install.add_argument("packages", type=str, nargs="*", help="Packages to install")
    pip_install.add_argument(
        "-r", "--requirement", type=str, action="append", help="Install from requirements file"
    )
    pip_install.add_argument("-c", "--constraint", type=str, action="append", help="Constrain versions")
    pip_install.add_argument("-e", "--editable", type=str, action="append", help="Install in editable mode")
    pip_install.add_argument("--upgrade", "-U", action="store_true", help="Upgrade packages")
    pip_install.add_argument(
        "--upgrade-package", "-P", type=str, action="append", help="Upgrade specific packages"
    )
    pip_install.add_argument("--reinstall", action="store_true", help="Reinstall all packages")
    pip_install.add_argument(
        "--reinstall-package", type=str, action="append", help="Reinstall specific packages"
    )
    pip_install.add_argument("--index-url", "-i", type=str, help="Base URL of package index")
    pip_install.add_argument(
        "--extra-index-url", type=str, action="append", help="Extra URLs of package indexes"
    )
    pip_install.add_argument(
        "--find-links", "-f", type=str, action="append", help="Path to search for distributions"
    )
    pip_install.add_argument("--no-index", action="store_true", help="Ignore package index")
    pip_install.add_argument("--no-deps", action="store_true", help="Don't install dependencies")
    pip_install.add_argument(
        "--resolution", choices=["highest", "lowest", "lowest-direct"], help="Resolution strategy"
    )
    pip_install.add_argument(
        "--prerelease", choices=["allow", "if-necessary", "explicit", "disallow"], help="Pre-release handling"
    )
    pip_install.add_argument("--python", type=str, help="Python interpreter")
    pip_install.add_argument("--system", action="store_true", help="Install into system Python")
    pip_install.add_argument(
        "--break-system-packages", action="store_true", help="Allow breaking system packages"
    )

    pip_uninstall = pip_subparsers.add_parser("uninstall", help="Uninstall packages from environment")
    pip_uninstall.add_argument("packages", type=str, nargs="*", help="Packages to uninstall")
    pip_uninstall.add_argument(
        "-r", "--requirement", type=str, action="append", help="Uninstall from requirements file"
    )
    pip_uninstall.add_argument("--python", type=str, help="Python interpreter")
    pip_uninstall.add_argument("--system", action="store_true", help="Uninstall from system Python")
    pip_uninstall.add_argument(
        "--break-system-packages", action="store_true", help="Allow breaking system packages"
    )

    pip_freeze = pip_subparsers.add_parser("freeze", help="List packages in requirements format")
    pip_freeze.add_argument("--exclude-editable", action="store_true", help="Exclude editable packages")
    pip_freeze.add_argument("--python", type=str, help="Python interpreter")
    pip_freeze.add_argument("--system", action="store_true", help="List system Python packages")

    pip_list = pip_subparsers.add_parser("list", help="List packages in tabular format")
    pip_list.add_argument("--editable", action="store_true", help="List only editable packages")
    pip_list.add_argument("--exclude-editable", action="store_true", help="Exclude editable packages")
    pip_list.add_argument(
        "--format", choices=["columns", "freeze", "json"], default="columns", help="Output format"
    )
    pip_list.add_argument("--python", type=str, help="Python interpreter")
    pip_list.add_argument("--system", action="store_true", help="List system Python packages")

    pip_show = pip_subparsers.add_parser("show", help="Show information about installed packages")
    pip_show.add_argument("packages", type=str, nargs="+", help="Packages to show")
    pip_show.add_argument("--python", type=str, help="Python interpreter")
    pip_show.add_argument("--system", action="store_true", help="Show system Python packages")

    pip_tree = pip_subparsers.add_parser("tree", help="Display dependency tree")
    pip_tree.add_argument("--depth", type=int, help="Maximum display depth")
    pip_tree.add_argument("--prune", type=str, action="append", help="Prune the given packages")
    pip_tree.add_argument("--package", type=str, action="append", help="Display only specified packages")
    pip_tree.add_argument("--no-dedupe", action="store_true", help="Don't de-duplicate repeated dependencies")
    pip_tree.add_argument("--invert", action="store_true", help="Invert the tree")
    pip_tree.add_argument("--python", type=str, help="Python interpreter")
    pip_tree.add_argument("--system", action="store_true", help="Use system Python")

    pip_check = pip_subparsers.add_parser(
        "check", help="Verify installed packages have compatible dependencies"
    )
    pip_check.add_argument("--python", type=str, help="Python interpreter")
    pip_check.add_argument("--system", action="store_true", help="Check system Python packages")

    # build command
    build_parser = subparsers.add_parser("build", help="Build Python packages into distributions and wheels")
    build_parser.add_argument("src", type=str, nargs="?", default=".", help="Source directory")
    build_parser.add_argument("--wheel", action="store_true", help="Build wheel only")
    build_parser.add_argument("--sdist", action="store_true", help="Build source distribution only")
    build_parser.add_argument("--out-dir", "-o", type=str, help="Output directory")
    build_parser.add_argument("--package", type=str, help="Package to build")
    build_parser.add_argument("--python", type=str, help="Python version to use")

    # publish command
    publish_parser = subparsers.add_parser("publish", help="Upload distributions to an index")
    publish_parser.add_argument("files", type=str, nargs="*", help="Distribution files to upload")
    publish_parser.add_argument("--index-url", type=str, help="Index URL to upload to")
    publish_parser.add_argument("--username", type=str, help="Username for authentication")
    publish_parser.add_argument("--password", type=str, help="Password for authentication")
    publish_parser.add_argument("--token", type=str, help="Token for authentication")
    publish_parser.add_argument("--skip-existing", action="store_true", help="Skip files that already exist")

    # venv command
    venv_parser = subparsers.add_parser("venv", help="Create a virtual environment")
    venv_parser.add_argument(
        "path", type=str, nargs="?", default=".venv", help="Path for virtual environment"
    )
    venv_parser.add_argument("--python", type=str, help="Python version to use")
    venv_parser.add_argument("--seed", action="store_true", help="Install seed packages")
    venv_parser.add_argument(
        "--system-site-packages", action="store_true", help="Give access to system packages"
    )
    venv_parser.add_argument("--prompt", type=str, help="Environment prompt")

    # cache command
    cache_parser = subparsers.add_parser("cache", help="Cache management")
    cache_subparsers = cache_parser.add_subparsers(dest="cache_command", help="Cache commands")

    cache_clean = cache_subparsers.add_parser("clean", help="Clear cache entries")
    cache_clean.add_argument("packages", type=str, nargs="*", help="Packages to clear from cache")

    cache_prune = cache_subparsers.add_parser("prune", help="Prune unreachable objects from cache")
    cache_prune.add_argument("--ci", action="store_true", help="Optimize for CI environments")

    cache_dir = cache_subparsers.add_parser("dir", help="Show cache directory")

    cache_size = cache_subparsers.add_parser("size", help="Show cache size")

    # self command
    self_parser = subparsers.add_parser("self", help="Self-management")
    self_subparsers = self_parser.add_subparsers(dest="self_command", help="Self commands")

    self_update = self_subparsers.add_parser("update", help="Update uv")
    self_update.add_argument("--version", type=str, help="Version to update to")

    self_version = self_subparsers.add_parser("version", help="Display uv's version")

    # generate-shell-completion command
    completion_parser = subparsers.add_parser(
        "generate-shell-completion", help="Generate shell completion scripts"
    )
    completion_parser.add_argument(
        "shell",
        choices=["bash", "zsh", "fish", "powershell", "elvish"],
        help="Shell to generate completion for",
    )

    # help command
    help_parser = subparsers.add_parser("help", help="Display documentation for a command")
    help_parser.add_argument("command", type=str, nargs="?", help="Command to show help for")

    return parser
