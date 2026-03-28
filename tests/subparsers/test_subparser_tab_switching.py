import pytest
from nicegui.testing import User

from nicegooey.argparse import NgArgumentParser, nice_gooey_argparse_main
from nicegooey.argparse.main import main_instance
from nicegooey.argparse.ui_classes.groupings.subparser_ui import SubparserUi


@pytest.mark.nicegui_main_file(__file__)
async def test_subparser_tab_switching(user: User) -> None:
    """Test switching between subparser tabs and verifying correct content."""

    await user.open("/")

    await user.should_see("build")
    await user.should_see("test")
    await user.should_see("deploy")

    # Click "build" tab and verify its content
    build_tab = user.find(marker=f"{SubparserUi.TAB_MARKER_PREFIX}build")
    build_tab.click()
    assert main_instance.namespace.command == "build"
    await user.should_see("output")

    # Click "test" tab and verify its content
    test_tab = user.find(marker=f"{SubparserUi.TAB_MARKER_PREFIX}test")
    test_tab.click()
    assert main_instance.namespace.command == "test"
    await user.should_see("verbose")

    # Click "deploy" tab and verify its content
    deploy_tab = user.find(marker=f"{SubparserUi.TAB_MARKER_PREFIX}deploy")
    deploy_tab.click()
    assert main_instance.namespace.command == "deploy"
    await user.should_see("environment")


@nice_gooey_argparse_main(patch_argparse=False)
def main() -> None:
    parser = NgArgumentParser()

    subparsers = parser.add_subparsers(dest="command", help="Commands")

    parser_build = subparsers.add_parser("build", help="Build command")
    parser_build.add_argument("--output", type=str, help="Output directory")

    parser_test = subparsers.add_parser("test", help="Test command")
    parser_test.add_argument("--verbose", action="store_true", help="Verbose output")

    parser_deploy = subparsers.add_parser("deploy", help="Deploy command")
    parser_deploy.add_argument("--environment", choices=["dev", "prod"], help="Environment")

    parser.parse_args()


if __name__ == "__main__":
    main()
