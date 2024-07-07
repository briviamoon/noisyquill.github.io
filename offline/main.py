import sys
from PyQt6.QtWidgets import QApplication
from tts_app import TTSApp

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = TTSApp()
    ex.show()
    sys.exit(app.exec())