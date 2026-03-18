import pytest
from nicegui.testing import User

from nicegooey.argparse import nice_gooey_argparse_main, NgArgumentParser
from nicegooey.argparse.main import main_instance


@pytest.mark.nicegui_main_file(__file__)
async def test_nargs_with_choices(user: User) -> None:
    """Test nargs with choices combination."""

    await user.open("/")

    await user.should_see("colors")

    assert main_instance.namespace.colors in (None, [])

    # TODO


@nice_gooey_argparse_main(patch_argparse=False)
def main():
    parser = NgArgumentParser()
    parser.add_argument("--colors", nargs="*", choices=["red", "green", "blue"], help="Select colors")
    parser.parse_args()


if __name__ == "__main__":
    main()
