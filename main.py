import argparse
import time

from nicegooey.argparse import NgArgumentParser, nice_gooey_argparse_main, NiceGooeyConfig
from nicegooey.argparse.ui_classes.actions.action_alternatives import store_action_slider_element


def process(parser: argparse.ArgumentParser, args: argparse.Namespace):
    print(args)
    time.sleep(1)
    print("wake up!")


@nice_gooey_argparse_main(patch_argparse=False)
def main1(*args, **kwargs):
    parser = NgArgumentParser()

    # Create two actions
    custom_action = parser.add_argument("--custom-name", type=int, required=True)

    # Set up override for only the first action
    parser.nicegooey_config = NiceGooeyConfig(
        action_element_overrides={custom_action: store_action_slider_element(0, 10, 1)}
    )

    # parser = uv_parser()
    ns = parser.parse_args()
    print(ns)


def uv_parser() -> NgArgumentParser:
    from tests.integration.uv import create_uv_parser

    p = NgArgumentParser.from_argparse(create_uv_parser())
    p.nicegooey_config.argument_vp_width = "w-6xl"
    return p


@nice_gooey_argparse_main(patch_argparse=False)
def main2(required: bool = False, nargs: int | str | None = None):
    config = NiceGooeyConfig(root_card_class="w-4xl")
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
