import pytest
from nicegui.testing import User

from nicegooey.argparse import nice_gooey_argparse_main, NgArgumentParser
from nicegooey.argparse.main import main_instance
from nicegooey.argparse.ui_classes.actions.action_sync_element import ActionSyncElement
from tests.conftest import find_within


@pytest.mark.nicegui_main_file(__file__)
async def test_append_const_and_append_same_dest(user: User) -> None:
    """Test append_const and append actions with same dest - verify list synchronization."""

    await user.open("/")

    await user.should_see("add-flag")
    await user.should_see("add-item")

    assert main_instance.namespace.items == []

    # Find the add button for append_const action (--add-flag)
    # Now elements have both the action marker and their type marker
    add_flag_button = find_within(
        user, marker=ActionSyncElement.ADD_BUTTON_MARKER, within_marker="ng-action-add-flag"
    )
    add_flag_button.click()
    assert main_instance.namespace.items == ["FLAG"]

    # Find input and button for append action (--add-item)
    input_field = find_within(
        user,
        marker=ActionSyncElement.BASIC_ELEMENT_MARKER + ActionSyncElement.LIST_INNER_ELEMENT_MARKER_SUFFIX,
        within_marker="ng-action-add-item",
    )
    add_item_button = find_within(
        user, marker=ActionSyncElement.ADD_BUTTON_MARKER, within_marker="ng-action-add-item"
    )

    # Add a custom item
    input_field.type("custom")
    add_item_button.click()
    assert main_instance.namespace.items == ["FLAG", "custom"]

    # Add another FLAG
    add_flag_button.click()
    assert main_instance.namespace.items == ["FLAG", "custom", "FLAG"]


@nice_gooey_argparse_main(patch_argparse=False)
def main():
    parser = NgArgumentParser()
    parser.add_argument(
        "--add-flag", action="append_const", const="FLAG", dest="items", help="Add flag constant"
    )
    parser.add_argument("--add-item", action="append", type=str, dest="items", help="Add custom item")
    parser.parse_args()


if __name__ == "__main__":
    main()
