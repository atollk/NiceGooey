import pytest
from nicegui import ui
from nicegui.testing import User

from nicegooey.argparse import NgArgumentParser, nice_gooey_argparse_main
from nicegooey.argparse.main import main_instance


@pytest.mark.nicegui_main_file(__file__)
async def test_string_action(user: User) -> None:
    """Test a basic string action with input field."""

    await user.open("/")
    await user.should_see("name")

    input_field = user.find(ui.input)
    input_field.type("Alice")

    assert main_instance.namespace.name == "Alice"


@nice_gooey_argparse_main(patch_argparse=False)
def main():
    parser = NgArgumentParser()
    parser.add_argument("--name", type=str, help="Your name", required=True)
    parser.parse_args()


if __name__ == "__main__":
    main()
