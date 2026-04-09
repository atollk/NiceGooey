import pytest
from nicegui.testing import User

from nicegooey.argparse import NgArgumentParser, nice_gooey_argparse_main
from nicegooey.argparse.main import main_instance


@pytest.mark.nicegui_main_file(__file__)
async def test_string_action_with_choices_fallback(user: User) -> None:
    """Test that when no const or default is set, the first choice is used as the initial value."""

    await user.open("/")
    await user.should_see("fruit")

    assert main_instance.namespace.fruit == "apple"


@nice_gooey_argparse_main(patch_argparse=False)
def main() -> None:
    parser = NgArgumentParser()
    # No default, no const — should fall back to first choice
    parser.add_argument("--fruit", choices=["apple", "banana"], help="Pick a fruit", required=True)
    parser.parse_args()


if __name__ == "__main__":
    main()
