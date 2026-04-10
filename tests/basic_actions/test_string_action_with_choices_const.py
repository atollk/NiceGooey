import pytest
from nicegui.testing import User

from nicegooey.argparse import NgArgumentParser, nice_gooey_argparse_main


@pytest.mark.nicegui_main_file(__file__)
async def test_string_action_with_choices_const(user: User) -> None:
    """Test that when a const is specified it takes priority as the initial value."""

    await user.open("/")
    await user.should_see("fruit")
    await user.should_see("required_fruit")

    # TODO: the namespace value should be "apple" at first for "fruit" but "orange" for "required-fruit". but the default selection of the element should be "orange" in both cases from the start. when enabling "fruit", the namespace value should then also be "orange".


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
    parser.add_argument(
        "--required_fruit",
        choices=["apple", "banana", "orange"],
        const="orange",
        default="apple",
        help="Pick a fruit",
        required=True,
        nargs="?",
    )
    parser.parse_args()


if __name__ == "__main__":
    main()
