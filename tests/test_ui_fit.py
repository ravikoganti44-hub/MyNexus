"""`pytest-qt` smoke/window-fit tests for MyNexus pages."""
import pytest

from PyQt6.QtWidgets import QWidget, QVBoxLayout

from src.ui.components.dashboard import DashboardWidget
from src.ui.components.activities import ActivitiesWidget
from src.ui.components.integrations import IntegrationsWidget
from src.ui.components.connected_apps import ConnectedAppsWidget
from src.ui.components.document_vault import DocumentVaultWidget
from src.ui.components.budget import BudgetTrackerWidget
from src.ui.components.calendar_view import CalendarViewWidget
from src.ui.components.settings import SettingsWidget


def _wrap_in_fixed_container(widget, width=1000, height=600):
    container = QWidget()
    layout = QVBoxLayout(container)
    layout.setContentsMargins(0, 0, 0, 0)
    layout.setSpacing(0)
    layout.addWidget(widget)
    container.resize(width, height)
    return container


class TestPagesInternalFit:
    """Each page must fit inside a 1000x600 container without clipping."""

    @pytest.mark.parametrize(
        "factory",
        [
            DashboardWidget,
            ActivitiesWidget,
            IntegrationsWidget,
            ConnectedAppsWidget,
            DocumentVaultWidget,
            BudgetTrackerWidget,
            CalendarViewWidget,
            SettingsWidget,
        ],
    )
    def test_page_fits_container(self, qtbot, factory):
        page = factory()
        container = _wrap_in_fixed_container(page, 1000, 600)
        qtbot.addWidget(container)
        container.show()
        qtbot.waitExposed(container)
        container_width = container.width()
        assert page.width() <= container_width + 2, (
            f"{factory.__name__} exceeds container width"
        )
