import pytest
from nicegui.testing import User

from nicegooey.argparse import nice_gooey_argparse_main, NgArgumentParser
from nicegooey.argparse.main import main_instance


@pytest.mark.nicegui_main_file(__file__)
async def test_nargs_zero(user: User) -> None:
    """Test nargs=0 - no value expected, action triggers without value."""

    await user.open("/")

    await user.should_see("flag")

    assert main_instance.namespace.flag == "NOT_TRIGGERED"


@nice_gooey_argparse_main(patch_argparse=False)
def main():
    parser = NgArgumentParser()
    parser.add_argument(
        "--flag",
        nargs=0,
        action="store_const",
        const="TRIGGERED",
        default="NOT_TRIGGERED",
        help="Flag with no args",
    )
    parser.parse_args()


if __name__ == "__main__":
    main()
