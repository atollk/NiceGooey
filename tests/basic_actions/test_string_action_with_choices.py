import pytest
from nicegui import ui
from nicegui.testing import User

from nicegooey.argparse import nice_gooey_argparse_main, NgArgumentParser
from nicegooey.argparse.main import main_instance


@pytest.mark.nicegui_main_file(__file__)
async def test_string_action_with_choices(user: User) -> None:
    """Test string action with choices renders as select dropdown."""

    await user.open("/")
    await user.should_see("fruit")

    select = user.find(ui.select)
    select.click()
    await user.should_see("banana")
    user.find("banana").click()

    assert main_instance.namespace.fruit == "banana"


@nice_gooey_argparse_main(patch_argparse=False)
def main():
    parser = NgArgumentParser()
    parser.add_argument("--fruit", choices=["apple", "banana", "orange"], help="Pick a fruit", required=True)
    parser.parse_args()


if __name__ == "__main__":
    main()
