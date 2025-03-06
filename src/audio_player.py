import pygame
from midi2audio import FluidSynth

def load_audio(audio_file):
    
    pygame.mixer.init()
    pygame.mixer.music.load(audio_file)
 
    
def play_audio():
   
    pygame.mixer.music.play()
    
  

def midi_to_audio(midi_file_path, output_audio_path, soundfont_path):
    # Create FluidSynth object with the soundfont
    fs = FluidSynth(soundfont_path)

    # Convert the MIDI file to an audio file (WAV)
    fs.midi_to_audio(midi_file_path, output_audio_path)
  


    




