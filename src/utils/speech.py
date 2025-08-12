import pyttsx3
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

engine = None

def init_engine():
    global engine
    try:
        engine = pyttsx3.init()
    except Exception as e:
        logger.error(f"Failed to initialize pyttsx3 engine: {e}")

def speak(text, volume=0.5, mute=False):
    global engine
    if engine is None:
        init_engine()

    if engine and not mute:
        try:
            engine.setProperty('volume', volume)
            engine.say(text)
            engine.runAndWait()
        except Exception as e:
            logger.error(f"Failed to speak: {e}")

def get_piece_name(char):
    pieces = {
        'p': 'Pawn', 'r': 'Rook', 'n': 'Knight', 'b': 'Bishop', 'q': 'Queen', 'k': 'King',
        'P': 'Pawn', 'R': 'Rook', 'N': 'Knight', 'B': 'Bishop', 'Q': 'Queen', 'K': 'King'
    }
    return pieces.get(char, '')

if __name__ == '__main__':
    speak("Hello, this is a test of the speech support.", volume=0.8)
    speak("Move Knight from G1 to F3", volume=0.5)
