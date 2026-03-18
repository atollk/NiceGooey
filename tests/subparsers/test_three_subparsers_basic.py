import pytest
from nicegui.testing import User

from nicegooey.argparse import nice_gooey_argparse_main, NgArgumentParser


@pytest.mark.nicegui_main_file(__file__)
async def test_three_subparsers_basic(user: User) -> None:
    """Test three subparsers: empty, simple (2 args), and complex (with group)."""

    await user.open("/")

    await user.should_see("empty")
    await user.should_see("simple")
    await user.should_see("complex")

    # TODO


@nice_gooey_argparse_main(patch_argparse=False)
def main():
    parser = NgArgumentParser()

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    subparsers.add_parser("empty", help="Empty command with no args")

    parser_simple = subparsers.add_parser("simple", help="Simple command with two args")
    parser_simple.add_argument("--arg1", type=str, help="First argument")
    parser_simple.add_argument("--arg2", type=int, help="Second argument")

    parser_complex = subparsers.add_parser("complex", help="Complex command with groups")
    group = parser_complex.add_argument_group(title="Complex Options")
    group.add_argument("--option-a", type=str, help="Option A")
    group.add_argument("--option-b", type=float, help="Option B")

    parser.parse_args()


if __name__ == "__main__":
    main()
