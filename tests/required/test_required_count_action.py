"""
Test that count actions enforce minimum count when required=True.
This test verifies count actions with required=True should enforce minimum count of 1.
"""

import pytest
from nicegui import ui
from nicegui.testing import User

from nicegooey.argparse.argument_parser import NgArgumentParser
from nicegooey.argparse.main import main_instance
from nicegooey.argparse.patch import nice_gooey_argparse_main
from tests.conftest import assert_has_validation_error


@pytest.mark.nicegui_main_file(__file__)
async def test_required_count_validation(user: User) -> None:
    """Test that required count actions enforce minimum count of 1."""
    await user.open("/")
    await user.should_see("verbose")

    # Count should start at 0 (current behavior) or 1 (after fix)
    number_input = user.find(ui.number)

    # Ensure it's at 0
    number_input.clear()
    number_input.type("0")
    assert main_instance.namespace.verbose == 0

    # Try to submit with count=0 - should fail for required count
    submit_button = user.find("Submit")
    submit_button.click()
    await assert_has_validation_error(user)

    # Set to 1
    number_input.clear()
    number_input.type("1")
    assert main_instance.namespace.verbose == 1

    # Now submit should pass
    submit_button.click()
    await user.should_see(kind=ui.xterm)


@nice_gooey_argparse_main(patch_argparse=False)
def main() -> None:
    parser = NgArgumentParser()
    parser.add_argument("--verbose", "-v", action="count", required=True, help="Verbosity level")
    parser.parse_args()


if __name__ == "__main__":
    main()
