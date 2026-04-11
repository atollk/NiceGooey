import pytest
from nicegui.testing import User

from nicegooey.argparse import NgArgumentParser, NiceGooeyConfig, nice_gooey_argparse_main


@pytest.mark.nicegui_main_file(__file__)
async def test_ng_action_wrapper_set_nicegooey_config(user: User) -> None:
    """Test that wrapper.set_nicegooey_config() has the same effect as direct property assignment."""

    await user.open("/")

    # The custom display name must be visible
    await user.should_see("My Output")

    # The raw dest should NOT appear as a label
    with pytest.raises(AssertionError):
        user.find(content="output")


@nice_gooey_argparse_main(patch_argparse=False)
def main() -> None:
    parser = NgArgumentParser()
    wrapper = parser.add_argument("--output", type=str, help="Output path", required=True)
    # Set config via helper method
    wrapper.set_nicegooey_config(NiceGooeyConfig.ActionConfig(display_name="My Output"))
    parser.parse_args()


if __name__ == "__main__":
    main()
