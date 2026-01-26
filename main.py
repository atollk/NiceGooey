from nicegooey.argparse import nice_gooey_argparse_main
from argparse import ArgumentParser


def process(*, name: str):
    print(f"Hello from nicegooey! {name}")


@nice_gooey_argparse_main(patch_argparse=True)
def main():
    parser = ArgumentParser()
    parser.add_argument("--name", type=str, default="World", help="Your name")
    parser.add_argument("--age", "-a", type=int, help="Your age")
    parser.add_argument("--disable-meme", "-dm", action="store_true", help="Disable memes")
    group1 = parser.add_argument_group(title="gruppo")
    group1.add_argument("--level", type=int, choices=range(1, 6), help="Pick a level from 1 to 5")
    parser.add_argument(
        "--append_const", action="append_const", const="NiceGooey", help="Append a constant value"
    )
    parser.add_argument("--append", action="append", type=str, help="Append multiple values")
    args = parser.parse_args()
    process(name=args.name)


if __name__ in {"__main__", "__mp_main__"}:
    main()
