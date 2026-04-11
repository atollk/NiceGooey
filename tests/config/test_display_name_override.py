import pytest
from nicegui.testing import User

from nicegooey.argparse import NgArgumentParser, NiceGooeyConfig, nice_gooey_argparse_main


@pytest.mark.nicegui_main_file(__file__)
async def test_display_name_override(user: User) -> None:
    """Test that ActionConfig.display_name overrides the label rendered for an action."""

    await user.open("/")

    # Custom display name is shown
    await user.should_see("Output File")

    # The raw dest/option-string is NOT shown as a label
    with pytest.raises(AssertionError):
        user.find(content="output-file")


@nice_gooey_argparse_main(patch_argparse=False)
def main() -> None:
    parser = NgArgumentParser()
    output_action = parser.add_argument("--output-file", type=str, help="Path to output file", required=True)
    output_action.nicegooey_config = NiceGooeyConfig.ActionConfig(display_name="Output File")
    parser.parse_args()


if __name__ == "__main__":
    main()
