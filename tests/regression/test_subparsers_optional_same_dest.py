import pytest
from nicegui.testing import User

from nicegooey.argparse import NgArgumentParser, nice_gooey_argparse_main
from nicegooey.argparse.ui_classes.actions.action_ui_element import ActionUiElement
from nicegooey.argparse.ui_classes.groupings.subparser_ui import SubparserUi

from tests.conftest import exactly_one, find_within
from nicegui import ui


@pytest.mark.nicegui_main_file(__file__)
async def test_subparsers_optional_same_dest(user: User) -> None:
    """
    Regression test for subparsers with optional arguments that have the same dest name.

    Tests that switching between subparsers properly resets UI state when they have
    optional arguments with the same dest name.
    """
    await user.open("/")

    # Navigate to pip subparser
    await user.should_see("pip")
    tab_pip = user.find(marker=f"{SubparserUi.TAB_MARKER_PREFIX}pip")
    tab_pip.click()

    # Find elements for sync subparser
    sync_enable_checkbox = find_within(
        user,
        kind=ui.checkbox,
        within_marker="ng-action-index_url",
        within_outer_marker=f"{SubparserUi.TABPANEL_MARKER_PREFIX}sync",
    )
    sync_input = find_within(
        user,
        marker=ActionUiElement.BASIC_ELEMENT_MARKER,
        within_marker="ng-action-index_url",
        within_outer_marker=f"{SubparserUi.TABPANEL_MARKER_PREFIX}sync",
    )

    # Find elements for install subparser
    install_enable_checkbox = find_within(
        user,
        kind=ui.checkbox,
        within_marker="ng-action-index_url",
        within_outer_marker=f"{SubparserUi.TABPANEL_MARKER_PREFIX}install",
    )
    install_input = find_within(
        user,
        marker=ActionUiElement.BASIC_ELEMENT_MARKER,
        within_marker="ng-action-index_url",
        within_outer_marker=f"{SubparserUi.TABPANEL_MARKER_PREFIX}install",
    )

    # Step 1: Navigate to sync tab - check that index-url is unchecked
    await user.should_see("sync")
    tab_sync = user.find(marker=f"{SubparserUi.TAB_MARKER_PREFIX}sync")
    tab_sync.click()

    assert exactly_one(sync_enable_checkbox.elements).value is False, (
        "Sync index-url checkbox should be unchecked initially"
    )

    # Step 2: Navigate to install tab - check that index-url is unchecked
    await user.should_see("install")
    tab_install = user.find(marker=f"{SubparserUi.TAB_MARKER_PREFIX}install")
    tab_install.click()

    assert exactly_one(install_enable_checkbox.elements).value is False, (
        "Install index-url checkbox should be unchecked initially"
    )

    # Step 3: Go back to sync, enable and set a value
    tab_sync.click()

    sync_enable_checkbox.click()
    assert exactly_one(sync_enable_checkbox.elements).value is True, (
        "Sync checkbox should be checked after clicking"
    )

    exactly_one(sync_input.elements).set_value("https://sync.example.com")
    assert exactly_one(sync_input.elements).value == "https://sync.example.com", (
        "Sync input should have the value"
    )

    # Step 4: Switch to install tab - should be unchecked and empty
    tab_install.click()

    assert exactly_one(install_enable_checkbox.elements).value is False, (
        "Install checkbox should be unchecked after switching from sync"
    )

    # Step 5: Enable and set a value in install
    install_enable_checkbox.click()
    assert exactly_one(install_enable_checkbox.elements).value is True, (
        "Install checkbox should be checked after clicking"
    )

    exactly_one(install_input.elements).set_value("https://install.example.com")
    assert exactly_one(install_input.elements).value == "https://install.example.com", (
        "Install input should have the value"
    )

    # Step 6: Switch back to sync - should be unchecked and empty
    tab_sync.click()

    assert exactly_one(sync_enable_checkbox.elements).value is False, (
        "Sync checkbox should be unchecked after switching from install"
    )


@nice_gooey_argparse_main(patch_argparse=False)
def main() -> None:
    parser = NgArgumentParser()
    subparsers = parser.add_subparsers(dest="subcommand")
    pip_parser = subparsers.add_parser("pip")
    pip_subparsers = pip_parser.add_subparsers(dest="pip_command", help="Pip commands")
    pip_sync = pip_subparsers.add_parser("sync")
    pip_sync.add_argument("--index-url", "-i")
    pip_install = pip_subparsers.add_parser("install")
    pip_install.add_argument("--index-url", "-i", type=str)
    parser.parse_args()


if __name__ == "__main__":
    main()
