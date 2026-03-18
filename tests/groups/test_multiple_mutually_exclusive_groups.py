import pytest
from nicegui import ui
from nicegui.testing import User

from nicegooey.argparse import NgArgumentParser, nice_gooey_argparse_main


@pytest.mark.nicegui_main_file(__file__)
async def test_multiple_mutually_exclusive_groups(user: User) -> None:
    """Test multiple ME groups in the same parser."""

    await user.open("/")

    selects = user.find(ui.select)
    assert selects is not None


@nice_gooey_argparse_main(patch_argparse=False)
def main():
    parser = NgArgumentParser()

    me_group1 = parser.add_mutually_exclusive_group()
    me_group1.add_argument("--verbose", action="store_true", help="Verbose output")
    me_group1.add_argument("--quiet", action="store_true", help="Quiet output")

    me_group2 = parser.add_mutually_exclusive_group()
    me_group2.add_argument("--color", action="store_true", help="Colored output")
    me_group2.add_argument("--no-color", action="store_true", help="No colored output")

    parser.parse_args()


if __name__ == "__main__":
    main()
