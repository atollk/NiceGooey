import abc
import argparse
import builtins
import typing

from nicegui import ui
from nicegui.elements.mixins import value_element, validation_element
from nicegui.elements.mixins.validation_element import ValidationElement

from ..main import NiceGooeyMain
from .util import UiWrapper


class ActionUi[ActionT: argparse.Action](UiWrapper):
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
            case argparse._HelpAction() | argparse._VersionAction() | argparse._SubParsersAction():
                # handled differently
                return None
            case _:
                raise NotImplementedError(f"UI for action type {type(action)} not implemented")

    def __init__(self, parent: NiceGooeyMain, action: ActionT) -> None:
        super().__init__(parent)
        self.action = action

    def render_action_name(self):
        with ui.row(align_items="center").props("data-testid=ng-action-name"):
            if isinstance(self.action.metavar, str):
                name = self.action.metavar
            elif isinstance(self.action.metavar, tuple):
                name = self.action.metavar[0]
            else:
                name = self.action.dest
            ui.label(name).classes("font-bold")
            if self.action.help:
                with ui.button(icon="question_mark").props("round padding=xs size=xs"):
                    ui.tooltip(self.action.help)

    def _action_type(self) -> typing.Callable[[str], typing.Any]:
        match self.action.type:
            case None:
                return str
            case argparse.FileType:
                raise NotImplementedError("argparse.FileType is deprecated and not supported.")
            case str():
                assert self.parent.parent_parser is not None
                return self.parent.parent_parser._registry_get("type", self.action.type)
            case _:
                return self.action.type

    def _action_type_input(self, *args, **kwargs) -> value_element.ValueElement:
        """Creates a ValueElement that represents the input of a single item matching the type of this action."""
        el: value_element.ValueElement
        if self.action.choices is not None:
            # TODO: make the size consistent
            choices = list(self.action.choices)
            el = ui.select(options=choices, *args, **kwargs)
        else:
            match self._action_type():
                case builtins.bool:
                    el = ui.checkbox(*args, **kwargs)
                case builtins.int:
                    el = ui.number(format="%d", *args, **kwargs).props("dense")
                case builtins.float:
                    el = ui.number(format="%f", *args, **kwargs).props("dense")
                case builtins.str:
                    el = ui.input(*args, **kwargs).props("dense")
                case _:
                    el = ui.input(*args, **kwargs).props("dense")
        el.props("data-testid=ng-action-type-input")
        return el

    def _action_default(self) -> typing.Any:
        if self.action.default is not None:
            return self.action.default
        if self.action.choices is not None:
            return []
        else:
            match self._action_type():
                case builtins.bool:
                    return False
                case builtins.int | builtins.float:
                    return 0
                case _:
                    return ""


class ActionUiElement[ActionT: argparse.Action](ActionUi[ActionT], abc.ABC):
    element: value_element.ValueElement | None = None

    @typing.override
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

    def _create_input_element_generic(
        self,
        init: typing.Callable[[typing.Any], value_element.ValueElement],
        forward_transform: typing.Callable[[typing.Any], typing.Any] = lambda x: x,
        validation: validation_element.ValidationFunction | validation_element.ValidationDict | None = None,
    ) -> value_element.ValueElement:
        """
        Creates/Renders the input element for this action and stores it in `self.element`.
        :param init: The type/constructor to use for the input element.
        :param forward_transform: The forward transformation when binding the input element value to the respective namespace variable.
        :return `self.element`
        """
        el = init(self._action_default())
        if isinstance(el, validation_element.ValidationElement):
            el.without_auto_validation()
            if validation is not None:
                el.validation = validation
                el.error = None
        if not hasattr(self.parent.namespace, self.action.dest):
            setattr(self.parent.namespace, self.action.dest, self._action_default())
        el.bind_value(
            target_object=self.parent.namespace, target_name=self.action.dest, forward=forward_transform
        )
        self.element = el
        return self.element

    @abc.abstractmethod
    def _create_input_element(self) -> value_element.ValueElement:
        """Creates the input element for this action."""
        raise NotImplementedError()

    @typing.override
    def render(self) -> ui.element:
        c = ui.column()
        with c:
            self.render_action_name()
            self._create_input_element()
        return c


class StoreActionUiElement(ActionUiElement[argparse._StoreAction]):
    @typing.override
    def _create_input_element(self) -> value_element.ValueElement:
        def forward_transform(v: typing.Any) -> typing.Any:
            ns = argparse.Namespace()
            ns.__setattr__(self.action.dest, getattr(self.parent.namespace, self.action.dest))
            try:
                cast = self._action_type()(v)
            except (TypeError, ValueError):
                pass
            else:
                assert self.parent.parent_parser is not None
                self.action(self.parent.parent_parser, ns, cast)
            return getattr(ns, self.action.dest)

        el = self._create_input_element_generic(
            lambda v: self._action_type_input(value=v), forward_transform, self._validate_input_value
        )
        return el


class StoreConstActionUiElement(ActionUiElement[argparse._StoreConstAction]):
    @typing.override
    def _create_input_element(self) -> value_element.ValueElement:
        def forward_transform(v: typing.Any) -> typing.Any:
            if v is True:
                ns = argparse.Namespace()
                assert self.parent.parent_parser is not None
                self.action(self.parent.parent_parser, ns, None)
                return getattr(ns, self.action.dest)
            else:
                return self._action_default()

        return self._create_input_element_generic(ui.checkbox, forward_transform)


class CountActionUiElement(ActionUiElement[argparse._CountAction]):
    @typing.override
    def _create_input_element(self) -> value_element.ValueElement:
        return self._create_input_element_generic(lambda v: ui.number(v, format="%d"))


class ListActionUiElement[ActionT: argparse.Action](ActionUiElement[ActionT], abc.ABC):
    add_element_default_value: typing.Any = None

    @typing.override
    def _create_input_element(self) -> value_element.ValueElement:
        def forward_transform(vs: list[typing.Any] | None) -> list[typing.Any] | None:
            ns = argparse.Namespace()
            ns.__setattr__(self.action.dest, getattr(self.parent.namespace, self.action.dest))
            try:
                cast = [self._action_type()(v) for v in (vs or [])]
            except TypeError:
                return getattr(ns, self.action.dest)
            else:
                return cast

        el = self._create_input_element_generic(ui.input_chips, forward_transform)
        el.classes("w-xl")
        return el

    def _create_add_buton(self, value_el: value_element.ValueElement) -> ui.button:
        def add() -> None:
            if isinstance(value_el, validation_element.ValidationElement):
                if not value_el.validate():
                    return
            ns = argparse.Namespace()
            assert self.parent.parent_parser is not None
            assert self.element is not None
            self.action(self.parent.parent_parser, ns, value_el.value)
            new = (self.element.value or []) + getattr(ns, self.action.dest)
            self.element.set_value(new)
            value_el.set_value(self.add_element_default_value)

        return ui.button(on_click=add).props("square padding=xs").props("data-testid=ng-action-add-button")


class AppendActionUiElement(ListActionUiElement[argparse._AppendAction]):
    @typing.override
    def render(self) -> ui.element:
        c = ui.column()
        with c:
            self.render_action_name()
            with ui.row(align_items="center"):
                value_el = self._create_add_element()
                self._create_add_buton(value_el).set_icon("south")
            self._create_input_element()
        return c

    def _create_add_element(self) -> value_element.ValueElement:
        value_el = self._action_type_input()
        if isinstance(value_el, ValidationElement):
            value_el.validation = {"Must enter a value": lambda v: v is not None}
            value_el.without_auto_validation()
            value_el.error = None
        self.add_element_default_value = value_el.value
        return value_el


class AppendConstActionUiElement(ListActionUiElement[argparse._AppendConstAction]):
    @typing.override
    def render(self) -> ui.element:
        c = ui.column()
        with c:
            self.render_action_name()
            with ui.row(align_items="center"):
                self._create_input_element().props("use-input=false")
                value_el = value_element.ValueElement(value=None)
                self._create_add_buton(value_el).set_icon("add")
        return c


class ExtendActionUiElement(AppendActionUiElement):
    # There is no difference between extend and append in the UI.
    pass
