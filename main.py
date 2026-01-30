import argparse
import time

from nicegooey.argparse import nice_gooey_argparse_main, ArgumentParserConfig, NgArgumentParser


def process(parser: argparse.ArgumentParser, args: argparse.Namespace):
    print(args)
    time.sleep(1)
    print("wake up!")


@nice_gooey_argparse_main(patch_argparse=False)
def main():
    config = ArgumentParserConfig(argument_vp_width="w-4xl")
    parser = NgArgumentParser()
    parser.nicegooey_config = config

    parser.add_argument("--name", type=str, default="World", help="Your name")
    parser.add_argument("--age", "-a", type=int, help="Your age")
    parser.add_argument("--disable-meme", "-dm", action="store_true", help="Disable memes")
    parser.add_argument("--favorite-food", choices=["banana", "apple"])
    group1 = parser.add_argument_group(title="gruppo")
    group1.add_argument("--level", type=int, choices=range(1, 6), help="Pick a level from 1 to 5")
    parser.add_argument(
        "--append_const", action="append_const", const="NiceGooey", help="Append a constant value"
    )
    parser.add_argument("--append", action="append", type=str, help="Append multiple values")
    group2 = parser.add_mutually_exclusive_group()
    group2.add_argument("--asdf")
    group3 = group1.add_mutually_exclusive_group()

    def validate_xxx(v: str) -> str:
        if len(v) < 3:
            raise ValueError()
        else:
            return v

    group3.add_argument("--xxx", type=validate_xxx)
    group3.add_argument("--yyy")
    args = parser.parse_args()
    process(parser, args)


if __name__ in {"__main__", "__mp_main__"}:
    main()
