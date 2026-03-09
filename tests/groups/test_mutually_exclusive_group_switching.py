import pytest
from nicegui import ui
from nicegui.testing import User

from nicegooey.argparse import nice_gooey_argparse_main, NgArgumentParser
from nicegooey.argparse.main import main_instance


@pytest.mark.nicegui_main_file(__file__)
async def test_mutually_exclusive_group_switching(user: User) -> None:
    """Test switching between options in mutually exclusive group."""

    await user.open("/")

    # Find the select dropdown for the mutually exclusive group
    select = user.find(ui.select)
    select_element = next(iter(select.elements))
    assert isinstance(select_element, ui.select)
    assert select is not None

    # Verify the select dropdown shows "-" initially (since group is not required)
    await user.should_see("-")

    # Verify both options are available in the dropdown
    select.click()
    await user.should_see("--mode-fast")
    await user.should_see("--mode-slow")

    # Initially, namespace should not have "mode" since no option is selected (group not required)
    assert not hasattr(main_instance.namespace, "mode")

    # Select the first option (--mode-fast)
    user.find("--mode-fast").click()

    # Wait a moment for the UI to update
    await user.should_see("Fast mode")

    # Verify that the namespace reflects the selected option
    assert main_instance.namespace.mode == "fast"

    # Now switch to the second option (--mode-slow)
    select.click()
    await user.should_see("--mode-slow")
    user.find("--mode-slow").click()

    # Wait for the UI to update
    await user.should_see("Slow mode")

    # Verify the namespace still has mode set
    assert main_instance.namespace.mode == "slow"

    # Switch back to --mode-fast to verify switching works both ways
    select.click()
    await user.should_see("--mode-fast")
    user.find("--mode-fast").click()

    # Wait for the UI to update
    await user.should_see("Fast mode")

    # Verify mode
    assert main_instance.namespace.mode == "fast"

    # Switch to empty/none option to test deselection
    # TODO: make MRE and debug that or report it to Github
    select.click()
    await user.should_see("-")
    user.find("-").click()

    # After deselecting, the namespace attribute should be reset to default (None)
    assert select_element.value is None
    assert main_instance.namespace.mode is None


@nice_gooey_argparse_main(patch_argparse=False)
def main():
    parser = NgArgumentParser()

    me_group = parser.add_mutually_exclusive_group()
    me_group.add_argument("--mode-fast", action="store_const", const="fast", dest="mode", help="Fast mode")
    me_group.add_argument("--mode-slow", action="store_const", const="slow", dest="mode", help="Slow mode")

    parser.parse_args()


if __name__ == "__main__":
    main()
