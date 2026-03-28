import pytest
from nicegui.testing import Screen
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

from nicegooey.argparse import NgArgumentParser, nice_gooey_argparse_main


@pytest.mark.nicegui_main_file(__file__)
async def test_keyboard_tab_navigation(screen: Screen) -> None:
    """Test that tab key navigates between input fields."""
    screen.open("/")

    # Wait for page to load
    screen.should_contain("name")
    screen.should_contain("email")
    screen.should_contain("age")

    # Get the Selenium driver
    driver = screen.selenium

    # Find all input elements on the page (we have 3: name, email, age)
    # They should be in order
    inputs = driver.find_elements(By.TAG_NAME, "input")

    # Filter to get text/number inputs (exclude checkboxes, etc.)
    text_inputs = [inp for inp in inputs if inp.get_attribute("type") in ("text", "number", None)]

    assert len(text_inputs) >= 3, f"Expected at least 3 text inputs, found {len(text_inputs)}"

    name_input = text_inputs[0]
    email_input = text_inputs[1]
    age_input = text_inputs[2]

    # Click on the name input to focus it
    name_input.click()
    assert driver.switch_to.active_element == name_input

    # Press Tab to navigate to email input
    name_input.send_keys(Keys.TAB)
    assert driver.switch_to.active_element == email_input

    # Press Tab to navigate to age input
    email_input.send_keys(Keys.TAB)
    assert driver.switch_to.active_element == age_input

    # Press Shift+Tab to navigate back to email input
    age_input.send_keys(Keys.SHIFT, Keys.TAB)
    assert driver.switch_to.active_element == email_input


@nice_gooey_argparse_main(patch_argparse=False)
def main() -> None:
    parser = NgArgumentParser()
    parser.add_argument("--name", type=str, help="Your name", required=True)
    parser.add_argument("--email", type=str, help="Your email", required=True)
    parser.add_argument("--age", type=int, help="Your age", required=True)
    parser.parse_args()


if __name__ == "__main__":
    main()
