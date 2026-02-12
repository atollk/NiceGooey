import pytest
from nicegui import ui
from nicegui.testing import User

from nicegooey.argparse import nice_gooey_argparse_main, NgArgumentParser


@pytest.mark.nicegui_main_file(__file__)
async def test_mutually_exclusive_group_switching(user: User) -> None:
    """Test switching between options in mutually exclusive group."""

    await user.open("/")

    select = user.find(ui.select)

    select.click()
    await user.should_see("mode-fast")


@nice_gooey_argparse_main(patch_argparse=False)
def main():
    parser = NgArgumentParser()

    me_group = parser.add_mutually_exclusive_group()
    me_group.add_argument("--mode-fast", action="store_true", dest="mode", help="Fast mode")
    me_group.add_argument("--mode-slow", action="store_true", dest="mode", help="Slow mode")

    parser.parse_args()


if __name__ == "__main__":
    main()
