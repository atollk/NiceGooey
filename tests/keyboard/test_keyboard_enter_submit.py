import pytest
from nicegui.testing import Screen
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

from nicegooey.argparse import NgArgumentParser, nice_gooey_argparse_main


@pytest.mark.nicegui_main_file(__file__)
async def test_keyboard_enter_submit(screen: Screen) -> None:
    """Test that pressing Enter key submits the form."""

    screen.open("/")

    # Wait for page to load
    screen.should_contain("name")

    # Get the Selenium driver
    driver = screen.selenium

    # Find the input field
    inputs = driver.find_elements(By.TAG_NAME, "input")
    text_inputs = [inp for inp in inputs if inp.get_attribute("type") in ("text", None)]
    assert len(text_inputs) >= 1, f"Expected at least 1 text input, found {len(text_inputs)}"

    name_input = text_inputs[0]

    # Type a value
    name_input.send_keys("Alice")

    # Press Enter to submit the form
    name_input.send_keys(Keys.ENTER)

    # Verify that the terminal (xterm) opened
    # The xterm should appear in the page after submission
    assert driver.find_elements(By.CLASS_NAME, "xterm") != []


@nice_gooey_argparse_main(patch_argparse=False)
def main() -> None:
    parser = NgArgumentParser()
    parser.add_argument("--name", type=str, help="Your name", required=True)

    parser.parse_args()


if __name__ == "__main__":
    main()
