import pytest
from nicegui import ui
from nicegui.testing import User

from nicegooey.argparse import nice_gooey_argparse_main, NgArgumentParser
from nicegooey.argparse.main import main_instance
from tests.conftest import exactly_one


@pytest.mark.nicegui_main_file(__file__)
async def test_float_action(user: User) -> None:
    """Test float action with number input."""

    await user.open("/")
    await user.should_see("price")

    number_input = user.find(ui.number)
    # .type doesn't work well with number inputs, so we set the value directory.
    exactly_one(number_input.elements).value = 19.99

    assert main_instance.namespace.price == 19.99


@nice_gooey_argparse_main(patch_argparse=False)
def main():
    parser = NgArgumentParser()
    parser.add_argument("--price", type=float, help="Price", required=True)
    parser.parse_args()


if __name__ == "__main__":
    main()
