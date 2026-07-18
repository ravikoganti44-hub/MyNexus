"""
Progress celebration overlay — shows animated confetti/emoji when milestones are hit.
"""
import random
from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout
from PyQt6.QtCore import Qt, QTimer, QPropertyAnimation, QPoint, QEasingCurve
from PyQt6.QtGui import QFont


class CelebrationOverlay(QWidget):
    """Full-window overlay that rains confetti emojis for ~2 seconds."""

    EMOJIS = ["🎉", "🏆", "⭐", "🔥", "💪", "🚀", "✨", "🎊"]

    def __init__(self, parent, message: str = "Milestone reached!"):
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self.resize(parent.size())
        self.move(0, 0)

        # Banner message
        banner = QLabel(message, self)
        banner.setAlignment(Qt.AlignmentFlag.AlignCenter)
        banner.setFont(QFont("Segoe UI", 22, QFont.Weight.Bold))
        banner.setStyleSheet(
            "color: #f5c518; background: rgba(0,0,0,0.55); border-radius: 12px; padding: 12px 28px;"
        )
        banner.adjustSize()
        banner.move((self.width() - banner.width()) // 2, self.height() // 3)

        # Spawn floating emoji particles
        self._particles = []
        for _ in range(18):
            emoji = random.choice(self.EMOJIS)
            lbl = QLabel(emoji, self)
            lbl.setFont(QFont("Segoe UI Emoji", random.randint(18, 32)))
            lbl.setStyleSheet("background: transparent;")
            lbl.adjustSize()
            start_x = random.randint(0, max(1, self.width() - 30))
            lbl.move(start_x, -40)
            lbl.show()

            anim = QPropertyAnimation(lbl, b"pos", self)
            anim.setStartValue(QPoint(start_x, -40))
            anim.setEndValue(QPoint(
                start_x + random.randint(-60, 60),
                self.height() + 40,
            ))
            anim.setDuration(random.randint(1800, 3000))
            anim.setEasingCurve(QEasingCurve.Type.InQuad)
            anim.start()
            self._particles.append(anim)

        self.show()
        self.raise_()
        QTimer.singleShot(3200, self._fade_out)

    def _fade_out(self):
        self.hide()
        self.deleteLater()


def maybe_celebrate(parent, completed_count: int):
    """Show celebration at milestone thresholds."""
    milestones = {10, 25, 50, 100, 200, 500, 1000}
    if completed_count in milestones:
        CelebrationOverlay(parent, f"🎉 {completed_count} activities completed!")
