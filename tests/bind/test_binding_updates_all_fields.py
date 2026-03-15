import pytest
from nicegui import ui
from nicegui.testing import User

from nicegooey.argparse import nice_gooey_argparse_main, NgArgumentParser
from nicegooey.argparse.main import main_instance


@pytest.mark.nicegui_main_file(__file__)
async def test_binding_updates_all_fields(user: User) -> None:
    """Test that updating one field updates all fields bound to the same dest."""

    await user.open("/")

    assert main_instance.namespace.name == "default"

    input1 = user.find(ui.input)
    input1.clear()
    input1.type("Alice")

    assert main_instance.namespace.name == "Alice"

    # TODO: finish the test


@nice_gooey_argparse_main(patch_argparse=False)
def main():
    parser = NgArgumentParser()
    parser.add_argument("--name1", dest="name", type=str, default="default", help="Name field 1")
    parser.add_argument("--name2", dest="name", type=str, help="Name field 2")
    parser.parse_args()


if __name__ == "__main__":
    main()
