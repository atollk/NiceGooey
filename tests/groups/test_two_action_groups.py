import pytest
from nicegui.testing import User

from nicegooey.argparse import nice_gooey_argparse_main, NgArgumentParser


@pytest.mark.nicegui_main_file(__file__)
async def test_two_action_groups(user: User) -> None:
    """Test that two action groups render as separate cards."""

    await user.open("/")

    await user.should_see("Database Options")
    await user.should_see("Logging Options")

    await user.should_see("db-host")
    await user.should_see("db-port")
    await user.should_see("log-level")
    await user.should_see("log-file")


@nice_gooey_argparse_main(patch_argparse=False)
def main():
    parser = NgArgumentParser()

    parser.add_argument("--global-option", type=str, help="Global option")

    group1 = parser.add_argument_group(title="Database Options")
    group1.add_argument("--db-host", type=str, help="Database host")
    group1.add_argument("--db-port", type=int, help="Database port")

    group2 = parser.add_argument_group(title="Logging Options")
    group2.add_argument("--log-level", type=str, choices=["DEBUG", "INFO", "ERROR"], help="Log level")
    group2.add_argument("--log-file", type=str, help="Log file path")

    parser.parse_args()


if __name__ == "__main__":
    main()
