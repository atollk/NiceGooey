import pytest
from nicegui import ui
from nicegui.testing import User

from nicegooey.argparse import nice_gooey_argparse_main, NgArgumentParser
from nicegooey.argparse.main import main_instance


@pytest.mark.nicegui_main_file(__file__)
async def test_store_false_action(user: User) -> None:
    """Test store_false action (checkbox that stores False when checked)."""

    await user.open("/")
    await user.should_see("cache")

    assert main_instance.namespace.cache is True

    checkbox = user.find(ui.checkbox)
    checkbox.click()

    assert main_instance.namespace.cache is False


@nice_gooey_argparse_main(patch_argparse=False)
def main():
    parser = NgArgumentParser()
    parser.add_argument("--no-cache", action="store_false", dest="cache", help="Disable cache")
    parser.parse_args()


if __name__ == "__main__":
    main()
