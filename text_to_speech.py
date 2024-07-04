import sys
from PyQt6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QTextEdit, 
                            QPushButton, QLabel, QMessageBox, QComboBox, QHBoxLayout, QProgressDialog)
from PyQt6.QtCore import Qt
from TTS.api import TTS
from pydub import AudioSegment
from pydub.playback import play
import re

class TTSApp(QWidget):
    def __init__(self):
        super().__init__()
        self.progress = QProgressDialog("Loading models...", "Cancel", 0, 100, self)
        self.progress.setWindowModality(Qt.WindowModality.WindowModal)
        self.progress.setAutoClose(True)
        self.progress.setAutoReset(True)
        self.models = self.get_available_models()
        self.current_model = None
        self.initUI()

    def get_available_models(self):
        available_models = {}
        
        tts_instance = TTS()
        model_manager = tts_instance.list_models()
        model_names = model_manager.list_models()
        
        self.progress.setMaximum(len(model_names))
        for i, model_name in enumerate(model_names):
            self.progress.setValue(i)
            if self.progress.wasCanceled():
                break
            
            self.ensureModelDownloaded(model_name)
            
            parts = model_name.split('/')
            if len(parts) >= 3:
                language = parts[1]
                details = parts[2].split('_')
                
                gender = "Unknown"
                age = "Adult"
                
                if "male" in details:
                    gender = "Male"
                elif "female" in details:
                    gender = "Female"
                
                if "child" in details:
                    age = "Child"
                elif "senior" in details or "elder" in details:
                    age = "Senior"
                
                key = f"{age} {gender} ({language.capitalize()})"
                available_models[key] = model_name
        
        self.progress.setValue(len(model_names))
        return available_models

    def ensureModelDownloaded(self, model_name):
        try:
            TTS(model_name=model_name)
        except Exception as e:
            self.showErrorMessage("Model Download Error", f"Failed to download model: {str(e)}")

    def initUI(self):
        layout = QVBoxLayout()

        model_layout = QHBoxLayout()
        self.modelCombo = QComboBox()
        self.modelCombo.addItems(self.models.keys())
        model_layout.addWidget(QLabel("Select Voice:"))
        model_layout.addWidget(self.modelCombo)
        layout.addLayout(model_layout)

        self.previewButton = QPushButton('Preview Voice')
        self.previewButton.clicked.connect(self.previewModel)
        layout.addWidget(self.previewButton)

        self.textEdit = QTextEdit()
        layout.addWidget(self.textEdit)

        self.playButton = QPushButton('Play')
        layout.addWidget(self.playButton)
        self.playButton.clicked.connect(self.playText)

        self.saveButton = QPushButton('Save')
        layout.addWidget(self.saveButton)
        self.saveButton.clicked.connect(self.saveAudio)

        self.statusLabel = QLabel()
        layout.addWidget(self.statusLabel)

        self.setLayout(layout)
        self.setGeometry(300, 300, 400, 400)
        self.setWindowTitle('TTS Application')

    def loadModel(self):
        model_key = self.modelCombo.currentText()
        model_name = self.models[model_key]
        if self.current_model != model_name:
            try:
                self.current_model = model_name
                self.tts = TTS(model_name=model_name)
                self.showStatusMessage(f"Loaded model: {model_key}")
            except Exception as e:
                self.showErrorMessage("Model Loading Error", f"Failed to load model: {str(e)}")
                self.current_model = None

    def previewModel(self):
        self.loadModel()
        if self.current_model:
            preview_text = "This is a preview of the selected voice."
            self.ttsToAudio(preview_text)

    def ttsToAudio(self, text):
        try:
            output_file = "output.wav"
            self.tts.tts_to_file(text=text, file_path=output_file)
            audio = AudioSegment.from_file(output_file)
            play(audio)
        except Exception as e:
            self.showErrorMessage("Error", f"An error occurred: {str(e)}")

    def playText(self):
        self.loadModel()
        if self.current_model:
            text = self.textEdit.toPlainText().strip()
            if not text:
                self.showErrorMessage("Error", "Please enter some text to play.")
                return
            self.ttsToAudio(text)

    def saveAudio(self):
        self.loadModel()
        if self.current_model:
            text = self.textEdit.toPlainText().strip()
            if not text:
                self.showErrorMessage("Error", "Please enter some text to save.")
                return
            
            try:
                from PyQt6.QtWidgets import QFileDialog
                save_path, _ = QFileDialog.getSaveFileName(self, "Save Audio", "", "Audio Files (*.wav)")
                if save_path:
                    self.tts.tts_to_file(text=text, file_path=save_path)
                    self.showStatusMessage(f"Audio saved successfully to {save_path}")
            except Exception as e:
                self.showErrorMessage("Error", f"An error occurred during saving: {str(e)}")

    def showErrorMessage(self, title, message):
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Icon.Warning)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        msg_box.exec()

    def showStatusMessage(self, message):
        self.statusLabel.setText(message)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    try:
        ex = TTSApp()
        ex.show()
        sys.exit(app.exec())
    except Exception as e:
        print(f"An error occurred: {str(e)}")