import pygame
from midi_processor import load_midi_file, parse_midi, convert_midi_to_mid
from visualizer import draw_notes, calculate_piano_y_position, calculate_note_falling_duration, Piano, keys
from audio_player import play_audio, load_audio, midi_to_audio
import time
from utils import resize_objects

def main():
    # Initialize
    pygame.init()
    screen_width = 800
    aspect_ratio = 9 / 16
    screen_height = 600
    new_screen_width, new_screen_height = 800, 600
    old_screen_width, old_screen_height = 800, 600
    screen = pygame.display.set_mode((screen_width, screen_height), pygame.RESIZABLE)
    clock = pygame.time.Clock()
    speed = 200
    audioHasPlayed = False
    
    # Load MIDI and Audio files
    piano = Piano(screen, screen_width, screen_height)
    midi_file_path = 'assets/Memoria.mid'
    midi_file = load_midi_file(midi_file_path)
    notes = parse_midi(midi_file)  
    audio_file = "assets/Memoria.mp3"
    load_audio(audio_file)

    
    

    # Main loop
    start_time = time.time()
    current_time = 0
    running = True
    paused = False

    while running:
        
        clock.tick(60) 
        current_time = time.time() - start_time  
    
        
        
        
        for event in pygame.event.get():
            
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.VIDEORESIZE:
          
                old_screen_width, old_screen_height = new_screen_width, new_screen_height
                new_screen_width = event.w
                new_screen_height = event.h
                screen = pygame.display.set_mode((new_screen_width, new_screen_height), pygame.RESIZABLE)

                for key in keys:
                     resize_objects(key, old_screen_width, old_screen_height, new_screen_width, new_screen_height)
                
                for note in notes:
                    resize_objects(note, old_screen_width, old_screen_height, new_screen_width, new_screen_height)
                    note.glow_images =  note.create_glow_images(note.glow_color, note.glow_size, note.width, note.height, note.border_radius)
                    
                


                screen.fill((0, 0, 0))
                piano.draw_piano()
                draw_notes(notes, current_time, speed, screen, new_screen_width, old_screen_height, new_screen_height)

                pygame.display.flip()
                clock.tick(60)
          
                
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:
                    paused = not paused
              
                    
        if not paused:
           

            screen.fill((0, 0, 0))
  
            
            draw_notes(notes, current_time, speed, screen, new_screen_width, old_screen_height, new_screen_height)
            piano.draw_piano()

            if current_time >= 1:
                from visualizer import first_note_object 
                                                                # offset: higher value means earlier playback
                if first_note_object.y_position + first_note_object.height + 10 > calculate_piano_y_position(new_screen_height) and not audioHasPlayed:
                    play_audio()
                    audioHasPlayed = True
                else:
                    pass
            
            pygame.display.flip()
           
           # print(f"FPS: {clock.get_fps()}")
          
            
           
        elif paused:
         
            '''needs to stop audio'''
            clock.tick(0)
       

    pygame.quit()

if __name__ == "__main__":
    main()


