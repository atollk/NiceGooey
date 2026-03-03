import pytest
from nicegui import ui
from nicegui.testing import User

from nicegooey.argparse import nice_gooey_argparse_main, NgArgumentParser
from nicegooey.argparse.main import main_instance


@pytest.mark.nicegui_main_file(__file__)
async def test_two_store_actions_same_dest_last_wins(user: User) -> None:
    """Test that when two store actions share a dest, the last update wins."""

    await user.open("/")

    await user.should_see("field_a")
    await user.should_see("field_b")

    input_a = user.find(ui.input)
    input_a.clear()
    input_a.type("value-a")

    assert main_instance.namespace.shared == "value-a"


@nice_gooey_argparse_main(patch_argparse=False)
def main():
    parser = NgArgumentParser()
    parser.add_argument("--field-a", dest="shared", type=str, help="Field A")
    parser.add_argument("--field-b", dest="shared", type=str, help="Field B")
    parser.parse_args()


if __name__ == "__main__":
    main()
