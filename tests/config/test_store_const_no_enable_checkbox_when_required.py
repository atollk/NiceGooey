import pytest
from nicegui import ui
from nicegui.testing import User

from nicegooey.argparse import NgArgumentParser, nice_gooey_argparse_main
from nicegooey.argparse.ui_classes.actions.action_ui_element import ActionUiElement


@pytest.mark.nicegui_main_file(__file__)
async def test_store_const_no_enable_checkbox_when_required(user: User) -> None:
    """Test that a store_const action with required=True has no enable checkbox."""

    await user.open("/")
    await user.should_see("verbose")

    # No enable checkbox when explicitly required
    with pytest.raises(AssertionError):
        user.find(kind=ui.checkbox, marker=ActionUiElement.ENABLE_PARAMETER_BOX_MARKER)


@nice_gooey_argparse_main(patch_argparse=False)
def main() -> None:
    parser = NgArgumentParser()
    parser.add_argument(
        "--verbose",
        action="store_const",
        const="VERBOSE",
        default="NORMAL",
        required=True,
        help="Verbose mode",
    )
    parser.parse_args()


if __name__ == "__main__":
    main()
