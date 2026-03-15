import pytest
from nicegui.testing import User

from nicegooey.argparse import nice_gooey_argparse_main, NgArgumentParser


@pytest.mark.nicegui_main_file(__file__)
@pytest.mark.skip(
    reason="Keyboard event testing not yet implemented - need to investigate NiceGUI keyboard API"
)
async def test_keyboard_tab_navigation(user: User) -> None:
    """Test that tab key navigates between input fields."""

    await user.open("/")

    # Find the input fields
    # name_input = user.find(ui.input, marker="ng-action-name")
    # email_input = user.find(ui.input, marker="ng-action-email")
    # age_input = user.find(ui.number, marker="ng-action-age")

    # TODO: Implement keyboard event testing
    # Expected behavior:
    # 1. Focus on name_input
    # 2. Press Tab key -> should focus email_input
    # 3. Press Tab key -> should focus age_input
    # 4. Press Shift+Tab -> should focus email_input

    # Placeholder for keyboard event API:
    # name_input.focus()
    # user.keyboard.press("Tab")
    # assert email_input.is_focused()
    # user.keyboard.press("Tab")
    # assert age_input.is_focused()
    # user.keyboard.press("Shift+Tab")
    # assert email_input.is_focused()

    pytest.fail("Keyboard event testing needs to be implemented")


@nice_gooey_argparse_main(patch_argparse=False)
def main():
    parser = NgArgumentParser()
    parser.add_argument("--name", type=str, help="Your name", required=True)
    parser.add_argument("--email", type=str, help="Your email", required=True)
    parser.add_argument("--age", type=int, help="Your age", required=True)
    parser.parse_args()


if __name__ == "__main__":
    main()
