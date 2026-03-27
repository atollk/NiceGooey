import pytest
from nicegui.testing import User

from nicegooey.argparse import NgArgumentParser, nice_gooey_argparse_main
from nicegooey.argparse.main import main_instance
from nicegooey.argparse.ui_classes.actions.action_ui_element import ActionUiElement

from nicegui import ui, ElementFilter
from nicegui.testing import UserInteraction
from nicegooey.argparse.ui_classes.actions.standard_actions import ListActionUiElement


@pytest.mark.nicegui_main_file(__file__)
async def test_nargs_asterisk_append(user: User) -> None:
    """
    Test append action with nargs='*' - creates a list of lists.

    With action="append" and nargs="*", each invocation creates a list,
    and those lists are appended together. For example:
        --items a b --items c d
    Results in: [['a', 'b'], ['c', 'd']]
    """
    await user.open("/")
    await user.should_see("items")

    # Initial state should be an empty list
    assert main_instance.namespace.items == []

    # For append with nargs="*", there's a nested structure:
    # - Inner chips (nargs="*") for entering a list of strings
    # - Outer list (append) for collecting multiple such lists
    # - Inner add button (marked) for adding strings to inner chips
    # - Outer add button (unmarked) for adding inner chips value to outer list

    # Find the inner chips element (for nargs="*")
    user.find(marker=ActionUiElement.NARGS_WRAPPER_MARKER)

    # Find the outer list element
    user.find(marker=ListActionUiElement.LIST_ELEMENT_MARKER)

    # Find all buttons within the required wrapper
    with user:
        buttons_filter = ElementFilter(kind=ui.button).within(marker=ActionUiElement.REQUIRED_WRAPPER_MARKER)
        all_buttons_interaction = UserInteraction(user=user, elements=set(buttons_filter), target=None)

    all_buttons = list(all_buttons_interaction.elements)

    # Filter to get the outer button (the one without ADD_BUTTON_MARKER)
    outer_button_el = [
        b for b in all_buttons if ActionUiElement.ADD_BUTTON_MARKER not in getattr(b, "_markers", [])
    ][0]

    # Create UserInteraction for the outer button
    with user:
        outer_button = UserInteraction(user=user, elements={outer_button_el}, target=None)

    # Find the basic input element (for typing individual strings) and inner add button
    basic_input = user.find(
        marker=ActionUiElement.BASIC_ELEMENT_MARKER + ActionUiElement.LIST_INNER_ELEMENT_MARKER_SUFFIX
    )
    inner_add_button = user.find(marker=ActionUiElement.ADD_BUTTON_MARKER)

    # Add first group: ["a", "b"]
    basic_input.type("a")
    inner_add_button.click()
    basic_input.type("b")
    inner_add_button.click()
    # Now the inner chips has ["a", "b"], click outer button to append to list
    outer_button.click()

    # Verify namespace now contains [["a", "b"]]
    assert main_instance.namespace.items == [["a", "b"]]

    # Add second group: ["c", "d"]
    basic_input.type("c")
    inner_add_button.click()
    basic_input.type("d")
    inner_add_button.click()
    outer_button.click()

    # Verify namespace now contains [["a", "b"], ["c", "d"]]
    assert main_instance.namespace.items == [["a", "b"], ["c", "d"]]

    # Add third group: ["e"]
    basic_input.type("e")
    inner_add_button.click()
    outer_button.click()

    # Verify namespace now contains [["a", "b"], ["c", "d"], ["e"]]
    assert main_instance.namespace.items == [["a", "b"], ["c", "d"], ["e"]]

    # Add an empty group: []
    # Just click the outer button without adding anything to inner chips
    outer_button.click()

    # Verify namespace now contains [["a", "b"], ["c", "d"], ["e"], []]
    assert main_instance.namespace.items == [["a", "b"], ["c", "d"], ["e"], []]


@nice_gooey_argparse_main(patch_argparse=False)
def main():
    parser = NgArgumentParser()
    parser.add_argument("--items", action="append", nargs="*", type=str, required=True)
    parser.parse_args()


if __name__ == "__main__":
    main()
