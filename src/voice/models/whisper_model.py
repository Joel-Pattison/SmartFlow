import torch
import whisper
import numpy as np

class Whisper:
    def __init__(self, model_name):
        self.model = None
        self.model_name = model_name
        self.sample_rate = 16000

    def recognize(self, audio_frames):
        all_frames_bytes = b''.join(audio_frames)

        audio_data = np.frombuffer(all_frames_bytes, dtype=np.int16).astype(np.float32) / 32768.0

        result = self.model.transcribe(audio_data)
        return result["text"]

    def load_model(self):
        self.model = whisper.load_model(self.model_name, device="cuda")

    def unload_model(self):
        self.model = None
        torch.cuda.empty_cache()

    def get_sample_rate(self):
        return self.sample_rate
