import pytest
from nicegui import ui
from nicegui.testing import User

from nicegooey.argparse import NgArgumentParser, NiceGooeyConfig, nice_gooey_argparse_main
from tests.conftest import find_within


@pytest.mark.nicegui_main_file(__file__)
async def test_override_type_renders_number_input(user: User) -> None:
    """Test that override_type=int causes a ui.number to be rendered instead of ui.input."""

    await user.open("/")
    await user.should_see("value")

    # A numeric input should be present
    find_within(user, kind=ui.number, within_marker="ng-action-value")

    # No plain text input
    with pytest.raises(AssertionError):
        find_within(user, kind=ui.input, within_marker="ng-action-value")


@nice_gooey_argparse_main(patch_argparse=False)
def main() -> None:
    parser = NgArgumentParser()
    # Custom lambda type — would normally render as ui.input
    value_action = parser.add_argument("--value", type=lambda s: int(s) * 2, help="A value", required=True)
    value_action.nicegooey_config = NiceGooeyConfig.ActionConfig(override_type=int)
    parser.parse_args()


if __name__ == "__main__":
    main()
