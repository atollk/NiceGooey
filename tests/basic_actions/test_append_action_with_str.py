import pytest
from nicegui.testing import User

from nicegooey.argparse import nice_gooey_argparse_main, NgArgumentParser
from nicegooey.argparse.main import main_instance
from nicegooey.argparse.ui_classes.actions.action_input_base import ActionInputBaseElement


@pytest.mark.nicegui_main_file(__file__)
async def test_append_action_with_str(user: User) -> None:
    """Test append action with string type."""

    await user.open("/")
    await user.should_see("tags")

    assert main_instance.namespace.tags == []

    input_field = user.find(marker=ActionInputBaseElement.LIST_INNER_ELEMENT_MARKER)
    assert len(input_field.elements) == 1
    add_button = user.find(marker=ActionInputBaseElement.ADD_BUTTON_MARKER)
    assert len(add_button.elements) == 1

    input_field.type("python")
    add_button.click()
    assert main_instance.namespace.tags == ["python"]

    input_field.clear()
    input_field.type("testing")
    add_button.click()
    assert main_instance.namespace.tags == ["python", "testing"]

    input_field.clear()
    input_field.type("nicegui")
    add_button.click()
    assert main_instance.namespace.tags == ["python", "testing", "nicegui"]


@nice_gooey_argparse_main(patch_argparse=False)
def main():
    parser = NgArgumentParser()
    parser.add_argument("--tag", action="append", type=str, dest="tags", help="Add tags", required=True)
    parser.parse_args()


if __name__ == "__main__":
    main()
