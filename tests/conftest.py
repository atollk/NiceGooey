import pytest
from nicegui.testing import UserInteraction


@pytest.fixture(autouse=True)
def reset_nicegooey_main():
    """Fixture to reset the main_instance before each test."""
    from nicegooey.argparse.main import main_instance

    main_instance.reset()
    yield


def input_number(interaction: UserInteraction, n: str | int) -> None:
    # Required until nicegui 3.8 is released and interaction.type becomes available.
    from nicegui.ui import number

    for element in interaction.elements:
        assert isinstance(element, number)
        element.value = n
