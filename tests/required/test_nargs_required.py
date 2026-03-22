import pytest
from nicegui import ui
from nicegui.testing import User

from nicegooey.argparse import NgArgumentParser, nice_gooey_argparse_main


@pytest.mark.nicegui_main_file(__file__)
async def test_nargs_required(user: User) -> None:
    """
    Test that the enable checkbox is correctly shown/hidden based on the required parameter.

    - required=True with nargs=* or nargs=+ -> no enable checkbox
    - required=False with nargs=* or nargs=+ -> has enable checkbox
    """
    from nicegooey.argparse.ui_classes.actions.action_ui_element import ActionUiElement
    from tests.conftest import find_within

    await user.open("/")

    # Test 1: required=True, nargs="*" -> no enable checkbox
    # The list input should be visible without an enable checkbox
    packages_star_required = find_within(
        user,
        marker=ActionUiElement.BASIC_ELEMENT_MARKER + ActionUiElement.LIST_INNER_ELEMENT_MARKER_SUFFIX,
        within_marker="ng-action-packages_star_required",
    )
    assert packages_star_required is not None, "List input for required nargs='*' should be visible"

    # Verify no enable checkbox exists for this field
    try:
        find_within(user, kind=ui.checkbox, within_marker="ng-action-packages_star_required")
        assert False, "Should not have enable checkbox for required=True, nargs='*'"
    except (ValueError, AssertionError):
        pass  # Expected - no checkbox should exist

    # Test 2: required=True, nargs="+" -> no enable checkbox
    packages_plus_required = find_within(
        user,
        marker=ActionUiElement.BASIC_ELEMENT_MARKER + ActionUiElement.LIST_INNER_ELEMENT_MARKER_SUFFIX,
        within_marker="ng-action-packages_plus_required",
    )
    assert packages_plus_required is not None, "List input for required nargs='+' should be visible"

    # Verify no enable checkbox exists for this field
    try:
        find_within(user, kind=ui.checkbox, within_marker="ng-action-packages_plus_required")
        assert False, "Should not have enable checkbox for required=True, nargs='+'"
    except (ValueError, AssertionError):
        pass  # Expected - no checkbox should exist

    # Test 3: required=False, nargs="*" -> has enable checkbox
    enable_checkbox_star = find_within(
        user, kind=ui.checkbox, within_marker="ng-action-packages_star_optional"
    )
    assert enable_checkbox_star is not None, "Enable checkbox should exist for required=False, nargs='*'"

    # Test 4: required=False, nargs="+" -> has enable checkbox
    enable_checkbox_plus = find_within(
        user, kind=ui.checkbox, within_marker="ng-action-packages_plus_optional"
    )
    assert enable_checkbox_plus is not None, "Enable checkbox should exist for required=False, nargs='+'"


@nice_gooey_argparse_main(patch_argparse=False)
def main():
    parser = NgArgumentParser()

    # Case 1: required=True, nargs="*" -> no enable checkbox
    parser.add_argument(
        "--packages-star-required", type=str, nargs="*", required=True, help="Required packages (nargs='*')"
    )

    # Case 2: required=True, nargs="+" -> no enable checkbox
    parser.add_argument(
        "--packages-plus-required", type=str, nargs="+", required=True, help="Required packages (nargs='+')"
    )

    # Case 3: required=False, nargs="*" -> has enable checkbox
    parser.add_argument(
        "--packages-star-optional", type=str, nargs="*", required=False, help="Optional packages (nargs='*')"
    )

    # Case 4: required=False, nargs="+" -> has enable checkbox
    parser.add_argument(
        "--packages-plus-optional", type=str, nargs="+", required=False, help="Optional packages (nargs='+')"
    )

    parser.parse_args()


if __name__ == "__main__":
    main()
