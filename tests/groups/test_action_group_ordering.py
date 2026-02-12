import pytest
from nicegui.testing import User

from nicegooey.argparse import nice_gooey_argparse_main, NgArgumentParser


@pytest.mark.nicegui_main_file(__file__)
async def test_action_group_ordering(user: User) -> None:
    """Test that actions within groups maintain their order."""

    await user.open("/")

    await user.should_see("Ordered Options")
    await user.should_see("first")
    await user.should_see("second")
    await user.should_see("third")


@nice_gooey_argparse_main(patch_argparse=False)
def main():
    parser = NgArgumentParser()

    group = parser.add_argument_group(title="Ordered Options")
    group.add_argument("--first", type=str, help="First option")
    group.add_argument("--second", type=str, help="Second option")
    group.add_argument("--third", type=str, help="Third option")

    parser.parse_args()


if __name__ == "__main__":
    main()
