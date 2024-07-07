# Text-to-Speech and Voice-to-Text Application

This project consists of two main applications: a Text-to-Speech (TTS) app and a Voice-to-Text app. These applications provide users with the ability to convert text to speech and vice versa, offering various customization options.

## Features

### Text-to-Speech Application (Offline)

- Multiple voice models support with different languages, genders, and ages
- Model downloading functionality with progress tracking
- Voice preview option
- Text input for conversion to speech
- Play converted speech directly
- Save audio output as WAV files
- Pause, resume, and cancel model downloads

### Voice-to-Text Application (Online)

- Text input for story or content
- Multiple voice options (en, en-au, en-uk, en-us)
- Adjustable speech rate (100-250 words per minute)
- Play converted speech
- Save converted speech as MP3 files
- Progress tracking for conversion process
- Cancel operation functionality

## Requirements

To run these applications, you'll need to install the required Python libraries. You can install them using the following command: ```pip install -r ../offline/requirements.txt```
The `requirements.txt` file includes all necessary libraries for both applications.

## Usage

### Text-to-Speech Application (Offline)

1. Run the `offline/text_to_speech.py` script: ```python3.9 offline/text_to_speech.py```
2. Select a voice model from the dropdown menu
3. Download the model if not already available
4. Enter the text you want to convert to speech
5. Use the "Preview Voice" button to hear a sample
6. Click "Play" to hear the converted speech
7. Use "Save" to store the audio as a WAV file

### Voice-to-Text Application (Online)

1. Run the `online/voice_to_text_app.py` script: ```python online/voice_to_text_app.py```
2. Enter your story or text in the provided text area
3. Select a voice option from the dropdown menu
4. Adjust the speech rate using the slider
5. Enter a file name for saving (optional)
6. Click "Play" to hear the converted speech
7. Click "Convert and Save" to store the audio as an MP3 file

## Note

The Text-to-Speech application works offline once the models are downloaded, while the Voice-to-Text application requires an internet connection to function.

## Contributing

Contributions to improve these applications are welcome. Please feel free to submit pull requests or open issues for any bugs or feature requests.

## Authors

- Brivia Odunga.
