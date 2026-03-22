import pytest
from nicegui import ui
from nicegui.testing import User

from nicegooey.argparse import NgArgumentParser, nice_gooey_argparse_main
from nicegooey.argparse.main import main_instance
from nicegooey.argparse.ui_classes.actions.action_ui_element import ActionUiElement


@pytest.mark.nicegui_main_file(__file__)
async def test_nargs_one(user: User) -> None:
    """Test nargs=1 - exactly one value expected (as a list with one item)."""

    await user.open("/")

    await user.should_see("item")

    assert main_instance.namespace.item == []

    user.find(ui.input).type("single-value")
    user.find(marker=ActionUiElement.ADD_BUTTON_MARKER).click()

    assert main_instance.namespace.item == ["single-value"]


@nice_gooey_argparse_main(patch_argparse=False)
def main():
    parser = NgArgumentParser()
    parser.add_argument("--item", nargs=1, type=str, help="One item", required=True)
    parser.parse_args()


if __name__ == "__main__":
    main()
