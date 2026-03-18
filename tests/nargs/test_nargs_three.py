import pytest
from nicegui.testing import User

from nicegooey.argparse import nice_gooey_argparse_main, NgArgumentParser
from nicegooey.argparse.main import main_instance


@pytest.mark.nicegui_main_file(__file__)
async def test_nargs_three(user: User) -> None:
    """Test nargs=3 - exactly three values expected."""

    await user.open("/")

    await user.should_see("coords")

    assert main_instance.namespace.coords in (None, [], [0, 0, 0])

    # TODO


@nice_gooey_argparse_main(patch_argparse=False)
def main():
    parser = NgArgumentParser()
    parser.add_argument("--coords", nargs=3, type=float, help="Three coordinates (x, y, z)")
    parser.parse_args()


if __name__ == "__main__":
    main()
