import nicegui.elements.mixins.value_element


def clear_value_element(e: nicegui.elements.mixins.value_element.ValueElement) -> None:
    e.value = ""
