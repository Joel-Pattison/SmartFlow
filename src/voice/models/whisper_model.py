import torch
import whisper
import numpy as np
import io
import wave

class Whisper:
    def __init__(self, model_name):
        self.model = None
        self.model_name = model_name

    def recognize(self, audio_frames):
        wav_writer = wave.open("tmp.wav", 'wb')
        wav_writer.setnchannels(1)
        wav_writer.setsampwidth(2)
        wav_writer.setframerate(44100)
        wav_writer.writeframes(b''.join(audio_frames))
        wav_writer.close()

        # with wave.open("tmp.wav") as wf:
        #     n_frames = wf.getnframes()
        #     frame_data = wf.readframes(n_frames)
        #     audio_data = np.frombuffer(frame_data, dtype=np.int16).astype(np.float32) / 32768.0

        result = self.model.transcribe("tmp.wav")
        return result["text"]


    def load_model(self):
        self.model = whisper.load_model(self.model_name, device="cuda")

    def unload_model(self):
        self.model = None
        torch.cuda.empty_cache()
