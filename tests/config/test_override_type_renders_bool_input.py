import pytest
from nicegui.testing import User

from nicegooey.argparse import NgArgumentParser, NiceGooeyConfig, nice_gooey_argparse_main
from nicegooey.ui_util.validation_checkbox import ValidationCheckbox
from tests.conftest import find_within


@pytest.mark.nicegui_main_file(__file__)
async def test_override_type_renders_bool_input(user: User) -> None:
    """Test that override_type=bool causes a ValidationCheckbox to be rendered."""

    await user.open("/")
    await user.should_see("flag")

    # A ValidationCheckbox should be present within the flag action
    find_within(user, kind=ValidationCheckbox, within_marker="ng-action-flag")


@nice_gooey_argparse_main(patch_argparse=False)
def main() -> None:
    parser = NgArgumentParser()
    flag_action = parser.add_argument("--flag", type=str, help="A flag", required=True)
    flag_action.nicegooey_config = NiceGooeyConfig.ActionConfig(override_type=bool)
    parser.parse_args()


if __name__ == "__main__":
    main()
