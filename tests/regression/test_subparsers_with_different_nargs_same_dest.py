import pytest
from nicegui.testing import User, UserInteraction
from nicegui import ui, ElementFilter

from nicegooey.argparse import NgArgumentParser, nice_gooey_argparse_main
from nicegooey.argparse.ui_classes.actions.action_sync_element import ActionSyncElement
from nicegooey.argparse.ui_classes.groupings.subparser_ui import SubparserUi

from tests.conftest import exactly_one


@pytest.mark.nicegui_main_file(__file__)
async def test_subparsers_with_different_nargs_same_dest(user: User) -> None:
    """
    Regression test for subparsers with different nargs values for the same dest name.

    Tests that switching between subparsers properly resets UI state when they have
    different nargs configurations (nargs="*" vs nargs="+") for the same argument name.
    """
    await user.open("/")

    # Step 1: Open "a" -> the 'enable' box should be unchecked and the input-chips element empty
    await user.should_see("a")
    tab_a = user.find(marker=f"{SubparserUi.TAB_MARKER_PREFIX}a")
    tab_a.click()

    # Check that the enable checkbox is unchecked (need 2 within scopes: within action, within tabpanel)
    with user:
        enable_checkbox_a_filter = (
            ElementFilter(kind=ui.checkbox)
            .within(marker="ng-action-packages")
            .within(marker=f"{SubparserUi.TABPANEL_MARKER_PREFIX}a")
        )
        enable_checkbox_a = UserInteraction(user=user, elements=set(enable_checkbox_a_filter), target=None)
    assert exactly_one(enable_checkbox_a.elements).value is False, (
        "Enable checkbox should be unchecked initially"
    )

    # Check that the input-chips element is empty
    with user:
        chips_element_a_filter = (
            ElementFilter(marker=ActionSyncElement.NARGS_WRAPPER_MARKER)
            .within(marker="ng-action-packages")
            .within(marker=f"{SubparserUi.TABPANEL_MARKER_PREFIX}a")
        )
        chips_element_a = UserInteraction(user=user, elements=set(chips_element_a_filter), target=None)
    assert exactly_one(chips_element_a.elements).value == [], "Input-chips should be empty initially"

    # Step 2: Open "b" -> the input-chips should be empty
    await user.should_see("b")
    tab_b = user.find(marker=f"{SubparserUi.TAB_MARKER_PREFIX}b")
    tab_b.click()

    # Check that the enable checkbox is unchecked
    with user:
        enable_checkbox_b_filter = (
            ElementFilter(kind=ui.checkbox)
            .within(marker="ng-action-packages")
            .within(marker=f"{SubparserUi.TABPANEL_MARKER_PREFIX}b")
        )
        enable_checkbox_b = UserInteraction(user=user, elements=set(enable_checkbox_b_filter), target=None)
    assert exactly_one(enable_checkbox_b.elements).value is False, (
        "Enable checkbox should be unchecked when switching to 'b'"
    )

    # Check that the input-chips element is empty
    with user:
        chips_element_b_filter = (
            ElementFilter(marker=ActionSyncElement.NARGS_WRAPPER_MARKER)
            .within(marker="ng-action-packages")
            .within(marker=f"{SubparserUi.TABPANEL_MARKER_PREFIX}b")
        )
        chips_element_b = UserInteraction(user=user, elements=set(chips_element_b_filter), target=None)
    assert exactly_one(chips_element_b.elements).value == [], (
        "Input-chips should be empty when switching to 'b'"
    )

    # Step 3: Open "a" again -> the 'enable' box should be unchecked and the input-chips element empty; add an element
    tab_a.click()

    # Verify the checkbox is unchecked and input-chips is empty
    with user:
        enable_checkbox_a_filter = (
            ElementFilter(kind=ui.checkbox)
            .within(marker="ng-action-packages")
            .within(marker=f"{SubparserUi.TABPANEL_MARKER_PREFIX}a")
        )
        enable_checkbox_a = UserInteraction(user=user, elements=set(enable_checkbox_a_filter), target=None)
    assert exactly_one(enable_checkbox_a.elements).value is False, (
        "Enable checkbox should be unchecked after switching back to 'a'"
    )

    with user:
        chips_element_a_filter = (
            ElementFilter(marker=ActionSyncElement.NARGS_WRAPPER_MARKER)
            .within(marker="ng-action-packages")
            .within(marker=f"{SubparserUi.TABPANEL_MARKER_PREFIX}a")
        )
        chips_element_a = UserInteraction(user=user, elements=set(chips_element_a_filter), target=None)
    assert exactly_one(chips_element_a.elements).value == [], (
        "Input-chips should be empty after switching back to 'a'"
    )

    # Add an element to subparser "a" (need to enable first)
    enable_checkbox_a.click()  # Enable the input first
    assert exactly_one(enable_checkbox_a.elements).value is True, (
        "Enable checkbox should be checked after clicking"
    )

    with user:
        packages_element_filter = (
            ElementFilter(
                marker=ActionSyncElement.BASIC_ELEMENT_MARKER
                + ActionSyncElement.LIST_INNER_ELEMENT_MARKER_SUFFIX
            )
            .within(marker="ng-action-packages")
            .within(marker=f"{SubparserUi.TABPANEL_MARKER_PREFIX}a")
        )
        packages_element = UserInteraction(user=user, elements=set(packages_element_filter), target=None)

        packages_add_button_filter = (
            ElementFilter(marker=ActionSyncElement.ADD_BUTTON_MARKER)
            .within(marker="ng-action-packages")
            .within(marker=f"{SubparserUi.TABPANEL_MARKER_PREFIX}a")
        )
        packages_add_button = UserInteraction(
            user=user, elements=set(packages_add_button_filter), target=None
        )

    packages_element.type("numpy")
    packages_add_button.click()

    # Verify the chip was added
    with user:
        chips_element_a_filter = (
            ElementFilter(marker=ActionSyncElement.NARGS_WRAPPER_MARKER)
            .within(marker="ng-action-packages")
            .within(marker=f"{SubparserUi.TABPANEL_MARKER_PREFIX}a")
        )
        chips_element_a = UserInteraction(user=user, elements=set(chips_element_a_filter), target=None)
    assert exactly_one(chips_element_a.elements).value == ["numpy"], "Input-chips should contain 'numpy'"

    # Step 4: Open "b" -> the input-chips should be empty; add an element
    tab_b.click()

    # Verify the checkbox is unchecked and input-chips is empty
    with user:
        enable_checkbox_b_filter = (
            ElementFilter(kind=ui.checkbox)
            .within(marker="ng-action-packages")
            .within(marker=f"{SubparserUi.TABPANEL_MARKER_PREFIX}b")
        )
        enable_checkbox_b = UserInteraction(user=user, elements=set(enable_checkbox_b_filter), target=None)
    assert exactly_one(enable_checkbox_b.elements).value is False, (
        "Enable checkbox should be unchecked when switching to 'b'"
    )

    with user:
        chips_element_b_filter = (
            ElementFilter(marker=ActionSyncElement.NARGS_WRAPPER_MARKER)
            .within(marker="ng-action-packages")
            .within(marker=f"{SubparserUi.TABPANEL_MARKER_PREFIX}b")
        )
        chips_element_b = UserInteraction(user=user, elements=set(chips_element_b_filter), target=None)
    assert exactly_one(chips_element_b.elements).value == [], (
        "Input-chips should be empty when switching to 'b'"
    )

    # Add an element to subparser "b" (also need to enable first for nargs="+")
    enable_checkbox_b.click()  # Enable the input first
    assert exactly_one(enable_checkbox_b.elements).value is True, (
        "Enable checkbox should be checked after clicking"
    )

    with user:
        packages_element_b_filter = (
            ElementFilter(
                marker=ActionSyncElement.BASIC_ELEMENT_MARKER
                + ActionSyncElement.LIST_INNER_ELEMENT_MARKER_SUFFIX
            )
            .within(marker="ng-action-packages")
            .within(marker=f"{SubparserUi.TABPANEL_MARKER_PREFIX}b")
        )
        packages_element_b = UserInteraction(user=user, elements=set(packages_element_b_filter), target=None)

        packages_add_button_b_filter = (
            ElementFilter(marker=ActionSyncElement.ADD_BUTTON_MARKER)
            .within(marker="ng-action-packages")
            .within(marker=f"{SubparserUi.TABPANEL_MARKER_PREFIX}b")
        )
        packages_add_button_b = UserInteraction(
            user=user, elements=set(packages_add_button_b_filter), target=None
        )

    packages_element_b.type("pandas")
    packages_add_button_b.click()

    # Verify the chip was added
    with user:
        chips_element_b_filter = (
            ElementFilter(marker=ActionSyncElement.NARGS_WRAPPER_MARKER)
            .within(marker="ng-action-packages")
            .within(marker=f"{SubparserUi.TABPANEL_MARKER_PREFIX}b")
        )
        chips_element_b = UserInteraction(user=user, elements=set(chips_element_b_filter), target=None)
    assert exactly_one(chips_element_b.elements).value == ["pandas"], "Input-chips should contain 'pandas'"

    # Step 5: Open "a" -> the 'enable' box should be unchecked and the input-chips element empty
    tab_a.click()

    # Verify the checkbox is unchecked and input-chips is empty
    with user:
        enable_checkbox_a_filter = (
            ElementFilter(kind=ui.checkbox)
            .within(marker="ng-action-packages")
            .within(marker=f"{SubparserUi.TABPANEL_MARKER_PREFIX}a")
        )
        enable_checkbox_a = UserInteraction(user=user, elements=set(enable_checkbox_a_filter), target=None)
    assert exactly_one(enable_checkbox_a.elements).value is False, (
        "Enable checkbox should be unchecked when switching back to 'a'"
    )

    with user:
        chips_element_a_filter = (
            ElementFilter(marker=ActionSyncElement.NARGS_WRAPPER_MARKER)
            .within(marker="ng-action-packages")
            .within(marker=f"{SubparserUi.TABPANEL_MARKER_PREFIX}a")
        )
        chips_element_a = UserInteraction(user=user, elements=set(chips_element_a_filter), target=None)
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
