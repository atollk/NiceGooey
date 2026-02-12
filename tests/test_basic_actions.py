"""Tests for basic action types in NiceGooey."""

import pytest
from nicegui import ui
from nicegui.testing import User

from nicegooey.argparse import nice_gooey_argparse_main, NgArgumentParser
from nicegooey.argparse.main import main_instance


@pytest.mark.nicegui_main_file(__file__)
async def test_string_action(user: User) -> None:
    """Test a basic string action with input field."""

    @nice_gooey_argparse_main(patch_argparse=False)
    def main():
        parser = NgArgumentParser()
        parser.add_argument("--name", type=str, help="Your name")
        parser.parse_args()

    await user.open("/")
    await user.should_see("name")

    # Find the input field and type a value
    input_field = user.find(ui.input)
    input_field.type("Alice")

    # Verify the namespace value
    assert main_instance.namespace.name == "Alice"


@pytest.mark.nicegui_main_file(__file__)
async def test_int_action(user: User) -> None:
    """Test integer action with number input."""

    @nice_gooey_argparse_main(patch_argparse=False)
    def main():
        parser = NgArgumentParser()
        parser.add_argument("--age", type=int, help="Your age")
        parser.parse_args()

    await user.open("/")
    await user.should_see("age")

    # Find the number input and set a value
    number_input = user.find(ui.number)
    number_input.type("42")

    # Verify the namespace value
    assert main_instance.namespace.age == 42


@pytest.mark.nicegui_main_file(__file__)
async def test_float_action(user: User) -> None:
    """Test float action with number input."""

    @nice_gooey_argparse_main(patch_argparse=False)
    def main():
        parser = NgArgumentParser()
        parser.add_argument("--price", type=float, help="Price")
        parser.parse_args()

    await user.open("/")
    await user.should_see("price")

    # Find the number input and set a value
    number_input = user.find(ui.number)
    number_input.type("19.99")

    # Verify the namespace value
    assert main_instance.namespace.price == 19.99


@pytest.mark.nicegui_main_file(__file__)
async def test_string_action_with_choices(user: User) -> None:
    """Test string action with choices renders as select dropdown."""

    @nice_gooey_argparse_main(patch_argparse=False)
    def main():
        parser = NgArgumentParser()
        parser.add_argument("--fruit", choices=["apple", "banana", "orange"], help="Pick a fruit")
        parser.parse_args()

    await user.open("/")
    await user.should_see("fruit")

    # Find the select dropdown
    select = user.find(ui.select)

    # Select an option
    select.click()
    await user.should_see("banana")
    # Click the banana option
    user.find("banana").click()

    # Verify the namespace value
    assert main_instance.namespace.fruit == "banana"


@pytest.mark.nicegui_main_file(__file__)
async def test_action_with_type_validation(user: User) -> None:
    """Test action with custom type function that can fail."""

    def validate_min_length(value: str) -> str:
        """Custom validator that requires at least 3 characters."""
        if len(value) < 3:
            raise ValueError("Must be at least 3 characters")
        return value

    @nice_gooey_argparse_main(patch_argparse=False)
    def main():
        parser = NgArgumentParser()
        parser.add_argument("--username", type=validate_min_length, help="Username (min 3 chars)")
        parser.parse_args()

    await user.open("/")
    await user.should_see("username")

    # Find the input field
    input_field = user.find(ui.input)

    # Try with invalid value (too short)
    input_field.type("ab")
    # Validation happens on submit or validate() call

    # Type a valid value
    input_field.clear()
    input_field.type("alice")

    # Verify the namespace value
    assert main_instance.namespace.username == "alice"


@pytest.mark.nicegui_main_file(__file__)
async def test_store_const_action(user: User) -> None:
    """Test store_const action with checkbox."""

    @nice_gooey_argparse_main(patch_argparse=False)
    def main():
        parser = NgArgumentParser()
        parser.add_argument(
            "--verbose", action="store_const", const="VERBOSE", default="NORMAL", help="Enable verbose mode"
        )
        parser.parse_args()

    await user.open("/")
    await user.should_see("verbose")

    # Initially should be default value
    assert main_instance.namespace.verbose == "NORMAL"

    # Find checkbox and click it
    checkbox = user.find(ui.checkbox)
    checkbox.click()

    # Should now have the const value
    assert main_instance.namespace.verbose == "VERBOSE"

    # Click again to uncheck
    checkbox.click()

    # Should revert to default
    assert main_instance.namespace.verbose == "NORMAL"


@pytest.mark.nicegui_main_file(__file__)
async def test_store_true_action(user: User) -> None:
    """Test store_true action (checkbox that stores True)."""

    @nice_gooey_argparse_main(patch_argparse=False)
    def main():
        parser = NgArgumentParser()
        parser.add_argument("--enable", action="store_true", help="Enable feature")
        parser.parse_args()

    await user.open("/")
    await user.should_see("enable")

    # Initially should be False
    assert main_instance.namespace.enable is False

    # Find checkbox and click it
    checkbox = user.find(ui.checkbox)
    checkbox.click()

    # Should now be True
    assert main_instance.namespace.enable is True


@pytest.mark.nicegui_main_file(__file__)
async def test_store_false_action(user: User) -> None:
    """Test store_false action (checkbox that stores False when checked)."""

    @nice_gooey_argparse_main(patch_argparse=False)
    def main():
        parser = NgArgumentParser()
        parser.add_argument("--no-cache", action="store_false", dest="cache", help="Disable cache")
        parser.parse_args()

    await user.open("/")
    await user.should_see("cache")

    # Initially should be True (store_false default)
    assert main_instance.namespace.cache is True

    # Find checkbox and click it
    checkbox = user.find(ui.checkbox)
    checkbox.click()

    # Should now be False
    assert main_instance.namespace.cache is False


@pytest.mark.nicegui_main_file(__file__)
async def test_count_action(user: User) -> None:
    """Test count action (increments a counter)."""

    @nice_gooey_argparse_main(patch_argparse=False)
    def main():
        parser = NgArgumentParser()
        parser.add_argument("--verbose", "-v", action="count", default=0, help="Verbosity level")
        parser.parse_args()

    await user.open("/")
    await user.should_see("verbose")

    # Initially should be 0
    assert main_instance.namespace.verbose == 0

    # Find the number input and change value
    number_input = user.find(ui.number)
    number_input.type("3")

    # Should now be 3
    assert main_instance.namespace.verbose == 3


@pytest.mark.nicegui_main_file(__file__)
async def test_append_const_action(user: User) -> None:
    """Test append_const action (button to append constant values)."""

    @nice_gooey_argparse_main(patch_argparse=False)
    def main():
        parser = NgArgumentParser()
        parser.add_argument("--add-flag", action="append_const", const="FLAG", dest="flags", help="Add flag")
        parser.parse_args()

    await user.open("/")
    await user.should_see("flags")

    # Initially should be empty list
    assert main_instance.namespace.flags == []

    # Find the add button
    add_button = user.find(ui.button).filter(
        lambda x: x.element.props.get("data-testid") == "ng-action-add-button"
    )

    # Click to add first flag
    add_button.click()
    assert main_instance.namespace.flags == ["FLAG"]

    # Click to add second flag
    add_button.click()
    assert main_instance.namespace.flags == ["FLAG", "FLAG"]

    # Click to add third flag
    add_button.click()
    assert main_instance.namespace.flags == ["FLAG", "FLAG", "FLAG"]


@pytest.mark.nicegui_main_file(__file__)
async def test_append_action_with_str(user: User) -> None:
    """Test append action with string type."""

    @nice_gooey_argparse_main(patch_argparse=False)
    def main():
        parser = NgArgumentParser()
        parser.add_argument("--tag", action="append", type=str, dest="tags", help="Add tags")
        parser.parse_args()

    await user.open("/")
    await user.should_see("tags")

    # Initially should be empty list
    assert main_instance.namespace.tags == []

    # Find the input field for adding values
    input_field = user.find(ui.input).filter(
        lambda x: x.element.props.get("data-testid") == "ng-action-type-input"
    )
    add_button = user.find(ui.button).filter(
        lambda x: x.element.props.get("data-testid") == "ng-action-add-button"
    )

    # Add first tag
    input_field.type("python")
    add_button.click()
    assert main_instance.namespace.tags == ["python"]

    # Add second tag
    input_field.type("testing")
    add_button.click()
    assert main_instance.namespace.tags == ["python", "testing"]

    # Add third tag
    input_field.type("nicegui")
    add_button.click()
    assert main_instance.namespace.tags == ["python", "testing", "nicegui"]


@pytest.mark.nicegui_main_file(__file__)
async def test_append_action_with_int(user: User) -> None:
    """Test append action with int type."""

    @nice_gooey_argparse_main(patch_argparse=False)
    def main():
        parser = NgArgumentParser()
        parser.add_argument("--number", action="append", type=int, dest="numbers", help="Add numbers")
        parser.parse_args()

    await user.open("/")
    await user.should_see("numbers")

    # Initially should be empty list
    assert main_instance.namespace.numbers == []

    # Find the number input for adding values
    number_input = user.find(ui.number)
    add_button = user.find(ui.button).filter(
        lambda x: x.element.props.get("data-testid") == "ng-action-add-button"
    )

    # Add first number
    number_input.type("42")
    add_button.click()
    assert main_instance.namespace.numbers == [42]

    # Add second number
    number_input.type("100")
    add_button.click()
    assert main_instance.namespace.numbers == [42, 100]

    # Add third number
    number_input.type("7")
    add_button.click()
    assert main_instance.namespace.numbers == [42, 100, 7]


@pytest.mark.nicegui_main_file(__file__)
async def test_extend_action(user: User) -> None:
    """Test extend action (similar UI to append)."""

    @nice_gooey_argparse_main(patch_argparse=False)
    def main():
        parser = NgArgumentParser()
        parser.add_argument("--item", action="extend", nargs="+", type=str, dest="items", help="Extend items")
        parser.parse_args()

    await user.open("/")
    await user.should_see("items")

    # Initially should be empty list
    assert main_instance.namespace.items == []

    # Find the input field for adding values
    input_field = user.find(ui.input).filter(
        lambda x: x.element.props.get("data-testid") == "ng-action-type-input"
    )
    add_button = user.find(ui.button).filter(
        lambda x: x.element.props.get("data-testid") == "ng-action-add-button"
    )

    # Add first item
    input_field.type("apple")
    add_button.click()
    assert main_instance.namespace.items == ["apple"]

    # Add second item
    input_field.type("banana")
    add_button.click()
    assert main_instance.namespace.items == ["apple", "banana"]
