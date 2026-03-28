import pytest
from nicegui import ui
from nicegui.testing import User

from nicegooey.argparse import NgArgumentParser, nice_gooey_argparse_main
from tests.conftest import find_within, assert_has_validation_error, exactly_one


@pytest.mark.nicegui_main_file(__file__)
async def test_action_validation(user: User) -> None:
    """Test that custom validation injected via the config is executed and, if failing, shows the error in the UI."""
    await user.open("/")
    await user.should_see("age")

    # Find the age input field
    age_input = exactly_one(find_within(user, kind=ui.number, within_marker="ng-action-age").elements)

    # Try submitting with invalid value (below minimum age)
    age_input.value = 15
    submit_button = user.find("Submit")
    submit_button.click()

    # Should show validation error
    await assert_has_validation_error(user)

    # Now enter a valid value
    age_input.value = 20
    submit_button.click()

    # Should succeed and show xterm
    await user.should_see(kind=ui.xterm)


@nice_gooey_argparse_main(patch_argparse=False)
def main() -> None:
    parser = NgArgumentParser()

    # Add an argument with custom validation
    age_action = parser.add_argument(
        "--age",
        type=int,
        help="Your age",
        required=True,
    )

    # Add custom validation: age must be >= 18
    def validate_age(value: int) -> str | None:
        if value < 18:
            return "Age must be at least 18"
        return None

    parser.nicegooey_config.action_config[age_action].validation = validate_age

    parser.parse_args()


if __name__ == "__main__":
    main()
