import pytest
from nicegui.testing import User

from nicegooey.argparse import NgArgumentParser, nice_gooey_argparse_main
from nicegooey.argparse.main import main_instance


@pytest.mark.nicegui_main_file(__file__)
async def test_string_action_with_choices_default(user: User) -> None:
    """Test that when a default is specified it is used as the initial value, not the first option."""

    await user.open("/")
    await user.should_see("fruit")

    assert main_instance.namespace.fruit == "banana"


@nice_gooey_argparse_main(patch_argparse=False)
def main() -> None:
    parser = NgArgumentParser()
    parser.add_argument(
        "--fruit", choices=["apple", "banana"], default="banana", help="Pick a fruit", required=True
    )
    parser.parse_args()


if __name__ == "__main__":
    main()
