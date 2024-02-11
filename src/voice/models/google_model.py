import speech_recognition as sr


class Google:
    def __init__(self):
        self.recognizer = sr.Recognizer()

    def recognize(self, audio_frames):
        try:
            audio_data = sr.AudioData(b''.join(audio_frames), 44100, 2)
            text = self.recognizer.recognize_google(audio_data)
            return text
        except sr.UnknownValueError:
            return "Google Speech Recognition could not understand audio"
        except sr.RequestError:
            return "Could not request results from Google Speech Recognition service"
        except Exception as e:
            return f"An error occurred: {e}"

    def load_model(self):
        pass

    def unload_model(self):
        pass