import pytest
from nicegui.testing import User

from nicegooey.argparse import nice_gooey_argparse_main, NgArgumentParser
from nicegooey.argparse.main import main_instance


@pytest.mark.nicegui_main_file(__file__)
async def test_list_actions_with_same_dest_share_list(user: User) -> None:
    """Test that multiple list actions sharing a dest share the same underlying list."""

    await user.open("/")

    await user.should_see("add-a")
    await user.should_see("add-b")

    assert main_instance.namespace.items == []


@nice_gooey_argparse_main(patch_argparse=False)
def main():
    parser = NgArgumentParser()
    parser.add_argument("--add-a", action="append", dest="items", type=str, help="Add via A")
    parser.add_argument("--add-b", action="append", dest="items", type=str, help="Add via B")
    parser.parse_args()


if __name__ == "__main__":
    main()
