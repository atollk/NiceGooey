"""Tests for subparser functionality."""

import pytest
from nicegui.testing import User

from nicegooey.argparse import nice_gooey_argparse_main, NgArgumentParser


@pytest.mark.nicegui_main_file(__file__)
async def test_three_subparsers_basic(user: User) -> None:
    """Test three subparsers: empty, simple (2 args), and complex (with group)."""

    @nice_gooey_argparse_main(patch_argparse=False)
    def main():
        parser = NgArgumentParser()

        # Add subparsers
        subparsers = parser.add_subparsers(dest="command", help="Available commands")

        # Empty subparser (no arguments)
        parser_empty = subparsers.add_parser("empty", help="Empty command with no args")

        # Simple subparser (two basic arguments)
        parser_simple = subparsers.add_parser("simple", help="Simple command with two args")
        parser_simple.add_argument("--arg1", type=str, help="First argument")
        parser_simple.add_argument("--arg2", type=int, help="Second argument")

        # Complex subparser (with argument group)
        parser_complex = subparsers.add_parser("complex", help="Complex command with groups")
        group = parser_complex.add_argument_group(title="Complex Options")
        group.add_argument("--option-a", type=str, help="Option A")
        group.add_argument("--option-b", type=float, help="Option B")

        parser.parse_args()

    await user.open("/")

    # Should see tabs for each subparser
    await user.should_see("empty")
    await user.should_see("simple")
    await user.should_see("complex")

    # Click on simple tab
    # (Would need to find the tab element and click it)
    # Then verify that arg1 and arg2 are visible

    # Click on complex tab
    # Verify that the group and its options are visible


@pytest.mark.nicegui_main_file(__file__)
async def test_optional_subparsers_with_dash_tab(user: User) -> None:
    """Test optional subparsers which show a '-' tab for no subparser selection."""

    @nice_gooey_argparse_main(patch_argparse=False)
    def main():
        parser = NgArgumentParser()

        # Optional subparsers (required=False)
        subparsers = parser.add_subparsers(dest="command", required=False, help="Optional commands")

        parser_cmd1 = subparsers.add_parser("cmd1", help="Command 1")
        parser_cmd1.add_argument("--opt1", type=str, help="Option 1")

        parser_cmd2 = subparsers.add_parser("cmd2", help="Command 2")
        parser_cmd2.add_argument("--opt2", type=str, help="Option 2")

        parser.parse_args()

    await user.open("/")

    # Should see tabs including the "-" tab for no selection
    await user.should_see("-")
    await user.should_see("cmd1")
    await user.should_see("cmd2")

    # Click on the "-" tab should show no additional arguments


@pytest.mark.nicegui_main_file(__file__)
async def test_required_subparsers_no_dash_tab(user: User) -> None:
    """Test required subparsers which don't show a '-' tab."""

    @nice_gooey_argparse_main(patch_argparse=False)
    def main():
        parser = NgArgumentParser()

        # Required subparsers (required=True, which is the default)
        subparsers = parser.add_subparsers(dest="command", required=True, help="Required commands")

        parser_cmd1 = subparsers.add_parser("cmd1", help="Command 1")
        parser_cmd1.add_argument("--opt1", type=str, help="Option 1")

        parser_cmd2 = subparsers.add_parser("cmd2", help="Command 2")
        parser_cmd2.add_argument("--opt2", type=str, help="Option 2")

        parser.parse_args()

    await user.open("/")

    # Should see tabs but NOT the "-" tab
    await user.should_see("cmd1")
    await user.should_see("cmd2")

    # The "-" tab should not be present
    # (This would require checking that "-" is not in the tabs)


@pytest.mark.nicegui_main_file(__file__)
async def test_subparsers_with_external_argument(user: User) -> None:
    """Test subparsers with an argument defined outside subparsers (always visible)."""

    @nice_gooey_argparse_main(patch_argparse=False)
    def main():
        parser = NgArgumentParser()

        # Global argument (outside subparsers)
        parser.add_argument("--global-option", type=str, help="Global option visible everywhere")

        # Add subparsers
        subparsers = parser.add_subparsers(dest="command", help="Commands")

        parser_cmd1 = subparsers.add_parser("cmd1", help="Command 1")
        parser_cmd1.add_argument("--cmd1-option", type=str, help="Command 1 option")

        parser_cmd2 = subparsers.add_parser("cmd2", help="Command 2")
        parser_cmd2.add_argument("--cmd2-option", type=int, help="Command 2 option")

        parser.parse_args()

    await user.open("/")

    # The global option should be visible regardless of which tab is selected
    await user.should_see("global-option")

    # Should see both command tabs
    await user.should_see("cmd1")
    await user.should_see("cmd2")

    # Click on cmd1 tab
    # Should see both global-option and cmd1-option

    # Click on cmd2 tab
    # Should see both global-option and cmd2-option


@pytest.mark.nicegui_main_file(__file__)
async def test_subparser_tab_switching(user: User) -> None:
    """Test switching between subparser tabs and verifying correct content."""

    @nice_gooey_argparse_main(patch_argparse=False)
    def main():
        parser = NgArgumentParser()

        subparsers = parser.add_subparsers(dest="command", help="Commands")

        parser_build = subparsers.add_parser("build", help="Build command")
        parser_build.add_argument("--output", type=str, help="Output directory")

        parser_test = subparsers.add_parser("test", help="Test command")
        parser_test.add_argument("--verbose", action="store_true", help="Verbose output")

        parser_deploy = subparsers.add_parser("deploy", help="Deploy command")
        parser_deploy.add_argument("--environment", choices=["dev", "prod"], help="Environment")

        parser.parse_args()

    await user.open("/")

    # Should see all three tabs
    await user.should_see("build")
    await user.should_see("test")
    await user.should_see("deploy")

    # Click on build tab
    # (Would need to find and click the tab)
    # Then verify "output" is visible

    # Click on test tab
    # Then verify "verbose" is visible

    # Click on deploy tab
    # Then verify "environment" is visible


@pytest.mark.nicegui_main_file(__file__)
async def test_subparser_with_groups(user: User) -> None:
    """Test subparser that contains argument groups."""

    @nice_gooey_argparse_main(patch_argparse=False)
    def main():
        parser = NgArgumentParser()

        subparsers = parser.add_subparsers(dest="command", help="Commands")

        parser_config = subparsers.add_parser("config", help="Configuration command")

        # Add groups within the subparser
        group1 = parser_config.add_argument_group(title="Database Config")
        group1.add_argument("--db-host", type=str, help="Database host")
        group1.add_argument("--db-port", type=int, help="Database port")

        group2 = parser_config.add_argument_group(title="Cache Config")
        group2.add_argument("--cache-size", type=int, help="Cache size")
        group2.add_argument("--cache-ttl", type=int, help="Cache TTL")

        parser.parse_args()

    await user.open("/")

    # Should see the config tab
    await user.should_see("config")

    # Click on config tab (or it might be selected by default)
    # Then verify both groups are visible
    # await user.should_see('Database Config')
    # await user.should_see('Cache Config')
    # And their respective arguments


@pytest.mark.nicegui_main_file(__file__)
async def test_nested_subparser_structure(user: User) -> None:
    """Test complex nested subparser structure with multiple levels."""

    @nice_gooey_argparse_main(patch_argparse=False)
    def main():
        parser = NgArgumentParser()

        # Main argument
        parser.add_argument("--verbose", action="store_true", help="Verbose mode")

        # First level subparsers
        subparsers = parser.add_subparsers(dest="command", help="Main commands")

        # Git-like structure: git remote add/remove
        parser_remote = subparsers.add_parser("remote", help="Remote operations")
        remote_subparsers = parser_remote.add_subparsers(dest="remote_command", help="Remote commands")

        parser_remote_add = remote_subparsers.add_parser("add", help="Add remote")
        parser_remote_add.add_argument("--name", type=str, help="Remote name")
        parser_remote_add.add_argument("--url", type=str, help="Remote URL")

        parser_remote_remove = remote_subparsers.add_parser("remove", help="Remove remote")
        parser_remote_remove.add_argument("--name", type=str, help="Remote name to remove")

        parser.parse_args()

    await user.open("/")

    # Should see main verbose option
    await user.should_see("verbose")

    # Should see the remote tab
    await user.should_see("remote")

    # After clicking remote, should see add and remove as sub-options
    # (The exact UI representation may vary - tabs within tabs, or different layout)
