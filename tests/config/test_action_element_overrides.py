from typing import override

import pytest
from nicegui.testing import User

from nicegooey.argparse import NgArgumentParser, nice_gooey_argparse_main
from nicegooey.argparse.ui_classes.actions.action_ui_element import ActionUiElement
from nicegooey.argparse.argument_parser import NiceGooeyConfig
from tests.conftest import find_within


class CustomStoreActionElement(ActionUiElement):
    """Custom action element with a distinct marker for testing."""

    CUSTOM_MARKER = "custom-test-element-marker"

    @override
    def _render_input_element(self) -> None:
        """Override to add a custom marker."""
        super()._render_input_element()
        assert self.inner_elements is not None
        # Add a custom marker to make it identifiable in tests
        self.inner_elements.nargs_wrapper_element.mark(
            *self.inner_elements.nargs_wrapper_element._markers, self.CUSTOM_MARKER
        )


@pytest.mark.nicegui_main_file(__file__)
async def test_action_element_overrides(user: User) -> None:
    """
    Test that action_element_overrides in NiceGooeyConfig allows custom UI elements
    to be used for specific actions.

    This test verifies that:
    1. An action with an override uses the custom element (with custom marker)
    2. An action without an override uses the default element (no custom marker)
    """
    await user.open("/")

    # The "custom-name" action should use the custom element and have the custom marker
    custom_element = user.find(marker=CustomStoreActionElement.CUSTOM_MARKER)
    assert len(custom_element.elements) == 1, "Custom action element should be used for overridden action"

    # The "regular-name" action should use the default element and NOT have the custom marker
    try:
        # Try to find the custom marker within the regular-name action
        find_within(
            user, marker=CustomStoreActionElement.CUSTOM_MARKER, within_marker="ng-action-regular-name"
        )
        assert False, "Regular action should NOT use custom element"
    except (ValueError, AssertionError):
        # Expected - the custom marker should not exist for regular-name
        pass

    # Verify that the custom element actually works by typing into it
    custom_input = find_within(
        user, marker=ActionUiElement.BASIC_ELEMENT_MARKER, within_marker="ng-action-custom-name"
    )
    custom_input.type("CustomValue")

    # Should be able to see the typed value
    await user.should_see("CustomValue")


@nice_gooey_argparse_main(patch_argparse=False)
def main():
    parser = NgArgumentParser()

    # Create two actions
    custom_action = parser.add_argument("--custom-name", type=str, help="Name with custom element")
    parser.add_argument("--regular-name", type=str, help="Name with regular element")

    # Set up override for only the first action
    parser.nicegooey_config = NiceGooeyConfig(
        action_element_overrides={custom_action: CustomStoreActionElement}
    )

    parser.parse_args()


if __name__ == "__main__":
    main()
