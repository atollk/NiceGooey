# Test Plan — v1.0.0b2 Branch

This document lists all tests that should be added to cover new features and changed behavior
introduced on this branch compared to `main`. Existing tests for `FilePicker` (`tests/ui_util/`)
are already present and are not repeated here.

---

## 1. `NiceGooeyConfig` — New Top-Level Fields

### 1.1 `display_help: DisplayHelp` enum

Three modes were added: `NoDisplay`, `Tooltip` (default), `Label`.

- **`tests/config/test_display_help_no_display.py`**
  - Set `config.display_help = NiceGooeyConfig.DisplayHelp.NoDisplay`
  - Assert that no tooltip button (`icon="question_mark"`) and no help label are rendered for an action with `help="..."`.
  - Assert the action name label is still rendered.

- **`tests/config/test_display_help_tooltip.py`**
  - Use default config (Tooltip mode).
  - Assert a `?` icon button is rendered for an action with help text.
  - Assert no standalone help label is rendered.

- **`tests/config/test_display_help_label.py`**
  - Set `config.display_help = NiceGooeyConfig.DisplayHelp.Label`
  - Assert a `ui.label` with the help text is rendered beneath the action name.
  - Assert no tooltip button is rendered.
  - Assert that `%(default)s` and similar format vars in help strings are expanded correctly (since `_expand_help` is now used).

### 1.2 `require_all_with_default: bool`

- **`tests/config/test_require_all_with_default.py`**
  - Set `config.require_all_with_default = True`
  - Add an optional `--name` argument with `default="Alice"`.
  - Assert the action does **not** have an enable checkbox (i.e., is treated as required).
  - Assert `main_instance.namespace.name == "Alice"` initially.
  - Change the value and assert namespace updates.

- **`tests/config/test_require_all_with_default_no_default.py`**
  - Set `config.require_all_with_default = True`
  - Add an optional `--name` argument with no default.
  - Assert the action still shows an enable checkbox (default behavior for optional without default).

### 1.3 `action_card_class: str`

- **`tests/config/test_action_card_class.py`**
  - Set `config.action_card_class = "test-custom-class"`
  - Render the UI and assert that the `ui.item` wrapping an action has the `test-custom-class` CSS class applied.

### 1.4 `process_arguments_on_submit`

- **`tests/config/test_process_arguments_on_submit.py`**
  - Set `config.process_arguments_on_submit` to a custom synchronous callable that records the fact it was called.
  - Fill in required arguments, click Submit.
  - Assert the custom callable was invoked (and received the `main_func`).

- **`tests/config/test_process_arguments_on_submit_async.py`**
  - Same as above but with an `async` callable.
  - Assert it was awaited correctly (check a side-effect such as setting a flag).

---

## 2. `ActionConfig` — New Per-Action Fields

### 2.1 `display_name: str | None`

- **`tests/config/test_display_name_override.py`**
  - Add an argument `--output-file` and set `ActionConfig(display_name="Output File")`.
  - Assert the label `"Output File"` is rendered instead of `"output-file"` (or `"output_file"`).

### 2.2 `override_required: bool | None`

- **`tests/config/test_override_required_true.py`**
  - Add an optional `--count` argument (no `required=True`).
  - Set `ActionConfig(override_required=True)`.
  - Assert there is no enable checkbox (treated as required).

- **`tests/config/test_override_required_false.py`**
  - Add an argument with `required=True`.
  - Set `ActionConfig(override_required=False)`.
  - Assert an enable checkbox is shown (treated as optional).

- **`tests/config/test_override_required_none_positional.py`**
  - Add a positional argument (no `--` prefix) without any override.
  - Assert no enable checkbox — positional args are always considered required.

### 2.3 `override_type: Type | None`

- **`tests/config/test_override_type_renders_number_input.py`**
  - Add `--value` with `type=lambda s: int(s) * 2` (a custom callable type).
  - Set `ActionConfig(override_type=int)`.
  - Assert a `ui.number` widget is rendered rather than a `ui.input`.

- **`tests/config/test_override_type_renders_bool_input.py`**
  - Add `--flag` with `type=str`.
  - Set `ActionConfig(override_type=bool)`.
  - Assert a `ValidationCheckbox` is rendered.

### 2.4 `number_precision: int | None`

- **`tests/config/test_number_precision_float.py`**
  - Add `--ratio` with `type=float`.
  - Set `ActionConfig(number_precision=2)`.
  - Assert the rendered `ui.number` widget has `precision=2` in its props.

- **`tests/config/test_number_precision_int.py`**
  - Add `--count` with `type=int`.
  - Set `ActionConfig(number_precision=0)`.
  - Assert the rendered `ui.number` widget has `precision=0`.

- **`tests/config/test_number_precision_on_non_numeric_raises.py`**
  - Add `--name` with `type=str`.
  - Set `ActionConfig(number_precision=2)`.
  - Assert a `TypeError` is raised during render.

- **`tests/config/test_number_precision_on_choices_raises.py`**
  - Add `--fruit` with `choices=["apple", "banana"]`.
  - Set `ActionConfig(number_precision=1)`.
  - Assert a `TypeError` is raised during render.

---

## 3. `_should_render_enable_box` — `StoreConst` / `AppendConst` Default Behavior

These action types now show an enable checkbox by default (previously they didn't). The
`override_required` interactions are already covered by §2.2 and don't need repeating here.

### 3.1 `StoreConstActionUiElement` behavior

- **`tests/config/test_store_const_enable_checkbox_default.py`**
  - Add a store-const argument without `required=True`.
  - Assert an enable checkbox is shown (new default — store-const actions are useless without it).

- **`tests/config/test_store_const_no_enable_checkbox_when_required.py`**
  - Add a store-const argument with `required=True`.
  - Assert no enable checkbox is shown.

### 3.2 `AppendConstActionUiElement` behavior

- **`tests/config/test_append_const_enable_checkbox_default.py`**
  - Add an append-const argument without `required=True`.
  - Assert an enable checkbox is shown.

---

## 4. `choices` Default Value Selection (Priority Fix)

The new logic for `choices` actions selects the initial value as: `const → default → first option`.

- **`tests/basic_actions/test_string_action_with_choices_default.py`**
  - Add `--fruit` with `choices=["apple", "banana"]` and `default="banana"`.
  - Assert `main_instance.namespace.fruit == "banana"` on load (previously would fall back to first option).

- **`tests/basic_actions/test_string_action_with_choices_const.py`**
  - Add a store-const-style choices action where `const` is a valid choice.
  - Assert the initial value is the `const` value.

- **`tests/basic_actions/test_string_action_with_choices_fallback.py`**
  - Add `--fruit` with `choices=["apple", "banana"]`, no default, no const.
  - Assert initial value is `"apple"` (first option fallback).

---

## 5. `store_action_file` — `mode` Parameter

The function now requires a `mode` argument and uses the new `FilePicker`.

- **`tests/config/test_store_action_file_write_mode.py`**
  - Set `element_override=store_action_file(mode="write_file")`.
  - Assert a "Browse files" button renders within the action.
  - Assert clicking the button opens a dialog containing a `FilePicker`.

- **`tests/config/test_store_action_file_read_file_or_dir.py`**
  - Set `element_override=store_action_file(mode="read_file_or_dir")`.
  - Assert the dialog contains a `FilePicker` in `read` mode.

- **Update `tests/config/test_store_action_file.py`**
  - The existing test calls `store_action_file()` with no args, which now raises `TypeError`.
  - Update it to pass `mode="read_file"` and assert the same button-rendering behavior.

---

## 6. `NgActionWrapper` — Fluent Config API

- **`tests/config/test_ng_action_wrapper_config.py`**
  - Use `add_argument(...)` and store the returned `NgActionWrapper`.
  - Set `wrapper.nicegooey_config = NiceGooeyConfig.ActionConfig(display_name="Custom")`.
  - Assert the custom display name is rendered in the UI.

- **`tests/config/test_ng_action_wrapper_set_nicegooey_config.py`**
  - Use `wrapper.set_nicegooey_config(...)` helper method.
  - Assert it has the same effect as setting `wrapper.nicegooey_config` directly.

---

## 7. `parse_quasar_theme_variables` Utility

This is a pure utility function — no UI needed.

- **`tests/test_parse_quasar_theme_variables.py`**
  - Test that valid SCSS variables like `$primary: #ff0000;` are parsed into `{"primary": "#ff0000"}`.
  - Test that multiple variables are all parsed.
  - Test that lines that don't match the pattern (comments, non-color vars) are ignored.
  - Test empty string input returns no colors.
  - Since `app.colors()` has a side effect, mock it or check the parsed dict before the call (the function calls `app.colors` internally — test by mocking `nicegooey.argparse.util.app`).

---

## 8. Submit Error Handling — Exceptions in `main_func`

- **`tests/test_submit_exception.py`**
  - Set `process_arguments_on_submit` to the default `NiceGooeyMain.submit_xterm_dialog` (or just leave config default).
  - Make `main_func` raise an exception (e.g., `RuntimeError("test error")`).
  - Submit and assert:
    - The `xterm` dialog is still opened.
    - The terminal output contains the red ANSI escape code (`\x1b[1;31m`) — indicating error styling.
    - The "Close" button is enabled after completion (not frozen).

---

## 9. `ActionUiElement._render_action_name` — Help Text Expansion

- **`tests/config/test_display_help_expand_default.py`**
  - Add `--count` with `default=5` and `help="Count (default: %(default)s)"`.
  - Set `display_help = DisplayHelp.Label`.
  - Assert the rendered label contains `"Count (default: 5)"`, not the unexpanded format string.

---

## Summary Table

| Area | New Test File(s) | Priority |
|---|---|---|
| `display_help` modes | `test_display_help_{no_display,tooltip,label}.py` | High |
| `require_all_with_default` | `test_require_all_with_default*.py` | High |
| `action_card_class` | `test_action_card_class.py` | Medium |
| `process_arguments_on_submit` | `test_process_arguments_on_submit*.py` | High |
| `display_name` override | `test_display_name_override.py` | Medium |
| `override_required` | `test_override_required_*.py` | High |
| `override_type` | `test_override_type_*.py` | High |
| `number_precision` | `test_number_precision_*.py` | Medium |
| `StoreConst`/`AppendConst` default enable-box | `test_store_const_enable_checkbox_*.py`, `test_append_const_enable_checkbox_default.py` | High |
| `choices` default priority | `test_string_action_with_choices_{default,const,fallback}.py` | Medium |
| `store_action_file` modes | `test_store_action_file_{write,read_file_or_dir}.py` + update existing | High |
| `NgActionWrapper` config API | `test_ng_action_wrapper_*.py` | Medium |
| `parse_quasar_theme_variables` | `test_parse_quasar_theme_variables.py` | Low |
| Submit exception handling | `test_submit_exception.py` | Medium |
| Help text expansion | `test_display_help_expand_default.py` | Low |
