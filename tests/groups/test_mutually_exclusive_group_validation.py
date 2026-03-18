import pytest
from nicegui import ui
from nicegui.testing import User

from nicegooey.argparse import NgArgumentParser, nice_gooey_argparse_main


@pytest.mark.nicegui_main_file(__file__)
async def test_mutually_exclusive_group_validation(user: User) -> None:
    """Test that ME groups validate correctly - only one option can be set."""

    await user.open("/")

    select = user.find(ui.select)
    assert select is not None

    select.click()


@nice_gooey_argparse_main(patch_argparse=False)
def main():
    parser = NgArgumentParser()

    me_group = parser.add_mutually_exclusive_group(required=True)
    me_group.add_argument("--json", action="store_true", dest="format_json", help="JSON output")
    me_group.add_argument("--xml", action="store_true", dest="format_xml", help="XML output")

    parser.parse_args()


if __name__ == "__main__":
    main()
