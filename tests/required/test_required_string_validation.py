"""
Test that required string arguments fail validation when empty.
This test verifies validation should fail when required fields are empty.
"""

import os

import pytest
from nicegui import ui
from nicegui.testing import User

from nicegooey.argparse.argument_parser import NgArgumentParser
from nicegooey.argparse.patch import nice_gooey_argparse_main


@pytest.mark.nicegui_main_file(__file__)
async def test_required_string_validation(user: User) -> None:
    """Test that required string fields fail validation when empty."""
    await user.open("/")
    await user.should_see("name")

    # Initially empty - should fail validation
    submit_button = user.find("Submit")
    submit_button.click()

    # Verify xterm does NOT appear (validation failed)
    with pytest.raises(AssertionError):
        user.find(kind=ui.xterm)

    # Fill in value
    input_field = user.find(ui.input)
    input_field.type("Alice")

    # Now should pass validation
    submit_button.click()
    await user.should_see(kind=ui.xterm)


@nice_gooey_argparse_main(patch_argparse=False)
def main():
    parser = NgArgumentParser()
    parser.add_argument("--name", type=str, required=True, help="Your name")
    args = parser.parse_args()

    if not os.environ["PYTEST_CURRENT_TEST"].endswith("(setup)"):
        print(f"Hello, {args.name}!")


if __name__ == "__main__":
    main()
