import argparse

from nicegooey.argparse import global_state


class ArgumentParser(argparse.ArgumentParser):
    actions: list[argparse.Action]

    def __init__(self, *args, **kwargs) -> None:
        self.actions = []
        super().__init__(*args, **kwargs)

    def add_argument(self, *args, **kwargs):
        action = super().add_argument(
            *args,
            **kwargs,
        )
        self.actions.append(action)
        return action

    def add_argument_group(self, *args, **kwargs):
        # TODO
        return super().add_argument_group(*args, **kwargs)

    def add_subparsers(self, *args, **kwargs):
        # TODO
        return super().add_subparsers(*args, **kwargs)

    def parse_args(self, *args, **kwargs):
        return global_state.main_instance.parse_args(self, *args, **kwargs)
