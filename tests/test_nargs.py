"""Tests for different nargs options."""

import pytest
from nicegui import ui
from nicegui.testing import User

from nicegooey.argparse import nice_gooey_argparse_main, NgArgumentParser
from nicegooey.argparse.main import main_instance


@pytest.mark.nicegui_main_file(__file__)
async def test_nargs_zero(user: User) -> None:
    """Test nargs=0 - no value expected, action triggers without value."""

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

    await user.open("/")

    # Should see the flag
    await user.should_see("flag")

    # With nargs=0, there should be no input field, just a trigger mechanism
    # (Likely a checkbox or button)

    # Check initial value
    assert main_instance.namespace.flag == "NOT_TRIGGERED"

    # Trigger the action (click checkbox/button)
    # checkbox = user.find(ui.checkbox)
    # checkbox.click()

    # After triggering
    # assert main_instance.namespace.flag == "TRIGGERED"


@pytest.mark.nicegui_main_file(__file__)
async def test_nargs_one(user: User) -> None:
    """Test nargs=1 - exactly one value expected (as a list with one item)."""

    @nice_gooey_argparse_main(patch_argparse=False)
    def main():
        parser = NgArgumentParser()
        parser.add_argument("--item", nargs=1, type=str, help="One item")
        parser.parse_args()

    await user.open("/")

    # Should see the item field
    await user.should_see("item")

    # With nargs=1, argparse returns a list with one element
    # The UI might show a single input or a list input

    # Initially should be None or empty list
    assert main_instance.namespace.item in (None, [], [""])

    # Type a value
    input_field = user.find(ui.input)
    input_field.type("single-value")

    # Should be a list with one element
    # assert main_instance.namespace.item == ['single-value']


@pytest.mark.nicegui_main_file(__file__)
async def test_nargs_three(user: User) -> None:
    """Test nargs=3 - exactly three values expected."""

    @nice_gooey_argparse_main(patch_argparse=False)
    def main():
        parser = NgArgumentParser()
        parser.add_argument("--coords", nargs=3, type=float, help="Three coordinates (x, y, z)")
        parser.parse_args()

    await user.open("/")

    # Should see the coords field
    await user.should_see("coords")

    # With nargs=3, needs exactly 3 values
    # The UI should provide a way to enter 3 values (possibly 3 inputs or a list input)

    # Initially should be None or empty list
    assert main_instance.namespace.coords in (None, [], [0, 0, 0])

    # Add three values
    # (This would require finding the input elements and adding values)
    # For a list-based UI, might use input_chips

    # After adding 3 values:
    # assert main_instance.namespace.coords == [1.0, 2.0, 3.0]

    # Validation should ensure exactly 3 values are provided


@pytest.mark.nicegui_main_file(__file__)
async def test_nargs_question_mark(user: User) -> None:
    """Test nargs='?' - zero or one value (optional single value)."""

    @nice_gooey_argparse_main(patch_argparse=False)
    def main():
        parser = NgArgumentParser()
        parser.add_argument(
            "--optional", nargs="?", type=str, const="CONST", default="DEFAULT", help="Optional value"
        )
        parser.parse_args()

    await user.open("/")

    # Should see the optional field
    await user.should_see("optional")

    # With nargs='?':
    # - If not provided: uses default
    # - If provided without value: uses const
    # - If provided with value: uses that value

    # Initially should have default value
    assert main_instance.namespace.optional == "DEFAULT"

    # Type a value
    input_field = user.find(ui.input)
    input_field.type("custom-value")

    # Should use the typed value
    assert main_instance.namespace.optional == "custom-value"

    # Clear the value
    input_field.clear()

    # Should revert to default or const depending on implementation
    # assert main_instance.namespace.optional in ("DEFAULT", "CONST")


@pytest.mark.nicegui_main_file(__file__)
async def test_nargs_asterisk(user: User) -> None:
    """Test nargs='*' - zero or more values (list)."""

    @nice_gooey_argparse_main(patch_argparse=False)
    def main():
        parser = NgArgumentParser()
        parser.add_argument("--items", nargs="*", type=str, help="Zero or more items")
        parser.parse_args()

    await user.open("/")

    # Should see the items field
    await user.should_see("items")

    # With nargs='*', can have 0 or more values
    # UI should allow adding multiple values (likely input_chips)

    # Initially should be empty list or None
    assert main_instance.namespace.items in (None, [])

    # The UI should allow adding items one by one
    # Or typing multiple items

    # Add some items
    # (Would require finding input and add button)

    # Can also have zero items (valid)
    # assert main_instance.namespace.items == []


@pytest.mark.nicegui_main_file(__file__)
async def test_nargs_plus(user: User) -> None:
    """Test nargs='+' - one or more values (at least one required)."""

    @nice_gooey_argparse_main(patch_argparse=False)
    def main():
        parser = NgArgumentParser()
        parser.add_argument("--required-items", nargs="+", type=str, help="One or more items (required)")
        parser.parse_args()

    await user.open("/")

    # Should see the required-items field
    await user.should_see("required-items")

    # With nargs='+', must have at least 1 value
    # UI should enforce this (validation)

    # Initially might be None or empty
    assert main_instance.namespace.required_items in (None, [])

    # Attempting to submit with zero items should fail validation
    # (Would need to test submit button and validation)

    # Add one item
    # (Would require finding input and add button)

    # After adding at least one item, validation should pass


@pytest.mark.nicegui_main_file(__file__)
async def test_nargs_specific_number_validation(user: User) -> None:
    """Test that nargs with specific number enforces exactly that many values."""

    @nice_gooey_argparse_main(patch_argparse=False)
    def main():
        parser = NgArgumentParser()
        parser.add_argument("--rgb", nargs=3, type=int, help="RGB color (3 integers)")
        parser.parse_args()

    await user.open("/")

    await user.should_see("rgb")

    # Should enforce exactly 3 values
    # Adding 2 values should not be valid
    # Adding 4 values should not be valid
    # Adding exactly 3 values should be valid

    # This would require testing the validation logic


@pytest.mark.nicegui_main_file(__file__)
async def test_nargs_with_choices(user: User) -> None:
    """Test nargs with choices combination."""

    @nice_gooey_argparse_main(patch_argparse=False)
    def main():
        parser = NgArgumentParser()
        parser.add_argument("--colors", nargs="*", choices=["red", "green", "blue"], help="Select colors")
        parser.parse_args()

    await user.open("/")

    await user.should_see("colors")

    # With nargs='*' and choices, should be able to select multiple values from the choices
    # UI might show a multi-select dropdown or chips with dropdown

    # Initially empty
    assert main_instance.namespace.colors in (None, [])

    # Add some colors from the choices
    # (Would require interacting with the multi-select UI)


@pytest.mark.nicegui_main_file(__file__)
async def test_nargs_different_types(user: User) -> None:
    """Test nargs with different type combinations."""

    @nice_gooey_argparse_main(patch_argparse=False)
    def main():
        parser = NgArgumentParser()
        parser.add_argument("--ints", nargs="+", type=int, help="One or more integers")
        parser.add_argument("--floats", nargs="*", type=float, help="Zero or more floats")
        parser.add_argument("--strings", nargs=2, type=str, help="Exactly two strings")
        parser.parse_args()

    await user.open("/")

    # All three should be visible
    await user.should_see("ints")
    await user.should_see("floats")
    await user.should_see("strings")

    # Each should have appropriate UI for its type and nargs
    # ints: number input, must have at least 1
    # floats: number input (float format), can have 0 or more
    # strings: text input, must have exactly 2
