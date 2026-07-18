from PyQt6.QtWidgets import QApplication
import sys, os
from src.main import MainWindow

app = QApplication(sys.argv)
window = MainWindow()
window.show()

results = []

# initial sizes
sizes = [1400, 1200, 1000, 800, 600]
for w in sizes:
    window.resize(w, 800)
    app.processEvents()
    sidebar_w = window.sidebar.width()
    collapsed = getattr(window.sidebar, '_collapsed', False)
    results.append((w, sidebar_w, collapsed))

# check pages and key widgets
page_checks = {}
pages = ['dashboard','activities','integrations','connected_apps','settings']
for idx, name in enumerate(pages):
    window.pages.setCurrentIndex(idx)
    app.processEvents()
    # quick checks
    page_widget = window.pages.currentWidget()
    # look for tables, buttons
    has_table = hasattr(page_widget, 'due_table') or hasattr(page_widget, 'activities_table')
    page_checks[name] = {
        'type': page_widget.__class__.__name__,
        'has_table': has_table,
        'width': page_widget.width(),
        'height': page_widget.height(),
    }

print('Resize results (window_width, sidebar_width, collapsed):')
for r in results:
    print(r)

print('\nPage checks:')
for k, v in page_checks.items():
    print(f"{k}: {v}")

# cleanup
window.reminder_engine.stop()
app.quit()
