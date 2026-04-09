import nicegooey
from nicegooey.argparse import NgArgumentParser

import multiprocessing


@nicegooey.argparse.nice_gooey_argparse_main(patch_argparse=False)
def main():
    parser = NgArgumentParser()
    parser.add_argument("--value-str", dest="value", type=str, default="", help="Value as string")
    parser.add_argument("--value-int", dest="value", type=int, default=0, help="Value as int")
    parser.parse_args()
    raise NotImplementedError


# needed on linux
multiprocessing.set_start_method("spawn", force=True)

if __name__ in {"__main__", "__mp_main__"}:
    main()
