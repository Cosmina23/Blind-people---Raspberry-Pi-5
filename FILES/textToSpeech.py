import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "1"  # Ascunde mesajul de întâmpinare

from gtts import gTTS
import pygame

def speak_text(text):
    # Creează obiectul gTTS
    tts = gTTS(text=text, lang='ro')

    # Salvează fișierul audio
    tts.save("output.mp3")

    # Inițializează pygame mixer
    pygame.mixer.init()

    # Încarcă și redă fișierul audio
    pygame.mixer.music.load("output.mp3")
    pygame.mixer.music.play()

    # Așteaptă până când fișierul audio este terminat
    while pygame.mixer.music.get_busy():
        continue

