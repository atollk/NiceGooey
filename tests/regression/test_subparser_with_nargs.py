import pytest
from nicegui.testing import User

from nicegooey.argparse import NgArgumentParser, nice_gooey_argparse_main
from nicegooey.argparse.main import main_instance
from nicegooey.argparse.ui_classes.actions.action_ui_element import ActionUiElement
from nicegooey.argparse.ui_classes.groupings.subparser_ui import SubparserUi


@pytest.mark.nicegui_main_file(__file__)
async def test_subparser_with_nargs(user: User) -> None:
    """Test positional argument with nargs='*' in subparser."""
    await user.open("/")

    # Navigate to the run subparser
    await user.should_see("run")
    run_tab = user.find(marker=f"{SubparserUi.TAB_MARKER_PREFIX}run")
    run_tab.click()

    # Verify command is set
    assert main_instance.namespace.command == "run"

    # Check initial namespace value for args (should be empty list for nargs="*")
    assert main_instance.namespace.args == []

    # Add an element to args
    basic_element = user.find(
        marker=ActionUiElement.BASIC_ELEMENT_MARKER + ActionUiElement.LIST_INNER_ELEMENT_MARKER_SUFFIX
    )
    add_button = user.find(marker=ActionUiElement.ADD_BUTTON_MARKER)
    assert len(basic_element.elements) == len(add_button.elements) == 1
    basic_element.type("value_1")
    add_button.click()

    # Verify namespace is updated correctly
    assert main_instance.namespace.args == ["value_1"]

    # Add a second element to args
    basic_element.type("value_2")
    add_button.click()

    # Verify namespace now contains both values
    assert main_instance.namespace.args == ["value_1", "value_2"]


@nice_gooey_argparse_main(patch_argparse=False)
def main():
    parser = NgArgumentParser()
    subparsers = parser.add_subparsers(dest="command", help="Commands", required=True)
    parser_run = subparsers.add_parser("run", help="Run a command or script")
    parser_run.add_argument("--args", nargs="*", type=str, help="Arguments for the command", required=True)
    parser.parse_args()


if __name__ == "__main__":
    main()
