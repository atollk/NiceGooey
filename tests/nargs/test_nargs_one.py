import pytest
from nicegui import ui
from nicegui.testing import User

from nicegooey.argparse import nice_gooey_argparse_main, NgArgumentParser
from nicegooey.argparse.main import main_instance


@pytest.mark.nicegui_main_file(__file__)
async def test_nargs_one(user: User) -> None:
    """Test nargs=1 - exactly one value expected (as a list with one item)."""

    await user.open("/")

    await user.should_see("item")

    assert main_instance.namespace.item in (None, [], [""])

    input_field = user.find(ui.input)
    input_field.type("single-value")


@nice_gooey_argparse_main(patch_argparse=False)
def main():
    parser = NgArgumentParser()
    parser.add_argument("--item", nargs=1, type=str, help="One item")
    parser.parse_args()


if __name__ == "__main__":
    main()
