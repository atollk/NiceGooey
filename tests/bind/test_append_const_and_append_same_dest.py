import pytest
from nicegui import ui
from nicegui.testing import User

from nicegooey.argparse import nice_gooey_argparse_main, NgArgumentParser
from nicegooey.argparse.main import main_instance


@pytest.mark.nicegui_main_file(__file__)
async def test_append_const_and_append_same_dest(user: User) -> None:
    """Test append_const and append actions with same dest - verify list synchronization."""

    await user.open("/")

    await user.should_see("add-flag")
    await user.should_see("add-item")

    assert main_instance.namespace.items == []

    add_const_button = user.find(ui.button).filter(
        lambda x: x.element.props.get("data-testid") == "ng-action-add-button"
    )
    add_const_button.click()

    assert "FLAG" in main_instance.namespace.items

    input_field = user.find(marker="ng-action-type-input-basic")
    input_field.type("custom")


@nice_gooey_argparse_main(patch_argparse=False)
def main():
    parser = NgArgumentParser()
    parser.add_argument(
        "--add-flag", action="append_const", const="FLAG", dest="items", help="Add flag constant"
    )
    parser.add_argument("--add-item", action="append", type=str, dest="items", help="Add custom item")
    parser.parse_args()


if __name__ == "__main__":
    main()
