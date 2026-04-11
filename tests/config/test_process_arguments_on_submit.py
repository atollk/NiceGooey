import asyncio
import sys

import pytest
from nicegui import app
from nicegui.testing import User
from nicegooey.argparse import NgArgumentParser, nice_gooey_argparse_main

pytestmark = pytest.mark.skipif(
    sys.platform == "win32", reason="https://github.com/zauberzeug/nicegui/issues/5949"
)


@pytest.mark.nicegui_main_file(__file__)
async def test_process_arguments_on_submit(user: User) -> None:
    """Test that a custom synchronous process_arguments_on_submit callable is invoked on submit."""

    app.storage.general["custom_submit_called"] = False

    await user.open("/")
    await user.should_see("name")

    user.find("Submit").click()
    await asyncio.sleep(0.1)

    assert app.storage.general.get("custom_submit_called", False), (
        "Custom process_arguments_on_submit was not called"
    )


@nice_gooey_argparse_main(patch_argparse=False)
def main() -> None:
    def custom_submit(main_func):
        app.storage.general["custom_submit_called"] = True

    parser = NgArgumentParser()
    parser.nicegooey_config.process_arguments_on_submit = custom_submit
    parser.add_argument("--name", type=str, help="Your name", required=True, default="Alice")
    parser.parse_args()


if __name__ == "__main__":
    main()
