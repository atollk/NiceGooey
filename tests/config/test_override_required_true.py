import pytest
from nicegui import ui
from nicegui.testing import User

from nicegooey.argparse import NgArgumentParser, NiceGooeyConfig, nice_gooey_argparse_main
from nicegooey.argparse.ui_classes.actions.action_ui_element import ActionUiElement


@pytest.mark.nicegui_main_file(__file__)
async def test_override_required_true(user: User) -> None:
    """Test that override_required=True removes the enable checkbox from an optional action."""

    await user.open("/")
    await user.should_see("count")

    # No enable checkbox — overridden to be required
    with pytest.raises(AssertionError):
        user.find(kind=ui.checkbox, marker=ActionUiElement.ENABLE_PARAMETER_BOX_MARKER)


@nice_gooey_argparse_main(patch_argparse=False)
def main() -> None:
    parser = NgArgumentParser()
    count_action = parser.add_argument("--count", type=int, help="Item count")
    count_action.nicegooey_config = NiceGooeyConfig.ActionConfig(override_required=True)
    parser.parse_args()


if __name__ == "__main__":
    main()
