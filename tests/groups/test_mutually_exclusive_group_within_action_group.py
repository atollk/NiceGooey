import pytest
from nicegui import ui
from nicegui.testing import User

from nicegooey.argparse import nice_gooey_argparse_main, NgArgumentParser


@pytest.mark.nicegui_main_file(__file__)
async def test_mutually_exclusive_group_within_action_group(user: User) -> None:
    """Test ME group nested within an action group."""

    await user.open("/")

    await user.should_see("Network Options")
    await user.should_see("timeout")

    select = user.find(ui.select)
    assert select is not None

    select.click()


@nice_gooey_argparse_main(patch_argparse=False)
def main():
    parser = NgArgumentParser()

    group = parser.add_argument_group(title="Network Options")
    group.add_argument("--timeout", type=int, help="Timeout in seconds")

    me_group = group.add_mutually_exclusive_group()
    me_group.add_argument("--ipv4", action="store_true", help="Use IPv4")
    me_group.add_argument("--ipv6", action="store_true", help="Use IPv6")

    parser.parse_args()


if __name__ == "__main__":
    main()
