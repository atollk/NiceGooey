import logging
import sys

import nicegui
import pytest
from nicegui import ui
from nicegui.testing import User

import nicegooey.argparse.main
from nicegooey.argparse import NgArgumentParser, NiceGooeyConfig, nice_gooey_argparse_main

pytestmark = pytest.mark.skipif(
    sys.platform == "win32", reason="https://github.com/zauberzeug/nicegui/issues/5949"
)


@pytest.mark.nicegui_main_file(__file__)
async def test_number_precision_on_non_numeric_raises(user: User, caplog: pytest.LogCaptureFixture) -> None:
    """Test that setting number_precision on a str action raises TypeError during render."""
    # Necessary so that the captured exception won't fail the test.
    caplog.set_level(logging.CRITICAL, logger="nicegui")

    assert len(nicegui.app.storage.general["exceptions"]) == 0
    await user.open("/")
    assert len(nicegui.app.storage.general["exceptions"]) == 1


@nice_gooey_argparse_main(patch_argparse=False)
def main() -> None:
    parser = NgArgumentParser()
    name_action = parser.add_argument("--name", type=str, help="A name", required=True)
    name_action.nicegooey_config = NiceGooeyConfig.ActionConfig(number_precision=2)
    parser.parse_args()


def prep() -> None:
    def patched_root():
        ui.on_exception(lambda e: nicegui.app.storage.general["exceptions"].append(str(e)))
        original_root()

    nicegui.app.storage.general["exceptions"] = []
    original_root = nicegooey.argparse.main.main_instance._ui_root
    nicegooey.argparse.main.main_instance._ui_root = patched_root


if __name__ == "__main__":
    prep()
    main()
