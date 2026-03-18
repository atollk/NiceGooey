import pytest
from nicegui.testing import User

from nicegooey.argparse import nice_gooey_argparse_main, NgArgumentParser


@pytest.mark.nicegui_main_file(__file__)
async def test_nargs_specific_number_validation(user: User) -> None:
    """Test that nargs with specific number enforces exactly that many values."""

    await user.open("/")

    await user.should_see("rgb")

    # TODO


@nice_gooey_argparse_main(patch_argparse=False)
def main():
    parser = NgArgumentParser()
    parser.add_argument("--rgb", nargs=3, type=int, help="RGB color (3 integers)")
    parser.parse_args()


if __name__ == "__main__":
    main()
