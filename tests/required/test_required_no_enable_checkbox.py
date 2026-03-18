import pytest
from nicegui import ui
from nicegui.testing import User

from nicegooey.argparse import nice_gooey_argparse_main, NgArgumentParser
from nicegooey.argparse.main import main_instance


@pytest.mark.nicegui_main_file(__file__)
async def test_required_no_enable_checkbox(user: User) -> None:
    """Test that required actions do not have an enable checkbox and namespace is set immediately."""

    await user.open("/")
    await user.should_see("name")

    # Verify there's no enable checkbox for required actions
    with pytest.raises(AssertionError):
        user.find(kind=ui.checkbox, marker="ng-action-type-input-enable-parameter-box")

    # The namespace should initially be empty string (no default provided)
    assert main_instance.namespace.name == ""

    # Find the input field and type in it
    input_field = user.find(ui.input)
    input_field.type("Alice")

    # The namespace should update immediately
    assert main_instance.namespace.name == "Alice"


@nice_gooey_argparse_main(patch_argparse=False)
def main():
    parser = NgArgumentParser()
    parser.add_argument("--name", type=str, help="Your name", required=True)
    parser.parse_args()


if __name__ == "__main__":
    main()
