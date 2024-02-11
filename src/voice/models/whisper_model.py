import whisper
class Whisper:
    def __init__(self):
        self.model = whisper.load_model("large-v3", device="cuda")
