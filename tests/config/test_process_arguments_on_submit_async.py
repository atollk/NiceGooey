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
async def test_process_arguments_on_submit_async(user: User) -> None:
    """Test that a custom async process_arguments_on_submit callable is awaited on submit."""

    app.storage.general["async_submit_called"] = False

    await user.open("/")
    await user.should_see("name")

    user.find("Submit").click()
    await asyncio.sleep(0.1)

    assert app.storage.general.get("async_submit_called", False), (
        "Custom async process_arguments_on_submit was not awaited"
    )


@nice_gooey_argparse_main(patch_argparse=False)
def main() -> None:
    async def custom_submit_async(main_func):
        app.storage.general["async_submit_called"] = True

    parser = NgArgumentParser()
    parser.nicegooey_config.process_arguments_on_submit = custom_submit_async
    parser.add_argument("--name", type=str, help="Your name", required=True, default="Alice")
    parser.parse_args()


if __name__ == "__main__":
    main()
