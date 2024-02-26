import pyaudio
import threading
from pynput import keyboard
import speech_recognition as sr
import time


class Voice:
    def __init__(self, settings_manager, llm_conversation, voice_models):
        self.voice_models = voice_models
        self.llm_conversation = llm_conversation
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
                print("Recording started with microphone: " + self.settings_manager.get_microphone_name())
        except AttributeError:
            pass

    def disable_recording(self):
        if self.recording:
            self.recording = False
            print("Recording stopped, processing...")
            return False

    def start_recording(self):
        mic_index = self.settings_manager.get_microphone_index()

        self.RATE = self.voice_models[self.settings_manager.get_voice_model()].get_sample_rate()

        stream = self.audio_interface.open(format=self.FORMAT, channels=self.CHANNELS,
                                           rate=self.RATE, input=True, frames_per_buffer=self.CHUNK,
                                           input_device_index=mic_index)
        self.frames = []

        while self.recording:
            data = stream.read(self.CHUNK, exception_on_overflow=False)
            self.frames.append(data)

        self.process_audio()

        stream.stop_stream()
        stream.close()

    def process_audio(self):
        start_time = time.time()
        text = self.voice_models[self.settings_manager.get_voice_model()].recognize(self.frames)
        end_time = time.time()
        print(f"Completed recognition, Time to process audio: {end_time - start_time}")
        print(f"Text: {text}")
        self.llm_conversation.run_conversation(text)
