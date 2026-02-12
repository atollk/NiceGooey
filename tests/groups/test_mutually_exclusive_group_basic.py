import pytest
from nicegui import ui
from nicegui.testing import User

from nicegooey.argparse import nice_gooey_argparse_main, NgArgumentParser


@pytest.mark.nicegui_main_file(__file__)
async def test_mutually_exclusive_group_basic(user: User) -> None:
    """Test mutually exclusive group with dropdown selector."""

    await user.open("/")

    select = user.find(ui.select)
    assert select is not None

    select.click()
    await user.should_see("option_a")


@nice_gooey_argparse_main(patch_argparse=False)
def main():
    parser = NgArgumentParser()

    me_group = parser.add_mutually_exclusive_group()
    me_group.add_argument("--option-a", type=str, help="Option A")
    me_group.add_argument("--option-b", type=str, help="Option B")
    me_group.add_argument("--option-c", type=str, help="Option C")

    parser.parse_args()


if __name__ == "__main__":
    main()
