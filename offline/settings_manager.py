import os
import json

class SettingsManager:
    def __init__(self, settings_file='tts_settings.json'):
        self.settings_file = settings_file
        self.settings = self.load_settings()

    def load_settings(self):
        if os.path.exists(self.settings_file):
            with open(self.settings_file, 'r') as f:
                return json.load(f)
        return {'model_paths': []}

    def save_settings(self):
        with open(self.settings_file, 'w') as f:
            json.dump(self.settings, f)

    def add_model_path(self, path):
        if path not in self.settings['model_paths']:
            self.settings['model_paths'].append(path)
            self.save_settings()

    def remove_model_path(self, path):
        if path in self.settings['model_paths']:
            self.settings['model_paths'].remove(path)
            self.save_settings()

    def get_model_paths(self):
        return self.settings['model_paths']