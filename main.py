"""Purely for internal testing"""

from nicegui import ui

import nicegooey
from nicegooey.argparse import NgArgumentParser, NiceGooeyConfig

import multiprocessing


def foo(main_func):
    ui.label(text=main_func.__name__)


@nicegooey.argparse.nice_gooey_argparse_main(patch_argparse=False)
def main():
    parser = NgArgumentParser()
    flag_action = parser.add_argument("--flag", type=str, help="A flag", required=True)
    flag_action.nicegooey_config = NiceGooeyConfig.ActionConfig(override_type=bool)
    parser.parse_args()


# needed on linux
multiprocessing.set_start_method("spawn", force=True)

if __name__ in {"__main__", "__mp_main__"}:
    main()
