import pytest
from nicegui import ui
from nicegui.testing import User

from nicegooey.argparse import NgArgumentParser, NiceGooeyConfig, nice_gooey_argparse_main
from tests.conftest import find_within, exactly_one


@pytest.mark.nicegui_main_file(__file__)
async def test_number_precision_int(user: User) -> None:
    """Test that number_precision=0 on an int action sets precision=0 on the rendered ui.number."""

    await user.open("/")
    await user.should_see("count")

    input_el = find_within(user, kind=ui.number, within_marker="ng-action-count")
    input_el.type("5.4")
    input_el.trigger("blur")
    assert exactly_one(input_el.elements).value == 5


@nice_gooey_argparse_main(patch_argparse=False)
def main() -> None:
    parser = NgArgumentParser()
    count_action = parser.add_argument("--count", type=int, help="Item count", required=True)
    count_action.nicegooey_config = NiceGooeyConfig.ActionConfig(number_precision=0)
    parser.parse_args()


if __name__ == "__main__":
    main()
