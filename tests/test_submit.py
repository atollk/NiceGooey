import os

import pytest
from nicegui import ui
from nicegui.testing import User

from nicegooey.argparse import NgArgumentParser, nice_gooey_argparse_main


@pytest.mark.nicegui_main_file(__file__)
async def test_submit(user: User) -> None:
    """Test that pressing the Submit button opens an xterm and executes the code."""

    await user.open("/")

    await user.should_see("name")

    # Find the input field and fill it
    name_input = user.find(ui.input)
    name_input.type("Alice")

    # Find and click the Submit button
    submit_button = user.find("Submit")
    submit_button.click()

    # Verify that the terminal (xterm) opened
    await user.should_see(kind=ui.xterm)
    assert user.should_see(content="Hello, Alice")


@nice_gooey_argparse_main(patch_argparse=False)
def main():
    parser = NgArgumentParser()
    parser.add_argument("--name", type=str, help="Your name", required=True)
    args = parser.parse_args()

    if not os.environ["PYTEST_CURRENT_TEST"].endswith("(setup)"):
        # In tests, `ui.run` doesn't block, so we have to manually skip this code during test setup.
        print(f"Hello, {args.name}")


if __name__ == "__main__":
    main()
