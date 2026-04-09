import pytest
from nicegui import ui, ElementFilter
from nicegui.testing import User

from nicegooey.argparse import NgArgumentParser, nice_gooey_argparse_main


@pytest.mark.nicegui_main_file(__file__)
async def test_action_card_class(user: User) -> None:
    """Test that action_card_class is applied to the ui.item wrapping each action."""

    await user.open("/")
    await user.should_see("name")

    with user:
        items = list(ElementFilter(kind=ui.item))
    assert any("test-custom-class" in (el.classes or set()) for el in items), (
        "Expected at least one ui.item with class 'test-custom-class'"
    )


@nice_gooey_argparse_main(patch_argparse=False)
def main() -> None:
    parser = NgArgumentParser()
    parser.nicegooey_config.action_card_class = "test-custom-class"
    parser.add_argument("--name", type=str, help="Your name", required=True)
    parser.parse_args()


if __name__ == "__main__":
    main()
