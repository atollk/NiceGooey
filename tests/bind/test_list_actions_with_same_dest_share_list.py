import pytest
from nicegui.testing import User

from nicegooey.argparse import NgArgumentParser, nice_gooey_argparse_main
from nicegooey.argparse.main import main_instance
from nicegooey.argparse.ui_classes.actions.action_ui_element import ActionUiElement
from nicegooey.argparse.ui_classes.actions.standard_actions import ListActionUiElement
from tests.conftest import find_within


@pytest.mark.nicegui_main_file(__file__)
async def test_list_actions_with_same_dest_share_list(user: User) -> None:
    """Test that multiple list actions sharing a dest share the same underlying list."""

    await user.open("/")

    await user.should_see("add-a")
    await user.should_see("add-b")

    assert main_instance.namespace.items == []

    # Find elements for --add-a action using action-specific markers
    input_a = find_within(
        user,
        marker=ActionUiElement.BASIC_ELEMENT_MARKER,
        within_marker="ng-action-add-a",
    )
    button_a = find_within(
        user, marker=ListActionUiElement.LIST_ADD_BUTTON_MARKER, within_marker="ng-action-add-a"
    )

    # Find elements for --add-b action using action-specific markers
    input_b = find_within(
        user,
        marker=ActionUiElement.BASIC_ELEMENT_MARKER,
        within_marker="ng-action-add-b",
    )
    button_b = find_within(
        user, marker=ListActionUiElement.LIST_ADD_BUTTON_MARKER, within_marker="ng-action-add-b"
    )

    # Add item via first action (add-a)
    input_a.type("item-a")
    button_a.click()
    assert main_instance.namespace.items == ["item-a"]

    # Add item via second action (add-b)
    input_b.type("item-b")
    button_b.click()
    assert main_instance.namespace.items == ["item-a", "item-b"]

    # Add another item via first action
    input_a.type("item-a2")
    button_a.click()
    assert main_instance.namespace.items == ["item-a", "item-b", "item-a2"]


@nice_gooey_argparse_main(patch_argparse=False)
def main():
    parser = NgArgumentParser()
    parser.add_argument("--add-a", action="append", dest="items", type=str, help="Add via A")
    parser.add_argument("--add-b", action="append", dest="items", type=str, help="Add via B")
    parser.parse_args()


if __name__ == "__main__":
    main()
