import pytest
from nicegui.testing import User

from nicegooey.argparse import NgArgumentParser, nice_gooey_argparse_main
from nicegooey.argparse.main import main_instance
from nicegooey.argparse.ui_classes.actions.action_ui_element import ActionUiElement
from tests.conftest import find_within


@pytest.mark.nicegui_main_file(__file__)
async def test_nargs_different_types(user: User) -> None:
    """Test nargs with different type combinations."""

    await user.open("/")

    await user.should_see("ints")
    await user.should_see("floats")
    await user.should_see("strings")

    # Add to ints: "1", "2", "3"
    ints_element = find_within(
        user,
        marker=ActionUiElement.BASIC_ELEMENT_MARKER + ActionUiElement.LIST_INNER_ELEMENT_MARKER_SUFFIX,
        within_marker="ng-action-ints",
    )
    ints_add_button = find_within(
        user, marker=ActionUiElement.ADD_BUTTON_MARKER, within_marker="ng-action-ints"
    )

    ints_element.type("1")
    ints_add_button.click()
    ints_element.type("2")
    ints_add_button.click()
    ints_element.type("3")
    ints_add_button.click()

    # Add to floats: "1.5"
    floats_element = find_within(
        user,
        marker=ActionUiElement.BASIC_ELEMENT_MARKER + ActionUiElement.LIST_INNER_ELEMENT_MARKER_SUFFIX,
        within_marker="ng-action-floats",
    )
    floats_add_button = find_within(
        user, marker=ActionUiElement.ADD_BUTTON_MARKER, within_marker="ng-action-floats"
    )

    floats_element.type("1.5")
    floats_add_button.click()

    # Add to strings: "hello", "world"
    strings_element = find_within(
        user,
        marker=ActionUiElement.BASIC_ELEMENT_MARKER + ActionUiElement.LIST_INNER_ELEMENT_MARKER_SUFFIX,
        within_marker="ng-action-strings",
    )
    strings_add_button = find_within(
        user, marker=ActionUiElement.ADD_BUTTON_MARKER, within_marker="ng-action-strings"
    )

    strings_element.type("hello")
    strings_add_button.click()
    strings_element.type("world")
    strings_add_button.click()

    # Verify
    assert main_instance.namespace.ints == [1, 2, 3]
    assert main_instance.namespace.floats == [1.5]
    assert main_instance.namespace.strings == ["hello", "world"]


@nice_gooey_argparse_main(patch_argparse=False)
def main():
    parser = NgArgumentParser()
    parser.add_argument("--ints", nargs="+", type=int, help="One or more integers", required=True)
    parser.add_argument("--floats", nargs="*", type=float, help="Zero or more floats", required=True)
    parser.add_argument("--strings", nargs=2, type=str, help="Exactly two strings", required=True)
    parser.parse_args()


if __name__ == "__main__":
    main()
