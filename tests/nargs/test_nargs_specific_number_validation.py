import pytest
from nicegui.testing import User

from nicegooey.argparse import NgArgumentParser, nice_gooey_argparse_main
from nicegooey.argparse.main import main_instance
from nicegooey.argparse.ui_classes.actions.action_sync_element import ActionSyncElement


@pytest.mark.nicegui_main_file(__file__)
async def test_nargs_specific_number_validation(user: User) -> None:
    """Test that nargs with specific number enforces exactly that many values."""

    await user.open("/")

    await user.should_see("rgb")

    # Verify initial namespace
    assert main_instance.namespace.rgb in (None, [], [0, 0, 0])

    # Add three RGB values
    basic_element = user.find(
        marker=ActionSyncElement.BASIC_ELEMENT_MARKER + ActionSyncElement.LIST_INNER_ELEMENT_MARKER_SUFFIX
    )
    add_button = user.find(marker=ActionSyncElement.ADD_BUTTON_MARKER)

    # Add first value (R)
    basic_element.type("255")
    add_button.click()
    # TODO: verify validation failure

    # Add second value (G)
    basic_element.type("128")
    add_button.click()
    # TODO: verify validation failure

    # Add third value (B)
    basic_element.type("64")
    add_button.click()
    # TODO: verify validation pass

    # Verify namespace contains all three values
    assert main_instance.namespace.rgb == [255, 128, 64]


@nice_gooey_argparse_main(patch_argparse=False)
def main():
    parser = NgArgumentParser()
    parser.add_argument("--rgb", nargs=3, type=int, help="RGB color (3 integers)", required=True)
    parser.parse_args()


if __name__ == "__main__":
    main()
