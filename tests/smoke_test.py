"""
Smoke test for NiceGooey - basic sanity check that core functionality works.

Run this directly with: python tests/smoke_test.py
"""

from nicegooey.argparse import NgArgumentParser, nice_gooey_argparse_main


@nice_gooey_argparse_main(patch_argparse=False)
def main() -> None:
    """Simple smoke test with a few basic arguments."""
    parser = NgArgumentParser()

    parser.add_argument("--name", type=str, help="Your name", default="World")
    parser.add_argument("--count", type=int, help="A count", default=1)
    parser.add_argument("--verbose", action="store_true", help="Enable verbose mode")
    parser.add_argument("--level", type=str, choices=["low", "medium", "high"], help="Choose a level")

    args = parser.parse_args()

    print(f"Hello, {args.name}!")
    print(f"Count: {args.count}")
    print(f"Verbose: {args.verbose}")
    print(f"Level: {args.level}")


if __name__ == "__main__":
    main()
