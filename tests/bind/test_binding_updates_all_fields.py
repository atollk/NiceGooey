import pytest
from nicegui import ui
from nicegui.testing import User

from nicegooey.argparse import NgArgumentParser, nice_gooey_argparse_main
from nicegooey.argparse.main import main_instance


@pytest.mark.nicegui_main_file(__file__)
async def test_binding_updates_all_fields(user: User) -> None:
    """Test that updating one field updates all fields bound to the same dest."""

    await user.open("/")

    assert main_instance.namespace.name == "default"

    inputs = user.find(ui.input)
    assert len(inputs.elements) == 2

    input1, input2 = inputs.elements

    # Update the first input
    input1.value = "Alice"
    assert main_instance.namespace.name == "Alice"
    assert input2.value == "Alice"  # Second input should be updated too

    # Update the second input
    input2.value = "Bob"
    assert main_instance.namespace.name == "Bob"
    assert input1.value == "Bob"  # First input should be updated too


@nice_gooey_argparse_main(patch_argparse=False)
def main() -> None:
    parser = NgArgumentParser()
    parser.add_argument(
        "--name1", dest="name", type=str, default="default", help="Name field 1", required=True
    )
    parser.add_argument("--name2", dest="name", type=str, help="Name field 2", required=True)
    parser.parse_args()


if __name__ == "__main__":
    main()
