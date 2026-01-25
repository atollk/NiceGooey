import argparse

from nicegooey.argparse import global_state


class ArgumentParser(argparse.ArgumentParser):
    def parse_args(self, *args, **kwargs):
        return global_state.main_instance.parse_args(self, *args, **kwargs)
