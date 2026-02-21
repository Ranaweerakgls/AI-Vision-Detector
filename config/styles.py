DARK_THEME_STYLESHEET = """
* { font-family: 'Segoe UI', sans-serif; }
QWidget { background-color: #0a0a0a; color: #e0e0e0; }
QPushButton {
    background-color: #1a1a1a;
    border: 1px solid #2a2a2a;
    border-radius: 8px;
    padding: 10px 16px;
    font-size: 13px;
    font-weight: 500;
}
QPushButton:hover {
    background-color: #252525;
    border-color: #38bdf8;
}
QPushButton:pressed {
    background-color: #38bdf8;
    color: #000;
}
QPushButton:disabled { opacity: 0.5; }
QSlider::groove:horizontal {
    height: 6px;
    background: #1a1a1a;
    border-radius: 3px;
}
QSlider::handle:horizontal {
    background: #38bdf8;
    width: 18px;
    margin: -6px 0;
    border-radius: 9px;
}
QComboBox {
    background-color: #1a1a1a;
    border: 1px solid #2a2a2a;
    border-radius: 6px;
    padding: 8px 12px;
}
QComboBox:hover { border-color: #38bdf8; }
QComboBox::drop-down { border: none; width: 30px; }
QComboBox QAbstractItemView {
    background-color: #1a1a1a;
    selection-background-color: #38bdf8;
}
#videoContainer {
    background-color: #000;
    border-radius: 12px;
    border: 1px solid #1a1a1a;
}
#sidePanel {
    background-color: #0f0f0f;
    border-left: 1px solid #1a1a1a;
}
#collapsible { background-color: #141414; border-radius: 8px; margin: 4px 0; }
#collapsibleHeader {
    background-color: transparent;
    border: none;
    text-align: left;
    font-weight: 600;
    font-size: 11px;
    text-transform: uppercase;
    letter-spacing: 1px;
    color: #38bdf8;
    padding: 12px;
}
#collapsibleHeader:hover { background-color: transparent; }
#detectionList QListWidget {
    background-color: transparent;
    border: none;
    font-size: 13px;
}
#detectionList QListWidget::item {
    padding: 6px 8px;
    border-radius: 4px;
    margin: 2px 0;
}
#detectionList QListWidget::item:hover { background-color: #1a1a1a; }
#statsCard { background-color: #141414; border-radius: 10px; padding: 10px; }
#statValue { font-size: 22px; font-weight: bold; color: #38bdf8; }
#statLabel { font-size: 10px; color: #666; text-transform: uppercase; }
#titleLabel { font-size: 20px; font-weight: 700; letter-spacing: 2px; color: #fff; }
#subtitleLabel { font-size: 11px; color: #555; }
#fpsLabel { font-size: 13px; font-weight: 600; color: #10b981; }
#loadingLabel { font-size: 13px; color: #38bdf8; font-weight: 500; }
.section-label { color: #666; font-size: 10px; text-transform: uppercase; margin-top: 8px; }
"""
