import pytest
from nicegui import ui
from nicegui.testing import User

from nicegooey.argparse import NgArgumentParser, NiceGooeyConfig, nice_gooey_argparse_main
from tests.conftest import find_within, exactly_one


@pytest.mark.nicegui_main_file(__file__)
async def test_number_precision_float(user: User) -> None:
    """Test that number_precision=2 on a float action sets precision=2 on the rendered ui.number."""

    await user.open("/")
    await user.should_see("ratio")

    number_el = exactly_one(find_within(user, kind=ui.number, within_marker="ng-action-ratio").elements)
    # TODO: set value of number_el, then un-focus from it (aka trigger blur event) and check that the precision is correct


@nice_gooey_argparse_main(patch_argparse=False)
def main() -> None:
    parser = NgArgumentParser()
    ratio_action = parser.add_argument("--ratio", type=float, help="A ratio", required=True)
    ratio_action.nicegooey_config = NiceGooeyConfig.ActionConfig(number_precision=2)
    parser.parse_args()


if __name__ == "__main__":
    main()
