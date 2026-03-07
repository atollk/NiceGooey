import pytest
from nicegui import ui
from nicegui.testing import User

from nicegooey.argparse import nice_gooey_argparse_main, NgArgumentParser
from nicegooey.argparse.main import main_instance


@pytest.mark.nicegui_main_file(__file__)
async def test_int_action(user: User) -> None:
    """Test integer action with number input."""

    await user.open("/")
    await user.should_see("age")

    number_input = user.find(ui.number)
    number_input.type("42")

    assert main_instance.namespace.age == 42


@nice_gooey_argparse_main(patch_argparse=False)
def main():
    parser = NgArgumentParser()
    parser.add_argument("--age", type=int, help="Your age", required=True)
    parser.parse_args()


if __name__ == "__main__":
    main()
