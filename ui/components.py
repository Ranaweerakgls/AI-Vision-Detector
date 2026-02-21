from PyQt5.QtWidgets import QFrame, QPushButton, QWidget, QVBoxLayout
from PyQt5.QtCore import Qt


class CollapsibleWidget(QFrame):
    def __init__(self, title, parent=None):
        super().__init__(parent)
        self.setObjectName("collapsible")
        self._expanded = True

        self._main_layout = QVBoxLayout(self)
        self._main_layout.setContentsMargins(0, 0, 0, 0)
        self._main_layout.setSpacing(0)

        self._header = QPushButton(f"▼ {title}")
        self._header.setObjectName("collapsibleHeader")
        self._header.clicked.connect(self._toggle)
        self._main_layout.addWidget(self._header)

        self._content = QWidget()
        self._content_layout = QVBoxLayout(self._content)
        self._content_layout.setContentsMargins(15, 10, 15, 10)
        self._main_layout.addWidget(self._content)

        self._header.setCursor(Qt.PointingHandCursor)

    @property
    def content_layout(self):
        return self._content_layout

    def _toggle(self):
        self._expanded = not self._expanded
        self._content.setVisible(self._expanded)
        arrow = "▼" if self._expanded else "▶"
        title = self._header.text()[2:]
        self._header.setText(f"{arrow} {title}")

    def is_expanded(self):
        return self._expanded

    def set_expanded(self, expanded):
        self._expanded = expanded
        self._content.setVisible(expanded)
        arrow = "▼" if expanded else "▶"
        title = self._header.text()[2:]
        self._header.setText(f"{arrow} {title}")
