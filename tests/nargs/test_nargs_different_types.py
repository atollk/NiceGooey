import pytest
from nicegui.testing import User

from nicegooey.argparse import nice_gooey_argparse_main, NgArgumentParser


@pytest.mark.nicegui_main_file(__file__)
async def test_nargs_different_types(user: User) -> None:
    """Test nargs with different type combinations."""

    await user.open("/")

    await user.should_see("ints")
    await user.should_see("floats")
    await user.should_see("strings")


@nice_gooey_argparse_main(patch_argparse=False)
def main():
    parser = NgArgumentParser()
    parser.add_argument("--ints", nargs="+", type=int, help="One or more integers")
    parser.add_argument("--floats", nargs="*", type=float, help="Zero or more floats")
    parser.add_argument("--strings", nargs=2, type=str, help="Exactly two strings")
    parser.parse_args()


if __name__ == "__main__":
    main()
