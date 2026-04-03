# type: ignore

import argparse


from nicegooey.argparse import NgArgumentParser, nice_gooey_argparse_main, NiceGooeyConfig
from nicegooey.argparse.util import parse_quasar_theme_variables

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
    ).nicegooey_config.override_required = True
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
        "-l",
        metavar="FREQ_KHZ",
        type=float,
        default=None,
        help=(
            "Lowpass filter cutoff frequency in kHz. "
            "Frequencies above this value are attenuated before encoding."
        ),
    )

    # Resample
    resample_group.add_argument(
        "--resample",
        "-r",
        metavar="FREQ_KHZ",
        type=float,
        default=None,
        help=(
            "Target sampling frequency of the output file in kHz "
            "(e.g. 44.1, 48.0). Resamples the audio stream before encoding."
        ),
    )

    parser.nicegooey_config.root_card_class = "max-w-6xl"
    parser.nicegooey_config.action_card_class = "max-w-1/3"
    parser.nicegooey_config.display_help = NiceGooeyConfig.DisplayHelp.Label
    parser.nicegooey_config.require_all_with_default = True
    parser.prog = "MP3 Encoder"
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

    parse_quasar_theme_variables("""
// Brand Colors
$primary   : #0ea5e9;
$secondary : #64748b;
$accent    : #06b6d4;

// Dark Mode
$dark      : #0c4a6e;
$dark-page : #082f49;

// Semantic Colors
$positive  : #22c55e;
$negative  : #ef4444;
$info      : #3b82f6;
$warning   : #f59e0b;

// Primary Scale
$primary-50: #f0f9ff;
$primary-100: #e0f2fe;
$primary-200: #bae6fd;
$primary-300: #7dd3fc;
$primary-400: #38bdf8;
$primary-500: #0ea5e9;
$primary-600: #0284c7;
$primary-700: #0369a1;
$primary-800: #075985;
$primary-900: #0c4a6e;
$primary-950: #082f49;

// Gray Scale
$gray-50: #f8fafc;
$gray-100: #f1f5f9;
$gray-200: #e2e8f0;
$gray-300: #cbd5e1;
$gray-400: #94a3b8;
$gray-500: #64748b;
$gray-600: #475569;
$gray-700: #334155;
$gray-800: #1e293b;
$gray-900: #0f172a;
$gray-950: #020617;

// Gradient Colors
$linear-1: rgba(255, 255, 255, 0) !default;
$linear-2: rgba(255, 255, 255, 1) !default;
$linear-dark-1: rgba(18, 18, 18, 0) !default;
$linear-dark-2: rgba(18, 18, 18, 1) !default;
    """)

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
