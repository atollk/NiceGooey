import pytest
from nicegui.testing import User

from nicegooey.argparse import NgArgumentParser, nice_gooey_argparse_main
from nicegooey.argparse.ui_classes.groupings.subparser_ui import SubparserUi


@pytest.mark.nicegui_main_file(__file__)
async def test_subparser_with_groups(user: User) -> None:
    """Test subparser that contains argument groups."""

    await user.open("/")

    await user.should_see("config")

    # Click "config" tab
    config_tab = user.find(marker=f"{SubparserUi.TAB_MARKER_PREFIX}config")
    config_tab.click()

    # Verify "Database Config" group is visible with its fields
    await user.should_see("Database Config")
    await user.should_see("db-host")
    await user.should_see("db-port")

    # Verify "Cache Config" group is visible with its fields
    await user.should_see("Cache Config")
    await user.should_see("cache-size")
    await user.should_see("cache-ttl")


@nice_gooey_argparse_main(patch_argparse=False)
def main() -> None:
    parser = NgArgumentParser()

    subparsers = parser.add_subparsers(dest="command", help="Commands")

    parser_config = subparsers.add_parser("config", help="Configuration command")

    group1 = parser_config.add_argument_group(title="Database Config")
    group1.add_argument("--db-host", type=str, help="Database host")
    group1.add_argument("--db-port", type=int, help="Database port")

    group2 = parser_config.add_argument_group(title="Cache Config")
    group2.add_argument("--cache-size", type=int, help="Cache size")
    group2.add_argument("--cache-ttl", type=int, help="Cache TTL")

    parser.parse_args()


if __name__ == "__main__":
    main()
