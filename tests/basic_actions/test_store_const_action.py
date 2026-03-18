import pytest
from nicegui import ui
from nicegui.testing import User

from nicegooey.argparse import NgArgumentParser, nice_gooey_argparse_main
from nicegooey.argparse.main import main_instance


@pytest.mark.nicegui_main_file(__file__)
async def test_store_const_action(user: User) -> None:
    """Test store_const action with checkbox."""

    await user.open("/")
    await user.should_see("verbose")

    assert main_instance.namespace.verbose == "NORMAL"

    checkbox = user.find(ui.checkbox)
    checkbox.click()

    assert main_instance.namespace.verbose == "VERBOSE"

    checkbox.click()

    assert main_instance.namespace.verbose == "NORMAL"


@nice_gooey_argparse_main(patch_argparse=False)
def main():
    parser = NgArgumentParser()
    parser.add_argument(
        "--verbose", action="store_const", const="VERBOSE", default="NORMAL", help="Enable verbose mode"
    )
    parser.parse_args()


if __name__ == "__main__":
    main()
