# type: ignore

import argparse


from nicegooey.argparse import NgArgumentParser, nice_gooey_argparse_main, NiceGooeyConfig

"""
MP3 Encoder - A software encoder for converting audio to the MP3 format.

Example usage:
    python mp3_encoder.py /Desktop/song.flac --compression high -m 8 -lr
    python mp3_encoder.py input.wav -o output.mp3 --compression medium --resample 44.1
    python mp3_encoder.py input.flac -o out.mp3 --lowpass 20.0 --lowpass-enable --resample 48.0 --resample-enable
"""


def build_parser() -> argparse.ArgumentParser:
    parser = NgArgumentParser(
        prog="mp3_encoder.py",
        description="MP3 Encoder — A software encoder for converting audio to the MP3 format.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )

    # ── Positional ────────────────────────────────────────────────────────────
    parser.add_argument(
        "input",
        metavar="INPUT_FILE",
        help="Path to the source audio file to encode (e.g. /Desktop/song.flac).",
    )

    # ── Output Stage ──────────────────────────────────────────────────────────
    output_group = parser.add_argument_group(
        "Output Stage",
        "Specify the desired output behavior for the encoded file.",
    )
    output_group.add_argument(
        "-o",
        "--output",
        metavar="OUTPUT_FILE",
        dest="output_file",
        default=None,
        help=(
            "The output destination for the encoded file. "
            "Defaults to the input filename with an .mp3 extension."
        ),
    )
    output_group.add_argument(
        "--compression",
        metavar="LEVEL",
        choices=["low", "medium", "high"],
        default="medium",
        help=(
            "Compression quality level: low, medium, or high. "
            "Higher compression yields smaller files at the cost of quality. "
            "Default: %(default)s."
        ),
    )
    output_group.add_argument(
        "-m",
        "--bitrate-mode",
        metavar="MODE",
        type=int,
        choices=range(0, 10),
        dest="bitrate_mode",
        default=4,
        help=(
            "Bitrate mode (0–9). Lower values produce higher quality / larger files; "
            "higher values produce smaller files. Default: %(default)s."
        ),
    )

    # ── Resampling ────────────────────────────────────────────────────────────
    resample_group = parser.add_argument_group(
        "Resampling",
        "Control lowpass filtering and output sample-rate resampling.",
    )

    # Lowpass
    resample_group.add_argument(
        "--lowpass",
        metavar="FREQ_KHZ",
        type=float,
        default=None,
        help=(
            "Lowpass filter cutoff frequency in kHz. "
            "Frequencies above this value are attenuated before encoding."
        ),
    )
    resample_group.add_argument(
        "-l",
        "--lowpass-enable",
        action="store_true",
        dest="lowpass_enable",
        default=False,
        help="Enable the lowpass filter. Requires --lowpass to be set.",
    )

    # Resample
    resample_group.add_argument(
        "--resample",
        metavar="FREQ_KHZ",
        type=float,
        default=None,
        help=(
            "Target sampling frequency of the output file in kHz "
            "(e.g. 44.1, 48.0). Resamples the audio stream before encoding."
        ),
    )
    resample_group.add_argument(
        "-r",
        "--resample-enable",
        action="store_true",
        dest="resample_enable",
        default=False,
        help="Enable resampling. Requires --resample to be set.",
    )

    parser.nicegooey_config.root_card_class = "max-w-6xl"
    parser.nicegooey_config.display_help = NiceGooeyConfig.DisplayHelp.Label
    parser.nicegooey_config.require_all_with_default = True
    return parser


def validate(args: argparse.Namespace, parser: argparse.ArgumentParser) -> None:
    """Cross-field validation that argparse itself cannot express."""
    if args.lowpass_enable and args.lowpass is None:
        parser.error("--lowpass-enable requires --lowpass <FREQ_KHZ> to be specified.")
    if args.resample_enable and args.resample is None:
        parser.error("--resample-enable requires --resample <FREQ_KHZ> to be specified.")


@nice_gooey_argparse_main(patch_argparse=True)
def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    validate(args, parser)

    # Pretty-print parsed configuration (no encoding logic — parser demo only)
    print("=" * 52)
    print("  MP3 Encoder — parsed configuration")
    print("=" * 52)
    print(f"  Input file   : {args.input}")
    print(f"  Output file  : {args.output_file or '<derive from input>'}")
    print(f"  Compression  : {args.compression}")
    print(f"  Bitrate mode : {args.bitrate_mode}")
    print()
    print("  Resampling")
    print(
        f"    Lowpass    : {'enabled' if args.lowpass_enable else 'disabled'}"
        + (f" @ {args.lowpass} kHz" if args.lowpass is not None else "")
    )
    print(
        f"    Resample   : {'enabled' if args.resample_enable else 'disabled'}"
        + (f" @ {args.resample} kHz" if args.resample is not None else "")
    )
    print("=" * 52)
    print("  (No encoding performed — parser demonstration only)")


if __name__ == "__main__":
    main()
