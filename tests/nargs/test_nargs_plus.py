import pytest
from nicegui.testing import User

from nicegooey.argparse import nice_gooey_argparse_main, NgArgumentParser
from nicegooey.argparse.main import main_instance


@pytest.mark.nicegui_main_file(__file__)
async def test_nargs_plus(user: User) -> None:
    """Test nargs='+' - one or more values (at least one required)."""

    await user.open("/")

    await user.should_see("required-items")

    assert main_instance.namespace.required_items in (None, [])

    # TODO


@nice_gooey_argparse_main(patch_argparse=False)
def main():
    parser = NgArgumentParser()
    parser.add_argument("--required-items", nargs="+", type=str, help="One or more items (required)")
    parser.parse_args()


if __name__ == "__main__":
    main()
