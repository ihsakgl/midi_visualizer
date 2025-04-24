import pygame
from midi_processor import load_midi_file, parse_midi
from visualizer import draw_notes, Piano, keys, visible_notes
from audio_player import play_audio, load_audio, pause_audio, resume_audio
from video_processor import Video
from utils import resize_objects
from UI import Button, InputBox


def main():
    # Initialize
    pygame.init()
   
    base_screen_width = 800
    base_screen_height = 600
    new_screen_width, new_screen_height = base_screen_width, base_screen_height
    old_screen_width, old_screen_height = base_screen_width, base_screen_height

    aspect_ratio = 16 / 9
    ui_width = base_screen_width * 0.25
    ui_height = base_screen_height
    visualizer_width = base_screen_width - ui_width
    visualizer_height = min(base_screen_height, visualizer_width / aspect_ratio)
    visualizer_x = ui_width
    visualizer_y = (base_screen_height - visualizer_height) / 2
    visualizer_rect = pygame.Rect(visualizer_x, visualizer_y, visualizer_width, visualizer_height)



    screen = pygame.display.set_mode((base_screen_width, base_screen_height), pygame.RESIZABLE)
    clock = pygame.time.Clock()
    speed = 100
    

    color = (70, 72, 220)
    audio_has_played = False
    video_started = False
    
    
    # Load MIDI and Audio files
    piano = Piano(screen, visualizer_rect)
    midi_file_path = 'assets/video test stuff/Recording 03-22 21.33.35.mid'
    midi_file = load_midi_file(midi_file_path)
    notes = parse_midi(midi_file)  
    audio_file = "assets/video test stuff/a.wav"
    load_audio(audio_file)

    # VIDEO
    video_file_path = "assets/video test stuff/PXL_20250322_212655211.mp4"
    video = Video(video_file_path, screen, visualizer_rect)
    frame_count = 0
    


    # Main loop
    current_time = 0
    running = True
    paused = False

   

    # UI elements 
    font = pygame.font.SysFont(None, 24)
    color_input = InputBox(30, 30, 150, 30, f"{color[0]}, {color[1]}, {color[2]}")
    video_rotation_input = InputBox(30, 70, 150, 30, "")
    video_scaling_input = InputBox(30, 100, 150, 30, "")
    
    inputs = [color_input, video_rotation_input, video_scaling_input]
    while running:
        
        delta_time = clock.tick(60) / 1000

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.VIDEORESIZE:
  
                old_screen_width, old_screen_height = new_screen_width, new_screen_height
                new_screen_width, new_screen_height = event.w, event.h
                old_visualizer_rect = visualizer_rect
                screen = pygame.display.set_mode((new_screen_width, new_screen_height), pygame.RESIZABLE)

                ui_width = new_screen_width * 0.25
                ui_height = new_screen_height
                visualizer_width = new_screen_width - ui_width
                visualizer_height = min(new_screen_height, visualizer_width / aspect_ratio)
                visualizer_x = ui_width
                visualizer_y = (new_screen_height - visualizer_height) // 2
                visualizer_rect = pygame.Rect(visualizer_x, visualizer_y, visualizer_width, visualizer_height) 
                
              

                for key in keys:
                    resize_objects(key, old_screen_width, old_screen_height, new_screen_width, new_screen_height, visualizer_rect, old_visualizer_rect, True)
                
             
                    
                for note in visible_notes:
                    
                    resize_objects(note, old_screen_width, old_screen_height, new_screen_width, new_screen_height, visualizer_rect, old_visualizer_rect, True)
                    note.max_glow_layers = round(20 * (visualizer_rect.height / 337.5))
                    note.note_image = note.create_radial_glow_surface(note.width, note.height, note.color, note.max_glow_layers, note.glow_intensity, note.blend_power)
                   
                    for particle in note.particles:
                   
                        resize_objects(particle, old_screen_width, old_screen_height, new_screen_width, new_screen_height, visualizer_rect, old_visualizer_rect, True)


                resize_objects(video, old_screen_width, old_screen_height, new_screen_width, new_screen_height, visualizer_rect, old_visualizer_rect, True)
           
           
                    

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:
                    paused = not paused
                    if paused:
                        pause_audio()
                   
                    else:
                        resume_audio()

                #if event.key == pygame.K_RETURN:
                    # color = color_input.get_value("tuple")
                    # video.rotation_angle = float(video_rotation_input.get_value("number"))
                    # video.scale_factor = float(video_scaling_input.get_value("number"))

            for input in inputs:
                input.handle_event(event)

        if not paused:
           
            current_time += delta_time
            screen.fill((0, 0, 0))

            #UI
            ui_surface = pygame.Surface((ui_width, ui_height), pygame.SRCALPHA)
            ui_surface.fill((50, 50, 50, 200))
            screen.blit(ui_surface, (0, 0))

            # visualizer
            clip_rect = pygame.Rect(visualizer_x, visualizer_y, visualizer_width, keys[0].y_position + keys[0].height - visualizer_y)
            screen.set_clip(clip_rect)
    
            pygame.draw.rect(screen, (0, 0, 0), visualizer_rect) 
            draw_notes(notes, current_time, speed, screen, visualizer_width, old_screen_height, visualizer_height, color, visualizer_rect, delta_time)
            piano.draw_piano()
            screen.set_clip(None)

            #VIDEO
            if not video_started:
                video.play()
                video_started = True
            video.update()
            frame_count += 1
            if frame_count >= 60: #print every 60 frames
              #  print(f"Dropped Frames: {video.dropped_frames}")
                frame_count = 0
                video.dropped_frames = 0 #reset dropped frames

          #  print(video.video_fps)
         

            from visualizer import first_note_object
            if first_note_object is not None:
            
                note_travel_distance = keys[0].y_position - visualizer_rect.y
                speed_px_per_sec = (visualizer_rect.height / 337.5) * speed
                hit_time = first_note_object.start_time + note_travel_distance / speed_px_per_sec

                if not audio_has_played and current_time + 100 >= hit_time:
              
                    exceeded_time = current_time - hit_time
                    play_audio(exceeded_time + first_note_object.start_time + 0.25)
                    audio_has_played = True  
                 

            for input in inputs:
                input.draw(screen)
            pygame.display.flip()
          #  print(clock.get_fps())


       

    pygame.quit()
    video.video_capture.release()
  

if __name__ == "__main__":
    main()


