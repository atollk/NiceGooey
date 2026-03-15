import argparse
import enum


class Nargs(enum.Enum):
    OPTIONAL = argparse.OPTIONAL
    ZERO_OR_MORE = argparse.ZERO_OR_MORE
    ONE_OR_MORE = argparse.ONE_OR_MORE
    PARSER = argparse.PARSER
    REMAINDER = argparse.REMAINDER
    SUPPRESS = argparse.SUPPRESS
    SINGLE_ELEMENT = "1"
