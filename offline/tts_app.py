import os
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QTextEdit, QPushButton, QLabel, 
                             QMessageBox, QComboBox, QHBoxLayout, QFileDialog, QProgressBar)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from TTS.api import TTS
from pydub import AudioSegment
from pydub.playback import play
from settings_manager import SettingsManager
from settings_dialog import SettingsDialog

class ModelDownloader(QThread):
    progress = pyqtSignal(int)
    completed = pyqtSignal(bool, str)

    def __init__(self, model_name):
        super().__init__()
        self.model_name = model_name

    def run(self):
        try:
            TTS(model_name=self.model_name)
            self.completed.emit(True, "")
        except Exception as e:
            self.completed.emit(False, str(e))

class TTSApp(QWidget):
    def __init__(self):
        super().__init__()
        self.settings_manager = SettingsManager()
        self.progress = 0
        self.models = self.get_available_models()
        self.current_model = None
        self.model_downloads = {model: False for model in self.models.values()}
        self.initUI()

    def get_available_models(self):
        available_models = {}
        tts_instance = TTS()
        model_manager = tts_instance.list_models()
        model_names = model_manager.list_models()
        
        for model_name in model_names:
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
        
        return available_models

    def initUI(self):
        layout = QVBoxLayout()

        model_layout = QHBoxLayout()
        self.modelCombo = QComboBox()
        self.modelCombo.addItems(self.models.keys())
        self.modelCombo.currentIndexChanged.connect(self.onModelChange)
        model_layout.addWidget(QLabel("Select Voice:"))
        model_layout.addWidget(self.modelCombo)
        layout.addLayout(model_layout)

        self.downloadButton = QPushButton('Download')
        self.downloadButton.clicked.connect(self.downloadModel)
        layout.addWidget(self.downloadButton)

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

        self.progressBar = QProgressBar()
        self.progressBar.setValue(0)
        self.progressBar.setVisible(False)
        layout.addWidget(self.progressBar)

        self.statusLabel = QLabel()
        layout.addWidget(self.statusLabel)

        self.settings_button = QPushButton('Settings')
        self.settings_button.clicked.connect(self.open_settings)
        layout.addWidget(self.settings_button)

        self.setLayout(layout)
        self.setGeometry(300, 300, 400, 400)
        self.setWindowTitle('TTS Application')

    def onModelChange(self):
        model_key = self.modelCombo.currentText()
        model_name = self.models[model_key]
        if self.model_downloads[model_name]:
            self.downloadButton.setVisible(False)
        else:
            self.downloadButton.setVisible(True)
        self.update()

    def downloadModel(self):
        model_key = self.modelCombo.currentText()
        model_name = self.models[model_key]

        self.downloadThread = ModelDownloader(model_name)
        self.downloadThread.progress.connect(self.updateDownloadProgress)
        self.downloadThread.completed.connect(self.onDownloadComplete)
        self.downloadThread.start()

        self.downloadButton.setVisible(False)
        self.progressBar.setVisible(True)
        self.statusLabel.setText("Downloading model...")

    def updateDownloadProgress(self, value):
        self.progressBar.setValue(value)
        self.update()

    def onDownloadComplete(self, success, message):
        self.progressBar.setVisible(False)
        self.downloadButton.setVisible(False)

        if success:
            model_key = self.modelCombo.currentText()
            model_name = self.models[model_key]
            self.model_downloads[model_name] = True
            self.statusLabel.setText("Model downloaded successfully.")
        else:
            self.statusLabel.setText(f"Download failed: {message}")
        self.update()

    def loadModel(self):
        model_key = self.modelCombo.currentText()
        model_name = self.models[model_key]
        if self.current_model != model_name:
            try:
                self.current_model = model_name
                model_path = self.find_model_path(model_name)
                if model_path:
                    self.tts = TTS(model_path=model_path)
                else:
                    self.tts = TTS(model_name=model_name)
                self.showStatusMessage(f"Loaded model: {model_key}")
            except Exception as e:
                self.showErrorMessage("Model Loading Error", f"Failed to load model: {str(e)}")
                self.current_model = None

    def find_model_path(self, model_name):
        for path in self.settings_manager.get_model_paths():
            potential_path = os.path.join(path, model_name)
            if os.path.exists(potential_path):
                return potential_path
        return None

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
                save_path, _ = QFileDialog.getSaveFileName(self, "Save Audio", "", "Audio Files (*.wav)")
                if save_path:
                    self.tts.tts_to_file(text=text, file_path=save_path)
                    self.showStatusMessage(f"Audio saved successfully to {save_path}")
            except Exception as e:
                self.showErrorMessage("Error", f"An error occurred: {str(e)}")

    def showErrorMessage(self, title, message):
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Icon.Warning)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        msg_box.exec()

    def showStatusMessage(self, message):
        self.statusLabel.setText(message)

    def open_settings(self):
        settings_dialog = SettingsDialog(self.settings_manager, self)
        settings_dialog.exec()