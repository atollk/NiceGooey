import pytest
from nicegui import ui
from nicegui.testing import User

from nicegooey.argparse import NgArgumentParser, nice_gooey_argparse_main
from nicegooey.argparse.ui_classes.actions.action_ui_element import ActionUiElement


@pytest.mark.nicegui_main_file(__file__)
async def test_require_all_with_default_no_default(user: User) -> None:
    """Test that require_all_with_default=True still shows enable checkbox for args without a default."""

    await user.open("/")
    await user.should_see("name")

    # Enable checkbox IS shown because there is no default value
    user.find(kind=ui.checkbox, marker=ActionUiElement.ENABLE_PARAMETER_BOX_MARKER)


@nice_gooey_argparse_main(patch_argparse=False)
def main() -> None:
    parser = NgArgumentParser()
    parser.nicegooey_config.require_all_with_default = True
    # No default provided
    parser.add_argument("--name", type=str, help="Your name")
    parser.parse_args()


if __name__ == "__main__":
    main()
