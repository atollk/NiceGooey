import pytest
from nicegui.testing import User

from nicegooey.argparse import NgArgumentParser, nice_gooey_argparse_main
from nicegooey.argparse.main import main_instance


@pytest.mark.nicegui_main_file(__file__)
async def test_string_action_with_choices_const(user: User) -> None:
    """Test that when a const is specified it takes priority as the initial value."""

    await user.open("/")
    await user.should_see("fruit")

    assert main_instance.namespace.fruit == "orange"


@nice_gooey_argparse_main(patch_argparse=False)
def main() -> None:
    parser = NgArgumentParser()
    parser.add_argument(
        "--fruit",
        choices=["apple", "banana", "orange"],
        const="orange",
        default="apple",
        nargs="?",
        help="Pick a fruit",
    )
    parser.parse_args()


if __name__ == "__main__":
    main()
