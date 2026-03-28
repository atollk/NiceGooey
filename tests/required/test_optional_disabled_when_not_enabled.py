import pytest
from nicegui import ui
from nicegui.testing import User

from nicegooey.argparse import NgArgumentParser, nice_gooey_argparse_main
from nicegooey.argparse.main import main_instance
from nicegooey.argparse.ui_classes.actions.action_ui_element import ActionUiElement


@pytest.mark.nicegui_main_file(__file__)
async def test_optional_disabled_when_not_enabled(user: User) -> None:
    """Test that optional (non-required) actions reset to None when enable checkbox is unchecked."""

    await user.open("/")
    await user.should_see("name")

    # Find the enable checkbox and input field
    enable_checkbox = user.find(kind=ui.checkbox, marker=ActionUiElement.ENABLE_PARAMETER_BOX_MARKER)
    input_field = user.find(ui.input)

    # Initially, the namespace value should be empty string (checkbox is unchecked by default)
    assert main_instance.namespace.name == ""

    # Enable the checkbox by clicking it
    enable_checkbox.click()

    # Type a value in the input field
    input_field.type("Alice")

    # The namespace should now have the typed value
    assert main_instance.namespace.name == "Alice"

    # Disable it again by clicking the checkbox
    enable_checkbox.click()

    # The namespace should reset to empty string when disabled
    assert main_instance.namespace.name == ""


@nice_gooey_argparse_main(patch_argparse=False)
def main() -> None:
    parser = NgArgumentParser()
    parser.add_argument("--name", type=str, help="Your name")
    parser.parse_args()


if __name__ == "__main__":
    main()
