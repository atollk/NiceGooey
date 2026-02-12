import pytest
from nicegui import ui
from nicegui.testing import User

from nicegooey.argparse import nice_gooey_argparse_main, NgArgumentParser
from nicegooey.argparse.main import main_instance


@pytest.mark.nicegui_main_file(__file__)
async def test_nargs_question_mark(user: User) -> None:
    """Test nargs='?' - zero or one value (optional single value)."""

    await user.open("/")

    await user.should_see("optional")

    assert main_instance.namespace.optional == "DEFAULT"

    input_field = user.find(ui.input)
    input_field.type("custom-value")

    assert main_instance.namespace.optional == "custom-value"

    input_field.clear()


@nice_gooey_argparse_main(patch_argparse=False)
def main():
    parser = NgArgumentParser()
    parser.add_argument(
        "--optional", nargs="?", type=str, const="CONST", default="DEFAULT", help="Optional value"
    )
    parser.parse_args()


if __name__ == "__main__":
    main()
