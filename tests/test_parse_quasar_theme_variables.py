from unittest.mock import patch, MagicMock


import nicegooey.argparse.util as util_module
from nicegooey.argparse.util import parse_quasar_theme_variables


def _parse_colors(scss: str) -> dict:
    """Helper that runs parse_quasar_theme_variables and returns the dict passed to app.colors."""
    captured = {}

    def fake_colors(**kwargs):
        captured.update(kwargs)

    with patch.object(util_module, "app") as mock_app:
        mock_app.colors = fake_colors
        parse_quasar_theme_variables(scss)

    return captured


def test_single_variable():
    colors = _parse_colors("$primary: #ff0000;")
    assert colors == {"primary": "#ff0000"}


def test_multiple_variables():
    scss = "$primary: #ff0000;\n$secondary: #00ff00;\n$accent: #0000ff;"
    colors = _parse_colors(scss)
    assert colors == {"primary": "#ff0000", "secondary": "#00ff00", "accent": "#0000ff"}


def test_ignores_comments():
    scss = "// This is a comment\n$primary: #aabbcc;"
    colors = _parse_colors(scss)
    assert colors == {"primary": "#aabbcc"}


def test_ignores_non_color_vars():
    scss = "$font-size: 14px;\n$primary: #123456;"
    colors = _parse_colors(scss)
    assert colors == {"primary": "#123456"}


def test_empty_string_returns_no_colors():
    colors = _parse_colors("")
    assert colors == {}


def test_uppercase_hex_not_matched():
    # The regex requires lowercase hex digits — uppercase should not match
    colors = _parse_colors("$primary: #FF0000;")
    assert colors == {}


def test_returns_none():
    # The function itself returns None
    with patch.object(util_module, "app") as mock_app:
        mock_app.colors = MagicMock()
        result = parse_quasar_theme_variables("$primary: #aabbcc;")
    assert result is None
