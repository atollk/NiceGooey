import time

import pytest
from nicegui.testing import Screen
from selenium.webdriver.common.by import By

from nicegooey.argparse import NgArgumentParser, nice_gooey_argparse_main


@pytest.mark.nicegui_main_file(__file__)
async def test_submit(screen: Screen) -> None:
    """Test that pressing the Submit button opens an xterm and executes the code."""

    screen.open("/")

    screen.should_contain("name")

    # Get the Selenium driver
    driver = screen.selenium

    # Find the input field and fill it
    inputs = driver.find_elements(By.TAG_NAME, "input")
    text_inputs = [inp for inp in inputs if inp.get_attribute("type") in ("text", None)]
    assert len(text_inputs) >= 1, f"Expected at least 1 text input, found {len(text_inputs)}"

    name_input = text_inputs[0]
    name_input.send_keys("Alice")

    # Find and click the Submit button
    buttons = driver.find_elements(By.TAG_NAME, "button")
    submit_button = [btn for btn in buttons if "submit" in btn.text.lower()][0]
    submit_button.click()

    # Verify that the terminal (xterm) opened
    # The xterm should appear in the page after submission
    xterms = []
    for _ in range(20):
        xterms = driver.find_elements(By.CLASS_NAME, "xterm")
        if xterms:
            break
        time.sleep(0.1)
    assert xterms != [], "xterm should be visible"

    # Verify the output contains "Hello, Alice"
    page_text = ""
    for _ in range(20):
        page_text = driver.find_element(By.TAG_NAME, "body").text
        if "Hello, Alice" in page_text:
            break
        time.sleep(0.1)
    assert "Hello, Alice" in page_text


@nice_gooey_argparse_main(patch_argparse=False)
def main() -> None:
    parser = NgArgumentParser()
    parser.add_argument("--name", type=str, help="Your name", required=True)
    args = parser.parse_args()

    try:
        print(f"Hello, {args.name}")
    except AttributeError:
        # In tests, `ui.run` doesn't block, so we have to ignore this error.
        pass


if __name__ == "__main__":
    main()
