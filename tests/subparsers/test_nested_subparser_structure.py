import pytest
from nicegui.testing import User

from nicegooey.argparse import nice_gooey_argparse_main, NgArgumentParser


@pytest.mark.nicegui_main_file(__file__)
async def test_nested_subparser_structure(user: User) -> None:
    """Test complex nested subparser structure with multiple levels."""

    await user.open("/")

    await user.should_see("verbose")
    await user.should_see("remote")


@nice_gooey_argparse_main(patch_argparse=False)
def main():
    parser = NgArgumentParser()

    parser.add_argument("--verbose", action="store_true", help="Verbose mode")

    subparsers = parser.add_subparsers(dest="command", help="Main commands")

    parser_remote = subparsers.add_parser("remote", help="Remote operations")
    remote_subparsers = parser_remote.add_subparsers(dest="remote_command", help="Remote commands")

    parser_remote_add = remote_subparsers.add_parser("add", help="Add remote")
    parser_remote_add.add_argument("--name", type=str, help="Remote name")
    parser_remote_add.add_argument("--url", type=str, help="Remote URL")

    parser_remote_remove = remote_subparsers.add_parser("remove", help="Remove remote")
    parser_remote_remove.add_argument("--name", type=str, help="Remote name to remove")

    parser.parse_args()


if __name__ == "__main__":
    main()
