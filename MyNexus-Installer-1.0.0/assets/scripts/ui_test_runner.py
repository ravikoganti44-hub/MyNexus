from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QTimer
import sys, os
from src.main import MainWindow
from PIL import ImageGrab

# Usage: python assets/scripts/ui_test_runner.py

SCREENSHOT_DIR = os.path.join(os.path.dirname(__file__), '..', 'screenshots')
os.makedirs(SCREENSHOT_DIR, exist_ok=True)

app = QApplication(sys.argv)
window = MainWindow()
window.show()

# sequence of (delay_ms, action_name)
steps = [
    (1000, 'dashboard'),
    (2000, 'activities'),
    (3000, 'integrations'),
    (4000, 'connected_apps'),
    (5000, 'settings'),
]

def take_screenshot(name):
    img = ImageGrab.grab()
    path = os.path.join(SCREENSHOT_DIR, f'{name}.png')
    img.save(path)
    print('Saved', path)

def perform_step(index=0):
    if index >= len(steps):
        QTimer.singleShot(500, app.quit)
        return
    delay, name = steps[index]
    # switch page
    mapping = {
        'dashboard': 0,
        'activities': 1,
        'integrations': 2,
        'connected_apps': 3,
        'settings': 4,
    }
    page_index = mapping.get(name, 0)
    try:
        window.pages.setCurrentIndex(page_index)
    except Exception as e:
        print('Could not switch page:', e)
    # capture after short delay
    QTimer.singleShot(500, lambda: (take_screenshot(name), perform_step(index+1)))

# start sequence
QTimer.singleShot(500, lambda: perform_step(0))

sys.exit(app.exec())