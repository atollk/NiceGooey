import pytest


@pytest.fixture(autouse=True)
def reset_nicegooey_main():
    """Fixture to reset the main_instance before each test."""
    from nicegooey.argparse.main import main_instance

    main_instance.reset()
    yield
