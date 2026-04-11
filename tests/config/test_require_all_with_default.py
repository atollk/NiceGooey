import pytest
from nicegui import ui
from nicegui.testing import User

from nicegooey.argparse import NgArgumentParser, nice_gooey_argparse_main
from nicegooey.argparse.main import main_instance
from nicegooey.argparse.ui_classes.actions.action_ui_element import ActionUiElement


@pytest.mark.nicegui_main_file(__file__)
async def test_require_all_with_default(user: User) -> None:
    """Test that require_all_with_default=True treats optional args with a default as required (no enable checkbox)."""

    await user.open("/")
    await user.should_see("name")

    # No enable checkbox — the arg is treated as required
    with pytest.raises(AssertionError):
        user.find(kind=ui.checkbox, marker=ActionUiElement.ENABLE_PARAMETER_BOX_MARKER)

    # Initial namespace value should be the default
    assert main_instance.namespace.name == "Alice"

    # Changing the value updates the namespace
    from tests.conftest import exactly_one

    input_el = exactly_one(user.find(ui.input).elements)
    input_el.value = "Bob"
    assert main_instance.namespace.name == "Bob"


@nice_gooey_argparse_main(patch_argparse=False)
def main() -> None:
    parser = NgArgumentParser()
    parser.nicegooey_config.require_all_with_default = True
    parser.add_argument("--name", type=str, default="Alice", help="Your name")
    parser.parse_args()


if __name__ == "__main__":
    main()
