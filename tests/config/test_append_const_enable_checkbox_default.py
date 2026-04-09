import pytest
from nicegui import ui
from nicegui.testing import User

from nicegooey.argparse import NgArgumentParser, nice_gooey_argparse_main
from nicegooey.argparse.ui_classes.actions.action_ui_element import ActionUiElement


@pytest.mark.nicegui_main_file(__file__)
async def test_append_const_enable_checkbox_default(user: User) -> None:
    """Test that an append_const action shows an enable checkbox by default (without required=True)."""

    await user.open("/")
    await user.should_see("add-flag")

    # Enable checkbox IS shown — append_const needs to be toggleable to be useful
    user.find(kind=ui.checkbox, marker=ActionUiElement.ENABLE_PARAMETER_BOX_MARKER)


@nice_gooey_argparse_main(patch_argparse=False)
def main() -> None:
    parser = NgArgumentParser()
    parser.add_argument("--add-flag", action="append_const", const="FLAG", dest="flags", help="Add a flag")
    parser.parse_args()


if __name__ == "__main__":
    main()
