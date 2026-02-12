import pytest
from nicegui import ui
from nicegui.testing import User

from nicegooey.argparse import nice_gooey_argparse_main, NgArgumentParser
from nicegooey.argparse.main import main_instance


@pytest.mark.nicegui_main_file(__file__)
async def test_store_true_action(user: User) -> None:
    """Test store_true action (checkbox that stores True)."""

    await user.open("/")
    await user.should_see("enable")

    assert main_instance.namespace.enable is False

    checkbox = user.find(ui.checkbox)
    checkbox.click()

    assert main_instance.namespace.enable is True


@nice_gooey_argparse_main(patch_argparse=False)
def main():
    parser = NgArgumentParser()
    parser.add_argument("--enable", action="store_true", help="Enable feature")
    parser.parse_args()


if __name__ == "__main__":
    main()
