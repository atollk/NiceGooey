import pytest
from nicegui import ui
from nicegui.testing import User

from nicegooey.argparse import nice_gooey_argparse_main, NgArgumentParser
from nicegooey.argparse.main import main_instance


def validate_min_length(value: str) -> str:
    """Custom validator that requires at least 3 characters."""
    if len(value) < 3:
        raise ValueError("Must be at least 3 characters")
    return value


@pytest.mark.nicegui_main_file(__file__)
async def test_action_with_type_validation(user: User) -> None:
    """Test action with custom type function that can fail."""

    await user.open("/")
    await user.should_see("username")

    input_field = user.find(ui.input)

    input_field.type("ab")

    input_field.clear()
    input_field.type("alice")

    assert main_instance.namespace.username == "alice"


@nice_gooey_argparse_main(patch_argparse=False)
def main():
    parser = NgArgumentParser()
    parser.add_argument("--username", type=validate_min_length, help="Username (min 3 chars)", required=True)
    parser.parse_args()


if __name__ == "__main__":
    main()
