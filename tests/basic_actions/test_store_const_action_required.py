import pytest
from nicegui import ui
from nicegui.testing import User

from nicegooey.argparse import nice_gooey_argparse_main, NgArgumentParser
from nicegooey.argparse.main import main_instance


@pytest.mark.nicegui_main_file(__file__)
async def test_store_const_action_required(user: User) -> None:
    """Test store_const action."""

    await user.open("/")
    await user.should_see("verbose")

    with pytest.raises(AssertionError):
        user.find(ui.checkbox)

    assert main_instance.namespace.verbose == "VERBOSE"


@nice_gooey_argparse_main(patch_argparse=False)
def main():
    parser = NgArgumentParser()
    parser.add_argument(
        "--verbose",
        required=True,
        action="store_const",
        const="VERBOSE",
        default="NORMAL",
        help="Enable verbose mode",
    )
    parser.parse_args()


if __name__ == "__main__":
    main()
