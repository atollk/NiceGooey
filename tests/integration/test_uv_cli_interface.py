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

from nicegooey.argparse import NgArgumentParser, nice_gooey_argparse_main
from nicegooey.argparse.main import main_instance
from tests.integration.uv import create_uv_parser


@pytest.mark.nicegui_main_file(__file__)
async def test_uv_cli_interface(user: User) -> None:
    """
    Comprehensive integration test that verifies complex argparse structures work correctly in NiceGooey.

    Tests a realistic CLI tool interface with nested subparsers, various action types,
    mutually exclusive groups, and both required and optional arguments.

    This test simulates: uv pip install numpy --upgrade --extra-index-url https://test.pypi.org --verbose --offline
    """
    from nicegooey.argparse.ui_classes.actions.action_sync_element import ActionSyncElement
    from nicegooey.argparse.ui_classes.groupings.subparser_ui import SubparserUi
    from tests.conftest import find_within

    await user.open("/")

    # Verify global options are visible
    await user.should_see("verbose")
    await user.should_see("offline")

    # Test global options: --verbose (count action) and --offline (store_true)
    verbose_checkbox = find_within(user, kind=ui.number, within_marker="ng-action-verbose")
    verbose_checkbox.type("1")
    assert main_instance.namespace.verbose == 1

    offline_checkbox = find_within(user, kind=ui.checkbox, within_marker="ng-action-offline")
    offline_checkbox.click()
    assert main_instance.namespace.offline is True

    # Navigate to "pip" subparser (first level)
    await user.should_see("pip")
    pip_tab = user.find(marker=f"{SubparserUi.TAB_MARKER_PREFIX}pip")
    pip_tab.click()
    assert main_instance.namespace.subcommand == "pip"

    # Navigate to "install" subparser (second level nested under pip)
    await user.should_see("install")
    install_tab = find_within(
        user,
        marker=f"{SubparserUi.TAB_MARKER_PREFIX}install",
        within_marker=f"{SubparserUi.TABPANEL_MARKER_PREFIX}pip",
    )
    assert len(install_tab.elements) == 1
    install_tab.click()
    assert main_instance.namespace.pip_command == "install"

    # Verify install-specific options are visible
    await user.should_see("packages")
    await user.should_see("upgrade")
    await user.should_see("extra-index-url")

    # Add a package "numpy" to the packages list (nargs="*")
    packages_element = find_within(
        user,
        marker=ActionSyncElement.BASIC_ELEMENT_MARKER + ActionSyncElement.LIST_INNER_ELEMENT_MARKER_SUFFIX,
        within_marker="ng-action-packages",
        within_outer_marker=f"{SubparserUi.TABPANEL_MARKER_PREFIX}install",
        within_outest_marker=f"{SubparserUi.TABPANEL_MARKER_PREFIX}pip",
    )
    packages_add_button = find_within(
        user,
        marker=ActionSyncElement.ADD_BUTTON_MARKER,
        within_marker="ng-action-packages",
        within_outer_marker=f"{SubparserUi.TABPANEL_MARKER_PREFIX}install",
        within_outest_marker=f"{SubparserUi.TABPANEL_MARKER_PREFIX}pip",
    )
    packages_element.type("numpy")
    packages_add_button.click()

    assert main_instance.namespace.packages == ["numpy"]

    # Enable --upgrade flag (store_true)
    upgrade_checkbox = find_within(
        user,
        kind=ui.checkbox,
        within_marker="ng-action-upgrade",
        within_outer_marker=f"{SubparserUi.TABPANEL_MARKER_PREFIX}install",
        within_outest_marker=f"{SubparserUi.TABPANEL_MARKER_PREFIX}pip",
    )
    upgrade_checkbox.click()
    assert main_instance.namespace.upgrade is True

    # Add an extra index URL (append action)
    extra_index_element = find_within(
        user,
        marker=ActionSyncElement.BASIC_ELEMENT_MARKER + ActionSyncElement.LIST_INNER_ELEMENT_MARKER_SUFFIX,
        within_marker="ng-action-extra_index_url",
        within_outer_marker=f"{SubparserUi.TABPANEL_MARKER_PREFIX}install",
        within_outest_marker=f"{SubparserUi.TABPANEL_MARKER_PREFIX}pip",
    )
    extra_index_add_button = find_within(
        user,
        marker=ActionSyncElement.ADD_BUTTON_MARKER,
        within_marker="ng-action-extra_index_url",
        within_outer_marker=f"{SubparserUi.TABPANEL_MARKER_PREFIX}install",
        within_outest_marker=f"{SubparserUi.TABPANEL_MARKER_PREFIX}pip",
    )
    extra_index_element.type("https://test.pypi.org")
    extra_index_add_button.click()

    assert main_instance.namespace.extra_index_url == ["https://test.pypi.org"]

    # Add a second extra index URL to test append action
    extra_index_element.type("https://backup.pypi.org")
    extra_index_add_button.click()

    assert main_instance.namespace.extra_index_url == ["https://test.pypi.org", "https://backup.pypi.org"]

    # Test choices field: --resolution
    # TODO: need to enable 'resolution' first
    await user.should_see("resolution")
    resolution_enable_box = find_within(
        user,
        marker=ActionSyncElement.ENABLE_PARAMETER_BOX_MARKER,
        within_marker="ng-action-resolution",
        within_outer_marker=f"{SubparserUi.TABPANEL_MARKER_PREFIX}install",
        within_outest_marker=f"{SubparserUi.TABPANEL_MARKER_PREFIX}pip",
    )
    resolution_select = find_within(
        user,
        kind=ui.select,
        within_marker="ng-action-resolution",
        within_outer_marker=f"{SubparserUi.TABPANEL_MARKER_PREFIX}install",
        within_outest_marker=f"{SubparserUi.TABPANEL_MARKER_PREFIX}pip",
    )
    resolution_enable_box.click()
    resolution_select.click()
    await user.should_see("highest")
    await user.should_see("lowest")
    user.find("highest").click()

    # Verify final namespace state
    assert main_instance.namespace.verbose == 1
    assert main_instance.namespace.offline is True
    assert main_instance.namespace.subcommand == "pip"
    assert main_instance.namespace.pip_command == "install"
    assert main_instance.namespace.packages == ["numpy"]
    assert main_instance.namespace.upgrade is True
    assert main_instance.namespace.extra_index_url == ["https://test.pypi.org", "https://backup.pypi.org"]
    assert main_instance.namespace.resolution == "highest"


@nice_gooey_argparse_main(patch_argparse=False)
def main():
    """Build the UV CLI interface using argparse."""
    parser = NgArgumentParser.from_argparse(create_uv_parser())
    parser.parse_args()


if __name__ == "__main__":
    main()
