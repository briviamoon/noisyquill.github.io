from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
                             QPushButton, QListWidget, QMessageBox)
from PyQt6.QtCore import Qt

class SettingsDialog(QDialog):
    def __init__(self, settings_manager, parent=None):
        super().__init__(parent)
        self.settings_manager = settings_manager
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        # Instructions
        instructions = QLabel(
            "To find TTS model files:\n"
            "Linux: Use 'find ~/ -name \"*freevc24*\"' in terminal\n"
            "Windows: Search for '*freevc24*' in File Explorer\n"
            "macOS: Use 'find ~ -name \"*freevc24*\"' in terminal"
        )
        layout.addWidget(instructions)

        # Path input
        path_layout = QHBoxLayout()
        self.path_input = QLineEdit()
        path_layout.addWidget(self.path_input)
        add_button = QPushButton("Add Path")
        add_button.clicked.connect(self.add_path)
        path_layout.addWidget(add_button)
        layout.addLayout(path_layout)

        # Path list
        self.path_list = QListWidget()
        self.update_path_list()
        layout.addWidget(self.path_list)

        # Remove path button
        remove_button = QPushButton("Remove Selected Path")
        remove_button.clicked.connect(self.remove_path)
        layout.addWidget(remove_button)

        self.setLayout(layout)
        self.setWindowTitle("TTS Settings")

    def add_path(self):
        path = self.path_input.text().strip()
        if path:
            self.settings_manager.add_model_path(path)
            self.update_path_list()
            self.path_input.clear()

    def remove_path(self):
        selected_items = self.path_list.selectedItems()
        if selected_items:
            path = selected_items[0].text()
            self.settings_manager.remove_model_path(path)
            self.update_path_list()

    def update_path_list(self):
        self.path_list.clear()
        for path in self.settings_manager.get_model_paths():
            self.path_list.addItem(path)