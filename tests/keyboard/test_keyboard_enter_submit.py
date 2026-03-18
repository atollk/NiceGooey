import pytest
from nicegui.testing import Screen

from nicegooey.argparse import nice_gooey_argparse_main, NgArgumentParser


@pytest.mark.nicegui_main_file(__file__)
async def test_keyboard_enter_submit(screen: Screen) -> None:
    """Test that pressing Enter key submits the form."""

    screen.open("/")

    # TODO:
    #  input something in "name"
    #  press Enter
    #  check that an xterm opened


@nice_gooey_argparse_main(patch_argparse=False)
def main():
    parser = NgArgumentParser()
    parser.add_argument("--name", type=str, help="Your name", required=True)
    parser.parse_args()


if __name__ == "__main__":
    main()
