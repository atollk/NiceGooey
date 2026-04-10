"""Purely for internal testing"""

from nicegui import ui

import nicegooey
from nicegooey.argparse import NgArgumentParser

import multiprocessing


def foo(main_func):
    ui.label(text=main_func.__name__)


@nicegooey.argparse.nice_gooey_argparse_main(patch_argparse=False)
def main():
    parser = NgArgumentParser()
    parser.add_argument(
        "--fruit",
        choices=["apple", "banana", "orange"],
        const="orange",
        default="apple",
        nargs="?",
        help="Pick a fruit",
    )
    ns = parser.parse_args()
    print(ns)


# needed on linux
multiprocessing.set_start_method("spawn", force=True)

if __name__ in {"__main__", "__mp_main__"}:
    main()
