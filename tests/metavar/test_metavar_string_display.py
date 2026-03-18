import pytest
from nicegui.testing import User

from nicegooey.argparse import NgArgumentParser, nice_gooey_argparse_main


@pytest.mark.nicegui_main_file(__file__)
async def test_metavar_string_display(user: User) -> None:
    """Test that metavar (string) is used to display the action name in the UI."""

    await user.open("/")

    # Should see the metavar "USERNAME" instead of the option string "name"
    await user.should_see("USERNAME")


@nice_gooey_argparse_main(patch_argparse=False)
def main():
    parser = NgArgumentParser()
    parser.add_argument("--name", type=str, metavar="USERNAME", help="Your username", required=True)
    parser.parse_args()


if __name__ == "__main__":
    main()
