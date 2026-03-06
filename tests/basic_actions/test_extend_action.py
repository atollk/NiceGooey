import pytest
from nicegui.testing import User

from nicegooey.argparse import nice_gooey_argparse_main, NgArgumentParser
from nicegooey.argparse.main import main_instance


@pytest.mark.nicegui_main_file(__file__)
async def test_extend_action(user: User) -> None:
    """Test extend action (similar UI to append)."""

    await user.open("/")
    await user.should_see("items")

    assert main_instance.namespace.items == []

    input_field = user.find(marker="ng-action-type-input-basic")
    assert len(input_field.elements) == 1
    add_button = user.find(marker="ng-action-add-button")
    assert len(add_button.elements) == 1

    input_field.type("apple")
    add_button.click()
    assert main_instance.namespace.items == ["apple"]

    input_field.clear()
    input_field.type("banana")
    add_button.click()
    assert main_instance.namespace.items == ["apple", "banana"]


@nice_gooey_argparse_main(patch_argparse=False)
def main():
    parser = NgArgumentParser()
    parser.add_argument(
        "--item", action="extend", nargs="+", type=str, dest="items", help="Extend items", required=True
    )
    parser.parse_args()


if __name__ == "__main__":
    main()
