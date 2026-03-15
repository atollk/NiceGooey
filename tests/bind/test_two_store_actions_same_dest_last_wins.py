import pytest
from nicegui import ui
from nicegui.testing import User

from nicegooey.argparse import nice_gooey_argparse_main, NgArgumentParser
from nicegooey.argparse.main import main_instance


@pytest.mark.nicegui_main_file(__file__)
async def test_two_store_actions_same_dest_last_wins(user: User) -> None:
    """Test that when two store actions share a dest, the last update wins."""

    await user.open("/")

    await user.should_see("field-a")
    await user.should_see("field-b")

    input_a, input_b = user.find(ui.input).elements
    input_a.value = "value-a"
    input_b.value = "value-b"

    assert main_instance.namespace.shared == "value-b"


@nice_gooey_argparse_main(patch_argparse=False)
def main():
    parser = NgArgumentParser()
    parser.add_argument("--field-a", dest="shared", type=str, help="Field A", required=True)
    parser.add_argument("--field-b", dest="shared", type=str, help="Field B", required=True)
    parser.parse_args()


if __name__ == "__main__":
    main()
