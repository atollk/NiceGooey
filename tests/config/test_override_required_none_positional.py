import pytest
from nicegui import ui
from nicegui.testing import User

from nicegooey.argparse import NgArgumentParser, nice_gooey_argparse_main
from nicegooey.argparse.ui_classes.actions.action_ui_element import ActionUiElement


@pytest.mark.nicegui_main_file(__file__)
async def test_override_required_none_positional(user: User) -> None:
    """Test that positional arguments always have no enable checkbox (always treated as required)."""

    await user.open("/")
    await user.should_see("filename")

    # Positional args are always required — no enable checkbox
    with pytest.raises(AssertionError):
        user.find(kind=ui.checkbox, marker=ActionUiElement.ENABLE_PARAMETER_BOX_MARKER)


@nice_gooey_argparse_main(patch_argparse=False)
def main() -> None:
    parser = NgArgumentParser()
    # Positional argument (no --)
    parser.add_argument("filename", type=str, help="Input file")
    parser.parse_args()


if __name__ == "__main__":
    main()
