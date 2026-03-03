# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

NiceGooey is a Python library that transforms Python CLI programs (using argparse) into modern web-based UIs. It uses NiceGUI as the underlying web framework to automatically generate interactive web interfaces from ArgumentParser definitions.

## Build and Development Commands

### Setup
```bash
# Install dependencies (using uv)
uv sync

# Activate virtual environment
source .venv/bin/activate
```

### Testing
```bash
# Run all tests
pytest

# Run specific test file
pytest tests/basic_actions/test_string_action.py

# Run specific test function
pytest tests/basic_actions/test_string_action.py::test_string_action

# Tests use NiceGUI's testing framework with async/await patterns
```

### Code Quality
```bash
# Run linting (uses ruff)
ruff check .

# Auto-fix linting issues
ruff check --fix .

# Format code
ruff format .

# Run pre-commit hooks
pre-commit run --all-files
```

### Running Examples
```bash
# Run the main demo
python main.py
```

## Architecture

### Core Components

1. **`nicegooey.argparse.patch.nice_gooey_argparse_main`**: Main decorator that wraps user functions to intercept ArgumentParser operations and launch the web UI instead of command-line parsing.

2. **`nicegooey.argparse.argument_parser.NgArgumentParser`**: Custom ArgumentParser subclass that redirects `parse_args()` calls to the NiceGooey main instance, which launches the web UI.

3. **`nicegooey.argparse.main.NiceGooeyMain`**: Singleton that manages the application lifecycle, coordinates between argparse and NiceGUI, and handles form submission. The global instance is `main_instance`.

4. **UI Classes** (`nicegooey/argparse/ui_classes/`):
   - `root.py`: Top-level UI container that renders the entire form
   - `argument_group_ui.py`: Handles argument groups
   - `mutually_exclusive_group_ui.py`: Handles mutually exclusive argument groups
   - `subparser_ui.py`: Handles subparsers
   - `actions/`: Contains UI element classes for different argparse actions (store, append, store_true, etc.)

### Data Flow

1. User calls function decorated with `@nice_gooey_argparse_main()`
2. Decorator sets up context and activates `main_instance.main_func`
3. User code creates ArgumentParser and calls `parse_args()`
4. `parse_args()` redirects to `main_instance.parse_args()`, which launches NiceGUI web server
5. UI is rendered based on ArgumentParser configuration (arguments, groups, subparsers)
6. User interacts with web form, values are bound to `main_instance.namespace` (a `BindingNamespace`)
7. On submit, validation runs, then original user function is executed with captured arguments
8. Output is displayed in a terminal dialog within the web UI

### Key Design Patterns

- **Action Pattern**: Each argparse action type (store, append, store_true, etc.) has a corresponding UI element class in `ui_classes/actions/`
- **Binding**: Uses `BindingNamespace` (from `util.py`) to bind UI elements to namespace attributes
- **Singleton**: `main_instance` is a global singleton that manages application state
- **Context Managers**: Used for patching argparse and managing active function contexts

### Testing

- Tests use NiceGUI's testing framework with `@pytest.mark.nicegui_main_file(__file__)`
- Each test file defines its own `main()` function that gets tested
- `conftest.py` contains a fixture that resets `main_instance` before each test
- Tests use `User` object to interact with UI elements and verify behavior
- Special helper `input_number()` in conftest for interacting with number inputs

## Important Notes

- The library is published under LGPL license
- When adding new argparse action types, create corresponding UI element classes in `ui_classes/actions/`
- All UI rendering happens through the UI class hierarchy starting from `RootUi`
- The `patch_argparse` parameter in the decorator controls whether to globally patch argparse.ArgumentParser or require explicit use of NgArgumentParser
- Recent work has focused on supporting `nargs` parameter and `required` parameter for arguments
