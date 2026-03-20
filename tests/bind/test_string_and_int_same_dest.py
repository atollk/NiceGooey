import pytest
from nicegui.testing import User

from nicegooey.argparse import NgArgumentParser, nice_gooey_argparse_main
from nicegooey.argparse.main import main_instance
from nicegooey.argparse.ui_classes.actions.action_sync_element import ActionSyncElement
from tests.conftest import find_within, exactly_one


@pytest.mark.nicegui_main_file(__file__)
async def test_string_and_int_same_dest(user: User) -> None:
    """Test one string and one int action with the same dest - verify two-way binding."""

    await user.open("/")

    await user.should_see("value")

    value_str_input = find_within(
        user, marker=ActionSyncElement.BASIC_ELEMENT_MARKER, within_marker="ng-action-value-str"
    )
    value_str_enable = find_within(
        user, marker=ActionSyncElement.ENABLE_PARAMETER_BOX_MARKER, within_marker="ng-action-value-str"
    )
    value_int_enable = find_within(
        user, marker=ActionSyncElement.ENABLE_PARAMETER_BOX_MARKER, within_marker="ng-action-value-int"
    )

    assert main_instance.namespace.value in ("", 0)
    assert not exactly_one(value_str_enable.elements).value
    assert not exactly_one(value_int_enable.elements).value

    value_str_enable.click()
    value_str_input.type("Hello")
    assert main_instance.namespace.value == "Hello"
    assert not exactly_one(value_int_enable.elements).value

    value_int_enable.click()
    exactly_one(value_str_input.elements).value = 123
    assert main_instance.namespace.value == "123"
    assert exactly_one(value_int_enable.elements).value
    assert exactly_one(value_str_input.elements).value in (123, "123")


@nice_gooey_argparse_main(patch_argparse=False)
def main():
    parser = NgArgumentParser()
    parser.add_argument("--value-str", dest="value", type=str, default="", help="Value as string")
    parser.add_argument("--value-int", dest="value", type=int, default=0, help="Value as int")
    parser.parse_args()


if __name__ == "__main__":
    main()
