import pytest
from nicegui import ui
from nicegui.testing import User

from nicegooey.argparse import nice_gooey_argparse_main, NgArgumentParser


@pytest.mark.nicegui_main_file(__file__)
@pytest.mark.skip(
    reason="Keyboard event testing not yet implemented - need to investigate NiceGUI keyboard API"
)
async def test_keyboard_enter_submit(user: User) -> None:
    """Test that pressing Enter key submits the form."""

    await user.open("/")

    # Find the input field
    name_input = user.find(ui.input)

    # Type a value
    name_input.type("Alice")

    # TODO: Implement keyboard event testing
    # Expected behavior:
    # 1. Press Enter key -> should submit the form
    # 2. Verify that the form submission was triggered

    # Placeholder for keyboard event API:
    # user.keyboard.press("Enter")
    # await user.should_see("Form submitted")  # or check some submission indicator

    pytest.fail("Keyboard event testing needs to be implemented")


@nice_gooey_argparse_main(patch_argparse=False)
def main():
    parser = NgArgumentParser()
    parser.add_argument("--name", type=str, help="Your name", required=True)
    parser.parse_args()


if __name__ == "__main__":
    main()
