import argparse
import time

from nicegooey.argparse import ArgumentParserConfig, NgArgumentParser, nice_gooey_argparse_main


def process(parser: argparse.ArgumentParser, args: argparse.Namespace):
    print(args)
    time.sleep(1)
    print("wake up!")


@nice_gooey_argparse_main(patch_argparse=False)
def main1(*args, **kwargs):
    parser = NgArgumentParser()

    # Case 1: required=True, nargs="*" -> no enable checkbox
    parser.add_argument(
        "--packages-star-required", type=str, nargs="*", required=True, help="Required packages (nargs='*')"
    )

    # Case 2: required=True, nargs="+" -> no enable checkbox
    parser.add_argument(
        "--packages-plus-required", type=str, nargs="+", required=True, help="Required packages (nargs='+')"
    )

    # Case 3: required=False, nargs="*" -> has enable checkbox
    parser.add_argument(
        "--packages-star-optional", type=str, nargs="*", required=False, help="Optional packages (nargs='*')"
    )

    # Case 4: required=False, nargs="+" -> has enable checkbox
    parser.add_argument(
        "--packages-plus-optional", type=str, nargs="+", required=False, help="Optional packages (nargs='+')"
    )

    # parser = uv_parser()
    # parser = uv_parser_mre()
    ns = parser.parse_args()
    print(ns)


def uv_parser_mre() -> NgArgumentParser:
    parser = NgArgumentParser()

    subparsers = parser.add_subparsers(dest="subcommand")

    # tool command
    tool_parser = subparsers.add_parser("tool")
    tool_subparsers = tool_parser.add_subparsers(dest="tool_command")
    tool_install = tool_subparsers.add_parser("install")
    tool_install.add_argument("packages", type=str, nargs="+")

    # pip command
    pip_parser = subparsers.add_parser("pip")
    pip_subparsers = pip_parser.add_subparsers(dest="pip_command")
    pip_install = pip_subparsers.add_parser("install")
    pip_install.add_argument("packages", type=str, nargs="*")

    return parser


def uv_parser() -> NgArgumentParser:
    from tests.integration.uv import create_uv_parser

    return NgArgumentParser.from_argparse(create_uv_parser())


@nice_gooey_argparse_main(patch_argparse=False)
def main2(required: bool = False, nargs: int | str | None = None):
    config = ArgumentParserConfig(argument_vp_width="w-4xl")
    parser = NgArgumentParser()
    parser.nicegooey_config = config

    parser.add_argument("--name", type=str, default="World", help="Your name", required=required, nargs=nargs)
    parser.add_argument("--age", "-a", type=int, help="Your age", required=required, nargs=nargs)
    parser.add_argument("--disable-meme", "-dm", action="store_true", help="Disable memes", required=required)
    parser.add_argument("--favorite-food", choices=["banana", "apple"], required=required, nargs=nargs)
    group1 = parser.add_argument_group(title="gruppo")
    group1.add_argument(
        "--level",
        type=int,
        choices=range(1, 6),
        help="Pick a level from 1 to 5",
        required=required,
        nargs=nargs,
    )
    parser.add_argument(
        "--append_const",
        action="append_const",
        const="NiceGooey",
        help="Append a constant value",
        required=required,
    )
    parser.add_argument(
        "--append", action="append", type=str, help="Append multiple values", required=required, nargs=nargs
    )
    group2 = parser.add_mutually_exclusive_group(required=required)
    group2.add_argument("--asdf", nargs=nargs)
    group3 = group1.add_mutually_exclusive_group(required=required)

    def validate_xxx(v: str) -> str:
        if len(v) < 3:
            raise ValueError()
        else:
            return v

    group3.add_argument("--xxx", type=validate_xxx, nargs=nargs)
    group3.add_argument("--yyy", nargs=nargs)

    subps = parser.add_subparsers(required=required)
    subp1 = subps.add_parser("sub1")
    subp1.add_argument("--sub1a", required=required, nargs=nargs)
    subp1.add_argument("--sub1b", type=float, required=required, nargs=nargs)
    subp2 = subps.add_parser("sub2")
    subp2.add_argument("--sub2a", type=str, required=required, nargs=nargs)

    args = parser.parse_args()
    process(parser, args)


if __name__ in {"__main__", "__mp_main__"}:
    main1(required=False, nargs="*")
