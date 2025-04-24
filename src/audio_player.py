import pygame


def load_audio(audio_file):
    
    pygame.mixer.init()
    pygame.mixer.music.load(audio_file)
 
    
def play_audio(pos):
    
    pygame.mixer.music.play()
    pygame.mixer.music.set_pos(pos)

def pause_audio():
    pygame.mixer.music.pause()
    
def resume_audio():
    pygame.mixer.music.unpause()
  


  


    




