import pytest
from nicegui.testing import User

from nicegooey.argparse import nice_gooey_argparse_main, NgArgumentParser


@pytest.mark.nicegui_main_file(__file__)
async def test_optional_subparsers_with_dash_tab(user: User) -> None:
    """Test optional subparsers which show a '-' tab for no subparser selection."""

    await user.open("/")

    await user.should_see("-")
    await user.should_see("cmd1")
    await user.should_see("cmd2")

    # TODO


@nice_gooey_argparse_main(patch_argparse=False)
def main():
    parser = NgArgumentParser()

    subparsers = parser.add_subparsers(dest="command", required=False, help="Optional commands")

    parser_cmd1 = subparsers.add_parser("cmd1", help="Command 1")
    parser_cmd1.add_argument("--opt1", type=str, help="Option 1")

    parser_cmd2 = subparsers.add_parser("cmd2", help="Command 2")
    parser_cmd2.add_argument("--opt2", type=str, help="Option 2")

    parser.parse_args()


if __name__ == "__main__":
    main()
