"""
MyNexus Design Tokens
----------------------
Single source of truth for visual language.
No inline magic values in component files.
"""

# ---------------------------------------------------------------------------
# Semantic token paths used by components:
#   color.bg.primary / secondary / tertiary / hover / overlay
#   color.text.primary / secondary / tertiary / inverse
#   color.accent.primary / secondary / light
#   color.semantic.success / warning / error / info
#   radius.sm / md / lg / xl
#   space.1..16, space.gap.sm/md/lg, space.gutter
#   shadow.sm / md / lg / xl
#   motion.duration.fast / base / slow
#   motion.easing.standard / emphasized / decelerated / accelerated
#   type.scale.display / h1 / h2 / h3 / body / caption
#   type.weight.medium / semibold / bold
# ---------------------------------------------------------------------------

_DARK: dict[str, object] = {
    # Surfaces
    "color.bg.primary":   "#0d1117",
    "color.bg.secondary": "#161b22",
    "color.bg.tertiary":  "#21262d",
    "color.bg.hover":     "#282e36",
    "color.bg.overlay":   "rgba(22, 27, 34, 0.88)",
    # Text
    "color.text.primary":   "#e6edf3",
    "color.text.secondary": "#b0bbc9",
    "color.text.tertiary":  "#6b7280",
    "color.text.inverse":   "#0d1117",
    # Accent
    "color.accent.primary":   "#58a6ff",
    "color.accent.secondary": "#79c0ff",
    "color.accent.light":     "#8b5cf6",
    "color.accent.bold":      "#2563eb",
    "color.accent.hover":     "#3b82f6",
    "color.accent.pressed":   "#1d4ed8",
    # Semantic
    "color.semantic.success": "#3fb950",
    "color.semantic.warning": "#d29922",
    "color.semantic.error":   "#f85149",
    "color.semantic.info":    "#79c0ff",
    "color.semantic.high":    "#dc2626",
    "color.semantic.hover":   "#ef4444",
    "color.semantic.pressed": "#b91c1c",
    # Borders
    "color.border.default": "#30363d",
    "color.border.light":   "#444c56",
    # Radius
    "radius.sm": "6px",
    "radius.md": "10px",
    "radius.lg": "14px",
    "radius.xl": "18px",
    # Space
    "space.1": "4px",
    "space.2": "8px",
    "space.3": "12px",
    "space.4": "16px",
    "space.5": "20px",
    "space.6": "24px",
    "space.7": "32px",
    "space.8": "40px",
    "space.gap.sm": "8px",
    "space.gap.md": "16px",
    "space.gap.lg": "24px",
    "space.gutter": "24px",
    # Shadows — alpha stacked for depth hierarchy
    "shadow.sm": "0 1px 2px rgba(0,0,0,0.24)",
    "shadow.md": "0 4px 12px rgba(0,0,0,0.28)",
    "shadow.lg": "0 12px 32px rgba(0,0,0,0.34)",
    "shadow.xl": "0 24px 56px rgba(0,0,0,0.44)",
    # Motion
    "motion.duration.fast":   "80ms",
    "motion.duration.base":   "140ms",
    "motion.duration.slow":   "220ms",
    "motion.easing.standard":      "ease-out",
    "motion.easing.emphasized":    "cubic-bezier(0.2, 0, 0, 1)",
    "motion.easing.decelerated":   "cubic-bezier(0, 0, 0.2, 1)",
    "motion.easing.accelerated":   "cubic-bezier(0.4, 0, 1, 1)",
    # Typography
    "type.scale.display": "28px",
    "type.scale.h1":      "22px",
    "type.scale.h2":      "18px",
    "type.scale.h3":      "15px",
    "type.scale.body":    "13px",
    "type.scale.caption": "11px",
    "type.weight.medium":  "500",
    "type.weight.semibold": "600",
    "type.weight.bold":    "700",
}

_LIGHT: dict[str, object] = {
    # Surfaces
    "color.bg.primary":   "#ffffff",
    "color.bg.secondary": "#f6f8fa",
    "color.bg.tertiary":  "#eaeef2",
    "color.bg.hover":     "#d0d7de",
    "color.bg.overlay":   "rgba(255, 255, 255, 0.88)",
    # Text
    "color.text.primary":   "#1f2328",
    "color.text.secondary": "#656d76",
    "color.text.tertiary":  "#8b949e",
    "color.text.inverse":   "#ffffff",
    # Accent
    "color.accent.primary":   "#0969da",
    "color.accent.secondary": "#0550ae",
    "color.accent.light":     "#8250df",
    # Semantic
    "color.semantic.success": "#1a7f37",
    "color.semantic.warning": "#9a6700",
    "color.semantic.error":   "#cf222e",
    "color.semantic.info":    "#0969da",
    # Borders
    "color.border.default": "#d0d7de",
    "color.border.light":   "#afb8c1",
    # Radius shared
    "radius.sm": "6px",
    "radius.md": "10px",
    "radius.lg": "14px",
    "radius.xl": "18px",
    # Space shared
    "space.1": "4px",
    "space.2": "8px",
    "space.3": "12px",
    "space.4": "16px",
    "space.5": "20px",
    "space.6": "24px",
    "space.7": "32px",
    "space.8": "40px",
    "space.gap.sm": "8px",
    "space.gap.md": "16px",
    "space.gap.lg": "24px",
    "space.gutter": "24px",
    # Shadows
    "shadow.sm": "0 1px 2px rgba(0,0,0,0.10)",
    "shadow.md": "0 4px 12px rgba(0,0,0,0.10)",
    "shadow.lg": "0 12px 32px rgba(0,0,0,0.12)",
    "shadow.xl": "0 24px 56px rgba(0,0,0,0.14)",
    # Motion shared
    "motion.duration.fast":   "80ms",
    "motion.duration.base":   "140ms",
    "motion.duration.slow":   "220ms",
    "motion.easing.standard":      "ease-out",
    "motion.easing.emphasized":    "cubic-bezier(0.2, 0, 0, 1)",
    "motion.easing.decelerated":   "cubic-bezier(0, 0, 0.2, 1)",
    "motion.easing.accelerated":   "cubic-bezier(0.4, 0, 1, 1)",
    # Typography shared
    "type.scale.display": "28px",
    "type.scale.h1":      "22px",
    "type.scale.h2":      "18px",
    "type.scale.h3":      "15px",
    "type.scale.body":    "13px",
    "type.scale.caption": "11px",
    "type.weight.medium":  "500",
    "type.weight.semibold": "600",
    "type.weight.bold":    "700",
}

THEME_TOKEN_MAP: dict[str, dict[str, object]] = {
    "dark": _DARK,
    "light": _LIGHT,
}

_current_theme_name = "dark"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def set_current_theme(name: str) -> None:
    global _current_theme_name
    _current_theme_name = name if name in THEME_TOKEN_MAP else "dark"


def get_current_theme_name() -> str:
    return _current_theme_name


def get_tokens(theme_name: str | None = None) -> dict[str, object]:
    if theme_name is None:
        theme_name = _current_theme_name
    return THEME_TOKEN_MAP.get(theme_name, _DARK)


def token(path: str, theme_name: str | None = None) -> str | int | float:
    """Resolve a semantic token path like ``color.accent.primary``."""
    tokens = get_tokens(theme_name)
    value = tokens.get(path)
    if value is None:
        raise KeyError(f"Unknown design token: {path}")
    if isinstance(value, tuple):
        value = value[0]
    return value


def spacing(path: str, theme_name: str | None = None) -> int:
    """Return spacing token values as integer pixels for layout methods."""
    raw = token(path, theme_name)
    if isinstance(raw, (int, float)):
        return int(raw)
    if isinstance(raw, str):
        cleaned = raw.strip().lower()
        if cleaned.endswith("px"):
            cleaned = cleaned[:-2].strip()
        return int(cleaned)
    raise ValueError(f"Invalid spacing token: {path} = {raw!r}")
