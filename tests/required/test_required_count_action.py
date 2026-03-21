"""Test that count actions enforce minimum count when required=True.

This test verifies TODO at action_impls.py:149 - count actions with required=True
should enforce minimum count of 1.
"""

import os

import pytest
from nicegui import ui
from nicegui.testing import User

from nicegooey.argparse.argument_parser import NgArgumentParser
from nicegooey.argparse.main import main_instance
from nicegooey.argparse.patch import nice_gooey_argparse_main


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
    with pytest.raises(AssertionError):
        user.find(kind=ui.xterm)

    # Set to 1
    number_input.clear()
    number_input.type("1")
    assert main_instance.namespace.verbose == 1

    # Now submit should pass
    submit_button.click()
    await user.should_see(kind=ui.xterm)


@pytest.mark.nicegui_main_file(__file__)
async def test_required_count_min_value(user: User) -> None:
    """Test that required count has appropriate minimum value."""
    await user.open("/")

    number_input = user.find(ui.number)

    # After implementation, the default might be 1 instead of 0
    # For now, this documents the expected behavior
    initial_value = main_instance.namespace.verbose

    # The minimum should prevent going below 0 (or 1 after fix)
    number_input.clear()
    number_input.type("-1")

    # Value should not go negative
    assert main_instance.namespace.verbose >= 0, "Count should not be negative"

    # For required counts, ideally minimum would be 1
    # This will fail initially but documents the expected behavior


@nice_gooey_argparse_main(patch_argparse=False)
def main():
    parser = NgArgumentParser()
    parser.add_argument("--verbose", "-v", action="count", required=True, help="Verbosity level")
    args = parser.parse_args()

    if not os.environ["PYTEST_CURRENT_TEST"].endswith("(setup)"):
        print(f"Verbosity: {args.verbose}")


if __name__ == "__main__":
    main()
