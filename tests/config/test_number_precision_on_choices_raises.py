import pytest
from nicegui.testing import User

from nicegooey.argparse import NgArgumentParser, NiceGooeyConfig, nice_gooey_argparse_main


@pytest.mark.nicegui_main_file(__file__)
async def test_number_precision_on_choices_raises(user: User) -> None:
    """Test that setting number_precision on a choices action raises TypeError during render."""

    with pytest.raises(TypeError, match="number_precision"):
        await user.open("/")


@nice_gooey_argparse_main(patch_argparse=False)
def main() -> None:
    parser = NgArgumentParser()
    fruit_action = parser.add_argument("--fruit", choices=["apple", "banana"], help="Pick a fruit")
    fruit_action.nicegooey_config = NiceGooeyConfig.ActionConfig(number_precision=1)
    parser.parse_args()


if __name__ == "__main__":
    main()
