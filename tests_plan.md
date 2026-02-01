### Basic tests

Tests to create a UI with basic actions:
- a string action
- an int action
- a float action
- a string action with choices
- an action with a `type` that can fail
- an action for each of the following predefined action types:
  - 'store_const'
  - 'store_true'
  - 'store_false'
  - 'count'
  - 'append_const'
  - 'append'
    - values of type str
    - values of type int
  - 'extend'

### Group tests

Tests to create action_groups and mutually_exclusive_groups and verify that they are displayed and function correctly.
Creates two action groups, a mutually_exclusive_group, and one mutually_exclusive_group that is part of another action group.
Verifies that they are displayed in the correct order and their actions are part of them.
Verifies that the mutually_exclusive_groups are verified correctly on submit.

### Bind tests

Test with multiple actions accessing the same "dest" variable:
- one string action and one int action with the same dest
- one "append_const" and one "append" with the same dest

The test should include that storing values / adding and removing elements updates both fields accordingly.

### Subparsers

TODO

### nargs

Verifies (for an action of str type), that the different options of "nargs" work correctly:
0, 1, 3, ?, *, +

### Special cases 1

https://stackoverflow.com/a/22751724/1833497

### System test 1

A clone of the complete OpenTofu CLI; no functionality, just the CLI arguments and their validation.

### System test 2

A clone of the complete uv CLI; no functionality, just the CLI arguments and their validation.
