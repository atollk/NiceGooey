import pytest
from nicegui.testing import User

from nicegooey.argparse import NgArgumentParser, nice_gooey_argparse_main


@pytest.mark.nicegui_main_file(__file__)
async def test_metavar_tuple_display(user: User) -> None:
    """Test that metavar (tuple) uses the first element to display the action name in the UI."""

    await user.open("/")

    # Should see the first element of metavar tuple "FILE1" instead of "files"
    await user.should_see("FILE1")


@nice_gooey_argparse_main(patch_argparse=False)
def main():
    parser = NgArgumentParser()
    parser.add_argument(
        "--files", type=str, metavar=("FILE1", "FILE2"), nargs="+", help="Input files", required=True
    )
    parser.parse_args()


if __name__ == "__main__":
    main()
