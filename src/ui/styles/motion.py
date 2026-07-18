"""
MyNexus Motion Language
-----------------------
Premium interaction timing/easing helpers for PyQt6.
Use these instead of magic durations in animation code.
"""

from src.ui.styles.tokens import get_tokens


def duration(name: str = "base") -> int:
    """
    Return motion duration in milliseconds for the current theme.
    Names map to token paths:
      fast   -> motion.duration.fast
      base   -> motion.duration.base
      slow   -> motion.duration.slow
    """
    tokens = get_tokens()
    key = f"motion.duration.{name}"
    raw = tokens.get(key)
    if raw is None:
        raise KeyError(key)
    if isinstance(raw, str) and raw.endswith("ms"):
        return int(raw[:-2])
    return int(raw)


def easing(name: str = "standard") -> str:
    """
    Return an easing curve spec usable with QPropertyAnimation / QEasingCurve.
    """
    tokens = get_tokens()
    key = f"motion.easing.{name}"
    raw = tokens.get(key)
    if raw is None:
        raise KeyError(key)
    return str(raw)
