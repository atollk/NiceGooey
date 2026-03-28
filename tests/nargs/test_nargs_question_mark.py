import pytest
from nicegui import ui
from nicegui.testing import User

from nicegooey.argparse import NgArgumentParser, nice_gooey_argparse_main
from nicegooey.argparse.main import main_instance
from nicegooey.argparse.ui_classes.actions.action_ui_element import ActionUiElement
from tests.conftest import find_within


@pytest.mark.nicegui_main_file(__file__)
async def test_nargs_question_mark(user: User) -> None:
    """Test nargs='?' - zero or one value (optional single value)."""

    await user.open("/")

    await user.should_see("optional")

    enable_arg_checkbox = user.find(marker=ActionUiElement.ENABLE_PARAMETER_BOX_MARKER)
    enable_value_checkbox = find_within(
        user, kind=ui.checkbox, within_marker=ActionUiElement.NARGS_WRAPPER_MARKER
    )
    value_input = find_within(user, kind=ui.input, within_marker=ActionUiElement.NARGS_WRAPPER_MARKER)
    assert (
        len(enable_arg_checkbox.elements)
        == len(enable_value_checkbox.elements)
        == len(value_input.elements)
        == 1
    )

    assert main_instance.namespace.optional == "DEFAULT"

    enable_arg_checkbox.click()

    assert main_instance.namespace.optional == "CONST"

    enable_value_checkbox.click()

    assert main_instance.namespace.optional == ""

    value_input.type("foo")

    assert main_instance.namespace.optional == "foo"


@nice_gooey_argparse_main(patch_argparse=False)
def main() -> None:
    parser = NgArgumentParser()
    parser.add_argument(
        "--optional", nargs="?", type=str, const="CONST", default="DEFAULT", help="Optional value"
    )
    parser.parse_args()


if __name__ == "__main__":
    main()
