import pytest
from nicegui.testing import User

from nicegooey.argparse import nice_gooey_argparse_main, NgArgumentParser
from nicegooey.argparse.main import main_instance
from nicegooey.argparse.ui_classes.actions.action_sync_element import ActionSyncElement


@pytest.mark.nicegui_main_file(__file__)
async def test_append_const_action(user: User) -> None:
    """Test append_const action (button to append constant values)."""

    await user.open("/")
    await user.should_see("add-flag")

    assert main_instance.namespace.flags == []

    add_button = user.find(marker=ActionSyncElement.ADD_BUTTON_MARKER)
    assert len(add_button.elements) == 1

    add_button.click()
    assert main_instance.namespace.flags == ["FLAG"]

    add_button.click()
    assert main_instance.namespace.flags == ["FLAG", "FLAG"]

    add_button.click()
    assert main_instance.namespace.flags == ["FLAG", "FLAG", "FLAG"]


@nice_gooey_argparse_main(patch_argparse=False)
def main():
    parser = NgArgumentParser()
    parser.add_argument("--add-flag", action="append_const", const="FLAG", dest="flags", help="Add flag")
    parser.parse_args()


if __name__ == "__main__":
    main()
