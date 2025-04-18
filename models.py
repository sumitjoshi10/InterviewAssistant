import speech_recognition as sr
import sounddevice as sd
import soundfile as sf
import numpy as np
import tempfile
import threading
import os
import whisper
import torch

class MicrophoneAccess:
    def __init__(self):
        self.fs = 16000  # Sample rate
        self.recording = False
        self.audio_data = []
        self.model = whisper.load_model("base")

    def _record_audio(self):
        """ Record audio from the microphone stream. """
        def callback(indata, frames, time, status):
            if self.recording:
                self.audio_data.append(indata.copy())

        with sd.InputStream(samplerate=self.fs, channels=1, callback=callback):
            while self.recording:
                sd.sleep(100)  # Non-blocking sleep to allow smooth recording

    def start_stream(self):
        """ Start the audio stream. """
        self.audio_data = []
        self.recording = True
        threading.Thread(target=self._record_audio, daemon=True).start()

    def stop_stream_and_transcribe(self):
        """ Stop the stream, save the audio, and transcribed. """
        self.recording = False
        audio = np.concatenate(self.audio_data, axis=0)

        # Save audio to a temporary .wav file
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_wav:
            temp_path = temp_wav.name
            sf.write(temp_path, audio, self.fs, format='WAV')  # write proper PCM WAV

        recognizer = sr.Recognizer()
        try:
            
            with sr.AudioFile(temp_path) as source:
                recorded_audio = recognizer.record(source)
                text = recognizer.recognize_google(recorded_audio)
        except sr.UnknownValueError:
            text = "[Could not understand audio]"
        except sr.RequestError as e:
            text = f"[Google error: {e}]"
       
        finally:
            # Clean up by deleting the temp file
            if os.path.exists(temp_path):
                os.remove(temp_path)

        return text