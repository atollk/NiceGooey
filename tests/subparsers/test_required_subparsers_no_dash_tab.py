import pytest
from nicegui.testing import User

from nicegooey.argparse import nice_gooey_argparse_main, NgArgumentParser


@pytest.mark.nicegui_main_file(__file__)
async def test_required_subparsers_no_dash_tab(user: User) -> None:
    """Test required subparsers which don't show a '-' tab."""

    await user.open("/")

    await user.should_see("cmd1")
    await user.should_see("cmd2")


@nice_gooey_argparse_main(patch_argparse=False)
def main():
    parser = NgArgumentParser()

    subparsers = parser.add_subparsers(dest="command", required=True, help="Required commands")

    parser_cmd1 = subparsers.add_parser("cmd1", help="Command 1")
    parser_cmd1.add_argument("--opt1", type=str, help="Option 1")

    parser_cmd2 = subparsers.add_parser("cmd2", help="Command 2")
    parser_cmd2.add_argument("--opt2", type=str, help="Option 2")

    parser.parse_args()


if __name__ == "__main__":
    main()
