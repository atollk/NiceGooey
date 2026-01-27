import abc
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
        match self.action.type:
            case None:
                return str
            case argparse.FileType:
                raise NotImplementedError("argparse.FileType is deprecated and not supported.")
            case str():
                assert self.parent.parent_parser is not None
                return self.parent.parent_parser._registry_get("type", self.action.type)
            case callable():
                return self.action.type
            case _:
                raise ValueError(f"Unsupported action type: {self.action.type}")

    def render_action_name(self):
        with ui.row(align_items="center"):
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

    def render(self) -> None:
        pass

    def validate(self) -> bool:
        return True


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
        init: typing.Callable[..., value_element.ValueElement],
        forward_transform: typing.Callable[[typing.Any], typing.Any] = lambda x: x,
        **init_kwargs,
    ) -> None:
        """
        Creates/Renders the input element for this action and stores it in `self.element`.
        :param init: The type/constructor to use for the input element.
        :param forward_transform: The forward transformation when binding the input element value to the respective namespace variable.
        :param init_kwargs: Any arguments to be passed to the element constructor.
        """
        el = init(value=self.action.default, **init_kwargs)
        if isinstance(el, validation_element.ValidationElement):
            el.without_auto_validation()
        if not hasattr(self.parent.namespace, self.action.dest):
            setattr(self.parent.namespace, self.action.dest, self.action.default)
        el.bind_value(
            target_object=self.parent.namespace, target_name=self.action.dest, forward=forward_transform
        )
        self.element = el

    @abc.abstractmethod
    def _create_input_element(self) -> None:
        """Creates the input element for this action."""
        raise NotImplementedError()

    @typing.override
    def render(self) -> None:
        with ui.column():
            self.render_action_name()
            self._create_input_element()


class StoreActionUiElement(ActionUiElement[argparse._StoreAction]):
    @typing.override
    def _create_input_element(self) -> None:
        def forward_transform(v: typing.Any) -> typing.Any:
            ns = argparse.Namespace()
            ns.__setattr__(self.action.dest, getattr(self.parent.namespace, self.action.dest))
            try:
                cast = self._action_type()(v)
            except TypeError:
                pass
            else:
                assert self.parent.parent_parser is not None
                self.action(self.parent.parent_parser, ns, cast)
            return getattr(ns, self.action.dest)

        match self._action_type():
            case builtins.bool:
                self._create_input_element_generic(ui.checkbox, forward_transform)
            case builtins.int:
                self._create_input_element_generic(ui.number, forward_transform, format="%d")
            case builtins.float:
                self._create_input_element_generic(ui.number, forward_transform, format="%f")
            case builtins.str:
                self._create_input_element_generic(ui.input, forward_transform)
            case _:
                self._create_input_element_generic(
                    ui.input, forward_transform, validation=self._validate_input_value
                )


class StoreConstActionUiElement(ActionUiElement[argparse._StoreConstAction]):
    @typing.override
    def _create_input_element(self) -> None:
        def forward_transform(v: typing.Any) -> typing.Any:
            if v is True:
                ns = argparse.Namespace()
                assert self.parent.parent_parser is not None
                self.action(self.parent.parent_parser, ns, None)
                return getattr(ns, self.action.dest)
            else:
                return self.action.default

        self._create_input_element_generic(ui.checkbox, forward_transform)


class CountActionUiElement(ActionUiElement[argparse._CountAction]):
    @typing.override
    def _create_input_element(self) -> None:
        self._create_input_element_generic(ui.number, format="%d")


class ListActionUiElement[ActionT: argparse.Action](ActionUiElement[ActionT], abc.ABC):
    @typing.override
    def _create_input_element(self) -> None:
        def forward_transform(vs: list[typing.Any] | None) -> list[typing.Any] | None:
            ns = argparse.Namespace()
            ns.__setattr__(self.action.dest, getattr(self.parent.namespace, self.action.dest))
            try:
                cast = [self._action_type()(v) for v in (vs or [])]
            except TypeError:
                return getattr(ns, self.action.dest)
            else:
                return cast

        self._create_input_element_generic(ui.input_chips, forward_transform)

    def _create_add_element_generic(
        self, init: typing.Callable[..., value_element.ValueElement], **init_kwargs
    ) -> None:
        """Creates the ui element that can be used to add individual items to the list."""
        el = init(value=self.action.default, **init_kwargs)
        if isinstance(el, validation_element.ValidationElement):
            el.without_auto_validation()

        def add() -> None:
            ns = argparse.Namespace()
            assert self.parent.parent_parser is not None
            assert self.element is not None
            self.action(self.parent.parent_parser, ns, el.value)
            new = (self.element.value or []) + getattr(ns, self.action.dest)
            self.element.set_value(new)
            el.set_value(None)

        ui.button(icon="plus", on_click=add)

    @abc.abstractmethod
    def _create_add_element(self) -> None:
        raise NotImplementedError()

    @typing.override
    def render(self) -> None:
        with ui.column():
            self.render_action_name()
            self._create_input_element()
            self._create_add_element()


class AppendActionUiElement(ListActionUiElement[argparse._AppendAction]):
    @typing.override
    def _create_add_element(self) -> None:
        match self._action_type():
            case builtins.bool:
                self._create_add_element_generic(ui.checkbox)
            case builtins.int:
                self._create_add_element_generic(ui.number, format="%d")
            case builtins.float:
                self._create_add_element_generic(ui.number, format="%f")
            case builtins.str:
                self._create_add_element_generic(ui.input)
            case _:
                self._create_add_element_generic(ui.input)


class AppendConstActionUiElement(ListActionUiElement[argparse._AppendConstAction]):
    @typing.override
    def _create_add_element(self) -> None:
        self._create_add_element_generic(value_element.ValueElement)


class ExtendActionUiElement(AppendActionUiElement):
    # There is no difference between extend and append in the UI.
    pass
