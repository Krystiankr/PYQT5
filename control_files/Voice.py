import pyttsx3


class voice_speech:
    def __init__(self):
        self.engine = pyttsx3.init()
        rate = self.engine.getProperty('rate')
        voices = self.engine.getProperty('voices')
        self.engine.setProperty('voice', voices[1].id)
        self.engine.setProperty('rate', rate - 70)

    def text(self, text):
        self.engine.say(text)
        self.engine.runAndWait()