import pytest
from nicegui import ui
from nicegui.testing import User

from nicegooey.argparse import NgArgumentParser, nice_gooey_argparse_main
from nicegooey.argparse.main import main_instance


@pytest.mark.nicegui_main_file(__file__)
async def test_string_and_int_same_dest(user: User) -> None:
    """Test one string and one int action with the same dest - verify two-way binding."""

    await user.open("/")

    await user.should_see("value")

    assert main_instance.namespace.value in ("", 0)

    inputs = user.find(ui.input)
    inputs.type("42")

    assert main_instance.namespace.value in ("42", 42)


@nice_gooey_argparse_main(patch_argparse=False)
def main():
    parser = NgArgumentParser()
    parser.add_argument("--value-str", dest="value", type=str, help="Value as string")
    parser.add_argument("--value-int", dest="value", type=int, help="Value as int")
    parser.parse_args()


if __name__ == "__main__":
    main()
