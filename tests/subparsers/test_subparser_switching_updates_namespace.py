import pytest
from nicegui.testing import User

from nicegooey.argparse import NgArgumentParser, nice_gooey_argparse_main
from nicegooey.argparse.main import main_instance
from nicegooey.argparse.ui_classes.groupings.subparser_ui import SubparserUi


@pytest.mark.nicegui_main_file(__file__)
async def test_subparser_switching_updates_namespace(user: User) -> None:
    """Test that switching between subparser tabs immediately updates the namespace with correct values."""

    await user.open("/")

    # Should see all three subparser tabs
    await user.should_see("build")
    await user.should_see("test")
    await user.should_see("deploy")

    # Find the tabs
    build_tab = user.find(marker=f"{SubparserUi.TAB_MARKER_PREFIX}build")
    test_tab = user.find(marker=f"{SubparserUi.TAB_MARKER_PREFIX}test")
    deploy_tab = user.find(marker=f"{SubparserUi.TAB_MARKER_PREFIX}deploy")

    # The namespace should have command set to "build"
    assert main_instance.namespace.command == "build"

    # Click on the test tab
    test_tab.click()

    # The namespace should now have command set to "test"
    assert main_instance.namespace.command == "test"

    # Click on the deploy tab
    deploy_tab.click()

    # The namespace should now have command set to "deploy"
    assert main_instance.namespace.command == "deploy"

    # Switch back to build
    build_tab.click()
    assert main_instance.namespace.command == "build"


@nice_gooey_argparse_main(patch_argparse=False)
def main() -> None:
    parser = NgArgumentParser()

    subparsers = parser.add_subparsers(dest="command", help="Commands", required=True)

    parser_build = subparsers.add_parser("build", help="Build command")
    parser_build.add_argument("--output", type=str, help="Output directory", default="/tmp/build")

    parser_test = subparsers.add_parser("test", help="Test command")
    parser_test.add_argument("--verbose", action="store_true", help="Verbose output")

    parser_deploy = subparsers.add_parser("deploy", help="Deploy command")
    parser_deploy.add_argument("--environment", choices=["dev", "prod"], help="Environment", default="dev")

    parser.parse_args()


if __name__ == "__main__":
    main()
