import pyaudio
import threading
from pynput import keyboard
import speech_recognition as sr


class Voice:
    def __init__(self, settings_manager):
        self.settings_manager = settings_manager
        self.record_thread = None
        self.audio_interface = pyaudio.PyAudio()
        self.FORMAT = pyaudio.paInt16
        self.CHANNELS = 1
        self.RATE = 44100
        self.CHUNK = 1024
        self.recording = False
        self.frames = []

    def enable_recording(self):
        try:
            if not self.recording:
                self.recording = True
                self.record_thread = threading.Thread(target=self.start_recording)
                self.record_thread.start()
                print("Recording started...")
        except AttributeError:
            pass

    def disable_recording(self):
        if self.recording:
            self.recording = False
            self.record_thread.join()
            print("Recording stopped, processing...")
            self.process_audio()
            return False

    def start_recording(self):
        mic_index = self.settings_manager.get_microphone_index()

        stream = self.audio_interface.open(format=self.FORMAT, channels=self.CHANNELS,
                                           rate=self.RATE, input=True, frames_per_buffer=self.CHUNK,
                                           input_device_index=mic_index)
        self.frames = []

        while self.recording:
            data = stream.read(self.CHUNK, exception_on_overflow=False)
            self.frames.append(data)

        stream.stop_stream()
        stream.close()

    def process_audio(self):
        recognizer = sr.Recognizer()
        audio_data = sr.AudioData(b''.join(self.frames), self.RATE, 2)
        try:
            text = recognizer.recognize_google(audio_data)
            print(f"Text: {text}")
        except sr.UnknownValueError:
            print("Google Speech Recognition could not understand audio")
        except sr.RequestError as e:
            print(f"Could not request results from Google Speech Recognition service; {e}")
