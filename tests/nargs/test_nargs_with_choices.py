import pytest
from nicegui import ui
from nicegui.testing import User

from nicegooey.argparse import NgArgumentParser, nice_gooey_argparse_main
from nicegooey.argparse.main import main_instance
from nicegooey.argparse.ui_classes.actions.action_ui_element import ActionUiElement


@pytest.mark.nicegui_main_file(__file__)
async def test_nargs_with_choices(user: User) -> None:
    """Test nargs with choices combination."""

    await user.open("/")

    await user.should_see("colors")

    assert main_instance.namespace.colors in (None, [])

    # Find the select element and add button
    select = user.find(ui.select)
    add_button = user.find(marker=ActionUiElement.ADD_BUTTON_MARKER)

    # Select "red" and add it
    select.click()
    await user.should_see("red")
    user.find("red").click()
    add_button.click()

    # Verify namespace contains ["red"]
    assert main_instance.namespace.colors == ["red"]

    # Select "blue" and add it
    select.click()
    await user.should_see("blue")
    user.find("blue").click()
    add_button.click()

    # Verify namespace contains both values
    assert main_instance.namespace.colors == ["red", "blue"]


@nice_gooey_argparse_main(patch_argparse=False)
def main() -> None:
    parser = NgArgumentParser()
    parser.add_argument(
        "--colors", nargs="*", choices=["red", "green", "blue"], help="Select colors", required=True
    )
    parser.parse_args()


if __name__ == "__main__":
    main()
