import asyncio

import pytest
from nicegui import ui, ElementFilter
from nicegui.testing import User

from nicegooey.argparse import NgArgumentParser, nice_gooey_argparse_main


@pytest.mark.nicegui_main_file(__file__)
async def test_submit_exception(user: User) -> None:
    """Test that an exception in main_func opens the xterm dialog and enables the Close button (no freeze)."""

    await user.open("/")
    await user.should_see("name")

    user.find("Submit").click()

    # The xterm dialog should open despite the exception
    await user.should_see(kind=ui.xterm)

    # The Close button should become enabled after the exception is handled (not frozen)
    for _ in range(30):
        with user:
            close_buttons = [
                el
                for el in ElementFilter(kind=ui.button, content="Close")
                if not el.props.get("disabled", False)
            ]
        if close_buttons:
            break
        await asyncio.sleep(0.1)
    assert close_buttons, "Close button should be enabled after exception is handled"


@nice_gooey_argparse_main(patch_argparse=False)
def main() -> None:
    parser = NgArgumentParser()
    parser.add_argument("--name", type=str, help="Your name", required=True, default="Alice")
    parser.parse_args()

    raise RuntimeError("test error — intentional exception")


if __name__ == "__main__":
    main()
