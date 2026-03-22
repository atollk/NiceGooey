import pytest
from nicegui.testing import User

from nicegooey.argparse import NgArgumentParser, nice_gooey_argparse_main
from nicegooey.argparse.ui_classes.actions.action_ui_element import ActionUiElement
from nicegooey.argparse.ui_classes.groupings.subparser_ui import SubparserUi

from tests.conftest import exactly_one, find_within


@pytest.mark.nicegui_main_file(__file__)
async def test_subparsers_with_different_nargs_same_dest(user: User) -> None:
    """
    Regression test for subparsers with different nargs values for the same dest name.

    Tests that switching between subparsers properly resets UI state when they have
    different nargs configurations (nargs="*" vs nargs="+") for the same argument name.
    """
    await user.open("/")

    # Find the relevant elements
    chips_element_a = find_within(
        user,
        marker=ActionUiElement.NARGS_WRAPPER_MARKER,
        within_marker="ng-action-packages",
        within_outer_marker=f"{SubparserUi.TABPANEL_MARKER_PREFIX}{'a'}",
    )
    chips_element_b = find_within(
        user,
        marker=ActionUiElement.NARGS_WRAPPER_MARKER,
        within_marker="ng-action-packages",
        within_outer_marker=f"{SubparserUi.TABPANEL_MARKER_PREFIX}{'b'}",
    )
    packages_element_a = find_within(
        user,
        marker=(ActionUiElement.BASIC_ELEMENT_MARKER + ActionUiElement.LIST_INNER_ELEMENT_MARKER_SUFFIX),
        within_marker="ng-action-packages",
        within_outer_marker=f"{SubparserUi.TABPANEL_MARKER_PREFIX}{'a'}",
    )
    packages_element_b = find_within(
        user,
        marker=(ActionUiElement.BASIC_ELEMENT_MARKER + ActionUiElement.LIST_INNER_ELEMENT_MARKER_SUFFIX),
        within_marker="ng-action-packages",
        within_outer_marker=f"{SubparserUi.TABPANEL_MARKER_PREFIX}{'b'}",
    )
    packages_add_button_a = find_within(
        user,
        marker=ActionUiElement.ADD_BUTTON_MARKER,
        within_marker="ng-action-packages",
        within_outer_marker=f"{SubparserUi.TABPANEL_MARKER_PREFIX}{'a'}",
    )
    packages_add_button_b = find_within(
        user,
        marker=ActionUiElement.ADD_BUTTON_MARKER,
        within_marker="ng-action-packages",
        within_outer_marker=f"{SubparserUi.TABPANEL_MARKER_PREFIX}{'b'}",
    )

    # Step 1: Open "a" -> the 'enable' box should be unchecked and the input-chips element empty
    await user.should_see("a")
    tab_a = user.find(marker=f"{SubparserUi.TAB_MARKER_PREFIX}a")
    tab_a.click()

    # Check that the input-chips element is empty
    assert exactly_one(chips_element_a.elements).value == [], "Input-chips should be empty initially"

    # Step 2: Open "b" -> the input-chips should be empty
    await user.should_see("b")
    tab_b = user.find(marker=f"{SubparserUi.TAB_MARKER_PREFIX}b")
    tab_b.click()

    # Check that the input-chips element is empty
    assert exactly_one(chips_element_b.elements).value == [], (
        "Input-chips should be empty when switching to 'b'"
    )

    # Step 3: Open "a" again -> the input-chips element empty; add an element
    tab_a.click()

    assert exactly_one(chips_element_a.elements).value == [], (
        "Input-chips should be empty after switching back to 'a'"
    )

    # Add an element to subparser "a"
    packages_element_a.type("numpy")
    packages_add_button_a.click()

    # Verify the chip was added
    assert exactly_one(chips_element_a.elements).value == ["numpy"], "Input-chips should contain 'numpy'"

    # Step 4: Open "b" -> the input-chips should be empty; add an element
    tab_b.click()

    assert exactly_one(chips_element_b.elements).value == [], (
        "Input-chips should be empty when switching to 'b'"
    )

    # Add an element to subparser "b"
    packages_element_b.type("pandas")
    packages_add_button_b.click()

    # Verify the chip was added
    assert exactly_one(chips_element_b.elements).value == ["pandas"], "Input-chips should contain 'pandas'"

    # Step 5: Open "a" -> the 'enable' box should be unchecked and the input-chips element empty
    tab_a.click()

    # Verify input-chips is empty
    assert exactly_one(chips_element_a.elements).value == [], (
        "Input-chips should be empty when switching back to 'a'"
    )


@nice_gooey_argparse_main(patch_argparse=False)
def main():
    parser = NgArgumentParser()
    subparsers = parser.add_subparsers()
    subp_a = subparsers.add_parser("a")
    subp_a.add_argument("packages", type=str, nargs="*")
    subp_b = subparsers.add_parser("b")
    subp_b.add_argument("packages", type=str, nargs="+")
    parser.parse_args()


if __name__ == "__main__":
    main()
