import pytest
from nicegui.testing import User

from nicegooey.argparse import nice_gooey_argparse_main, NgArgumentParser
from nicegooey.argparse.main import main_instance


@pytest.mark.nicegui_main_file(__file__)
async def test_nargs_asterisk(user: User) -> None:
    """Test nargs='*' - zero or more values (list)."""

    await user.open("/")

    await user.should_see("items")

    assert main_instance.namespace.items in (None, [])


@nice_gooey_argparse_main(patch_argparse=False)
def main():
    parser = NgArgumentParser()
    parser.add_argument("--items", nargs="*", type=str, help="Zero or more items")
    parser.parse_args()


if __name__ == "__main__":
    main()
