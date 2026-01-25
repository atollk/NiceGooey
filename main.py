from nicegooey.argparse import ArgumentParser, nice_gooey_argparse_main


def process(*, name: str):
    print(f"Hello from nicegooey! {name}")


@nice_gooey_argparse_main(patch_argparse=False)
def main():
    parser = ArgumentParser()
    parser.add_argument("--name", type=str, default="World", help="Your name")
    parser.add_argument("--age", "-a", type=int, help="Your age")
    parser.add_argument("--disable-meme", "-dm", action="store_true", help="Disable memes")
    args = parser.parse_args()
    process(name=args.name)


if __name__ in {"__main__", "__mp_main__"}:
    main()
