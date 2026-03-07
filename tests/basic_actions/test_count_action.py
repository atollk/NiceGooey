import pytest
from nicegui import ui
from nicegui.testing import User

from nicegooey.argparse import nice_gooey_argparse_main, NgArgumentParser
from nicegooey.argparse.main import main_instance


@pytest.mark.nicegui_main_file(__file__)
async def test_count_action(user: User) -> None:
    """Test count action (increments a counter)."""

    await user.open("/")
    await user.should_see("verbose")

    assert main_instance.namespace.verbose == 0

    number_input = user.find(ui.number)
    number_input.type(3)

    assert main_instance.namespace.verbose == 3


@nice_gooey_argparse_main(patch_argparse=False)
def main():
    parser = NgArgumentParser()
    parser.add_argument("--verbose", "-v", action="count", default=0, help="Verbosity level", required=True)
    parser.parse_args()


if __name__ == "__main__":
    main()
