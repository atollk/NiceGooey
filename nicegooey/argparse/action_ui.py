import argparse
import builtins
import typing

from nicegui import ui
from nicegui.elements.mixins import value_element, validation_element

from .main import NiceGooeyMain


class ActionUi[ActionT: argparse.Action]:
    parent: NiceGooeyMain
    action: ActionT

    @staticmethod
    def from_action(parent: NiceGooeyMain, action: argparse.Action) -> "ActionUi | None":
        match action:
            case argparse._StoreAction():
                return StoreActionUiElement(parent=parent, action=action)
            case argparse._StoreConstAction():
                return StoreConstActionUiElement(parent=parent, action=action)
            case argparse._ExtendAction():
                return ExtendActionUiElement(parent=parent, action=action)
            case argparse._AppendAction():
                return AppendActionUiElement(parent=parent, action=action)
            case argparse._AppendConstAction():
                return AppendConstActionUiElement(parent=parent, action=action)
            case argparse._CountAction():
                return CountActionUiElement(parent=parent, action=action)
            case argparse._HelpAction() | argparse._VersionAction():
                # help and version are handled differently
                return None
            case argparse._SubParsersAction():
                pass  # TODO
                raise NotImplementedError()
            case _:
                raise NotImplementedError(f"UI for action type {type(action)} not implemented")

    def __init__(self, parent: NiceGooeyMain, action: ActionT) -> None:
        self.parent = parent
        self.action = action

    def _action_type(self) -> typing.Callable[[str], typing.Any]:
        if self.action.type is None:
            return str
        else:
            return self.action.type

    def render_action_name(self):
        with ui.row():
            ui.label(self.action.metavar or self.action.dest)
            if self.action.help:
                with ui.button(icon="question_mark").props("round padding=xs size=xs"):
                    ui.tooltip(self.action.help)

    def render(self) -> None:
        pass

    def validate(self) -> bool:
        return True


class ActionUiElement[ActionT: argparse.Action](ActionUi[ActionT]):
    element: value_element.ValueElement | None = None

    def validate(self) -> bool:
        if isinstance(self.element, validation_element.ValidationElement):
            return self.element.validate()
        return True

    def _validate_input_value(self, value: str) -> str | None:
        try:
            self._action_type()(value)
            return None
        except Exception as e:
            return str(e)


class StoreActionUiElement(ActionUiElement[argparse._StoreAction]):
    def _create_input_element(self, init: typing.Callable[..., value_element.ValueElement], **kwargs) -> None:
        el = init(value=self.action.default, **kwargs)
        if isinstance(el, validation_element.ValidationElement):
            el.without_auto_validation()
        if not hasattr(self.parent.namespace, self.action.dest):
            setattr(self.parent.namespace, self.action.dest, self.action.default)

        def forward_transform(v: typing.Any) -> typing.Any:
            ns = argparse.Namespace()
            ns.__setattr__(self.action.dest, getattr(self.parent.namespace, self.action.dest))
            try:
                cast = self._action_type()(v)
            except TypeError:
                pass
            else:
                self.action(self.parent.parent_parser, ns, cast)
            return getattr(ns, self.action.dest)

        el.bind_value(
            target_object=self.parent.namespace, target_name=self.action.dest, forward=forward_transform
        )
        self.element = el

    def render(self) -> None:
        match self._action_type():
            case builtins.bool:
                with ui.row():
                    self._create_input_element(ui.checkbox)
                    self.render_action_name()
            case builtins.int:
                with ui.row():
                    self._create_input_element(ui.number, format="%d")
                    self.render_action_name()
            case builtins.float:
                with ui.row():
                    self._create_input_element(ui.number, format="%f")
                    self.render_action_name()
            case builtins.str:
                with ui.row():
                    self._create_input_element(ui.input)
                    self.render_action_name()
            case _:
                with ui.row():
                    self._create_input_element(ui.input, validation=self._validate_input_value)
                    self.render_action_name()


class StoreConstActionUiElement(ActionUiElement[argparse._StoreConstAction]):
    def _create_input_element(self, init: typing.Callable[..., value_element.ValueElement], **kwargs) -> None:
        el = init(value=self.action.default, **kwargs)
        if isinstance(el, validation_element.ValidationElement):
            el.without_auto_validation()
        if not hasattr(self.parent.namespace, self.action.dest):
            setattr(self.parent.namespace, self.action.dest, self.action.default)

        def forward_transform(v: typing.Any) -> typing.Any:
            if v:
                ns = argparse.Namespace()
                self.action(self.parent.parent_parser, ns, None)
                return getattr(ns, self.action.dest)
            else:
                return self.action.default

        el.bind_value(
            target_object=self.parent.namespace, target_name=self.action.dest, forward=forward_transform
        )
        self.element = el

    def render(self) -> None:
        with ui.row():
            self._create_input_element(ui.checkbox)
            self.render_action_name()


class CountActionUiElement(ActionUiElement[argparse._CountAction]):
    def render(self) -> None:
        with ui.row():
            self._create_input_element(ui.number, format="%d")
            self.render_action_name()


class ListActionUiElement[ActionT: argparse.Action](ActionUi[ActionT]):
    element: value_element.ValueElement | None = None

    def validate(self) -> bool:
        if isinstance(self.element, validation_element.ValidationElement):
            return self.element.validate()
        return True

    def _create_input_chips_element(self, **kwargs) -> None:
        # TODO: auto complete
        el = ui.input_chips(value=self.action.default, **kwargs)
        if isinstance(el, validation_element.ValidationElement):
            el.without_auto_validation()
        if not hasattr(self.parent.namespace, self.action.dest):
            setattr(self.parent.namespace, self.action.dest, self.action.default)

        def forward_transform(v: list[typing.Any] | None) -> list[typing.Any] | None:
            ns = argparse.Namespace()
            ns.__setattr__(self.action.dest, getattr(self.parent.namespace, self.action.dest))
            try:
                cast = [self._action_type()(x) for x in v]
            except TypeError:
                return getattr(ns, self.action.dest)
            else:
                return cast

        el.bind_value(
            target_object=self.parent.namespace, target_name=self.action.dest, forward=forward_transform
        )
        self.element = el

    def _validate_input_value(self, value: str) -> str | None:
        try:
            self._action_type()(value)
            return None
        except Exception as e:
            return str(e)


class AppendActionUiElement(ListActionUiElement[argparse._AppendAction]):
    def _create_add_element(self, init: typing.Callable[..., value_element.ValueElement], **kwargs) -> None:
        el = init(value=self.action.default, **kwargs)
        if isinstance(el, validation_element.ValidationElement):
            el.without_auto_validation()

        def add() -> None:
            ns = argparse.Namespace()
            self.action(self.parent.parent_parser, ns, el.value)
            new = (self.element.value or []) + getattr(ns, self.action.dest)
            self.element.set_value(new)
            el.set_value(None)

        ui.button("+", on_click=add)

    def render(self) -> None:
        match self._action_type():
            case builtins.bool:
                with ui.row():
                    self._create_input_chips_element()
                    self._create_add_element(ui.checkbox)
                    self.render_action_name()
            case builtins.int:
                with ui.row():
                    self._create_input_chips_element()
                    self._create_add_element(ui.number, format="%d")
                    self.render_action_name()
            case builtins.float:
                with ui.row():
                    self._create_input_chips_element()
                    self._create_add_element(ui.number, format="%f")
                    self.render_action_name()
            case builtins.str:
                with ui.row():
                    self._create_input_chips_element()
                    self._create_add_element(ui.input)
                    self.render_action_name()
            case _:
                with ui.row():
                    self._create_input_chips_element()
                    self._create_add_element(ui.input)
                    self.render_action_name()


class AppendConstActionUiElement(ListActionUiElement[argparse._AppendConstAction]):
    def render(self) -> None:
        with ui.row():
            self._create_input_chips_element()

            def add() -> None:
                assert self.element is not None
                self.action(self.parent.parent_parser, self.parent.namespace, self.element.value)

            ui.button("+", on_click=add)
            self.render_action_name()


class ExtendActionUiElement(AppendActionUiElement):
    pass
