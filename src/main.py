import pygame
from midi_processor import load_midi_file, parse_midi
from visualizer import draw_notes, Piano, keys, visible_notes
from audio_player import play_audio, load_audio, pause_audio, resume_audio
from video_processor import Video
from utils import resize_objects
from UI import Button, InputBox, SeekBar
import time as Time


import moderngl
import moderngl_window as mglw
from moderngl_window import geometry
import numpy as np
from visualizer import Visualizer, Rect


class VisualizerApp(mglw.WindowConfig):
    gl_version = (3, 3)
    title = "Visualizer"
    window_size = (1920, 1080)
    aspect_ratio = 16 / 9
    resizable = True
    resource_dir = 'ModernGL shaders'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.wnd.resize(1920, 1080)
        self.title_bar_height = 32
        self.ctx.enable(moderngl.BLEND)
        self.ctx.enable(moderngl.PROGRAM_POINT_SIZE)
      

        self.ctx.blend_func = (moderngl.SRC_ALPHA, moderngl.ONE_MINUS_SRC_ALPHA)

        
     

        self.color = (45, 43, 135)
        self.audio_has_played = False
        self.video_started = False
        self.video_start_time = 0
        self.current_time = 0
        self.speed = 100
        self.paused = False

        # TODO: Piano, Video, InputBox, Button, SeekBar sınıfları modernGL uyumlu hale getirilmeli
        self.screen_quad = geometry.quad_fs()
        self.prog = self.load_program(
            vertex_shader='rect.vert',
            fragment_shader='rect.frag'
        )
        self.prog['u_resolution'].value = tuple(self.window_size)
        vertices = np.array([
            0.0, 0.0,
            1.0, 0.0,
            0.0, 1.0,
            1.0, 1.0,
        ], dtype='f4')
        self.vbo = self.ctx.buffer(vertices.tobytes())
        self.vao = self.ctx.simple_vertex_array(self.prog, self.vbo, 'in_position')

        width, height = self.wnd.buffer_size
        self.resize(width, height)

        self.visualizer = Visualizer(self.visualizer_x, self.visualizer_y, self.visualizer_width, self.visualizer_height, self.ctx, self.color)
        self.midi_file_path = 'assets/general/TSFH- Heart of Courage.mid'
        self.midi_file = load_midi_file(self.midi_file_path)
        self.notes = parse_midi(self.midi_file)  

        self._last_time = 0
        self._fps = 0
        self._accumulator = 0
     

    def resize(self, width: int, height: int):
        width, height = self.wnd.buffer_size 
        print("RESIZED ####################################################################")
        print(f"resize() called with: {width=} {height=}")
        print(f"self.wnd.buffer_size: {self.wnd.buffer_size}")
        print(f"self.wnd.window_size: {self.wnd.size}")
        # Gerçek zamanlı pencere boyutu
        self.new_screen_width = width
        self.new_screen_height = height

        # UI boyutları
        self.ui_width = width * 0.25
        self.ui_height = height

        # Visualizer boyut ve konum
        self.visualizer_width = self.new_screen_width * 0.75
        self.visualizer_height = min(self.new_screen_height, self.visualizer_width / self.aspect_ratio)

        self.visualizer_x = self.ui_width
        self.visualizer_y = round((self.new_screen_height - self.visualizer_height) / 2) + 40
 

        self.visualizer_rect = {
            "x": self.visualizer_x,
            "y": self.visualizer_y,
            "width": self.visualizer_width,
            "height": self.visualizer_height,
        }
        top_margin = self.visualizer_y
        bottom_margin = self.new_screen_height - (self.visualizer_y + self.visualizer_height)
        print(f"Top margin: {top_margin}")
        print(f"Bottom margin: {bottom_margin}")
  
      

    def key_event(self, key, action, modifiers):
        if action == self.wnd.keys.ACTION_PRESS:
            if key == self.wnd.keys.P:
                self.paused = not self.paused
                # TODO: pause/resume audio/video
            elif key == self.wnd.keys.RETURN:
                # TODO: Input değerlerini güncelle
                pass

    def on_render(self, time: float, frame_time: float):
        
        now = Time.time()
        self.ctx.viewport = (0, 0, self.new_screen_width, self.new_screen_height)
        
        if not self.paused:
            self.ctx.screen.use()
            self.ctx.clear(0.0, 0.0, 0.0, 1.0)
            self.prog["u_resolution"].value = (self.new_screen_width, self.new_screen_height)
            self.current_time += frame_time

            # TODO: UI çerçevesi ve video frame render işlemleri
            # self.screen_quad.render()

            # TODO: draw_notes, piano.draw, input.draw, button.draw, seek_bar.draw

            # TODO: video.get_frame() sonucu texture olarak render edilmelidir

            # UI Panel (sol tarafta)
            self.prog['u_position'].value = (0.0, 0.0)
            self.prog['u_size'].value = (self.ui_width, self.ui_height)
            self.prog['u_color'].value = (0.2, 0.2, 0.2)
            self.vao.render(mode=moderngl.TRIANGLE_STRIP)

            # Visualizer Panel (sağda)
            self.prog['u_position'].value = (self.visualizer_x, self.visualizer_y)
            self.prog['u_size'].value = (self.visualizer_width, self.visualizer_height)
            self.prog['u_color'].value = (0.0, 0.0, 0.0)
            self.vao.render(mode=moderngl.TRIANGLE_STRIP)


            draw_notes(self.notes, self.current_time, self.speed, Rect(0, 0, self.new_screen_width, self.new_screen_height),
            self.color, self.visualizer.rect, 0.016, self.prog, self.vao, self.ctx, self.visualizer)
            self.visualizer.render(self.prog, self.vao, frame_time)
            print(frame_time)

           
            dt = now - self._last_time
            # Ortalama FPS hesaplamak için
            self._fps = 0.9*self._fps + 0.1*(1.0/dt)  
            self._last_time = now

            # Yarım saniyede bir yazdır
            self._accumulator += dt
            if self._accumulator >= 0.0:
                # print(f"FPS: {self._fps:.1f}")
                self._accumulator = 0.0
                    

    def close(self):
        # TODO: kaynakları serbest bırak
        pass


if __name__ == '__main__':
    mglw.run_window_config(VisualizerApp)



# PYGAME OLD


# def main():
#     pygame.init()
#     base_screen_width = 800
#     base_screen_height = 600
#     new_screen_width, new_screen_height = base_screen_width, base_screen_height
#     old_screen_width, old_screen_height = base_screen_width, base_screen_height

#     aspect_ratio = 16 / 9
#     ui_width = base_screen_width * 0.25
#     ui_height = base_screen_height
#     visualizer_width = base_screen_width - ui_width
#     visualizer_height = min(base_screen_height, visualizer_width / aspect_ratio)
#     visualizer_x = ui_width
#     visualizer_y = (base_screen_height - visualizer_height) / 2
#     visualizer_rect = pygame.Rect(visualizer_x, visualizer_y, visualizer_width, visualizer_height)



#     screen = pygame.display.set_mode((base_screen_width, base_screen_height), pygame.RESIZABLE)
#     clock = pygame.time.Clock()
#     speed = 100
    

#     color = (70, 72, 220)
#     audio_has_played = False
#     video_started = False
    
#     # Load MIDI and Audio files
#     piano = Piano(screen, visualizer_rect)
#     midi_file_path = 'assets/video test stuff/Recording 03-22 21.33.35.mid'
#     midi_file = load_midi_file(midi_file_path)
#     notes = parse_midi(midi_file)  
#     audio_file = "assets/video test stuff/a.wav"
#     load_audio(audio_file)

#     # VIDEO
#     video_start_time = 0
#     video_file_path = "assets/video test stuff/PXL_20250322_212655211.mp4"
#     video = Video(video_file_path, screen, visualizer_rect, video_start_time)
#     video.duration -= video_start_time
#     frame_count = 0

#     # Main loop
#     current_time = 0
#     running = True
#     paused = False

#     # UI elements 
#     font = pygame.font.SysFont(None, 24)
#     color_input = InputBox(30, 30, 150, 30, f"{color[0]}, {color[1]}, {color[2]}")
#     video_rotation_input = InputBox(30, 70, 150, 30, "")
#     video_scaling_input = InputBox(30, 110, 150, 30, "")
#     video_brightness_input = InputBox(30, 150, 150, 30, "")
    
#     inputs = [color_input, video_rotation_input, video_scaling_input, video_brightness_input]



#     video_forward_button = Button((30, 300, 150, 30), (0, 0, 0), "Forward", font, video.forward, 10)
#     buttons = [video_forward_button]
#     video_position_seek_bar = SeekBar(30, 400, ui_width - 30, 10, video.duration, video.rewind)
#     seek_bars = [video_position_seek_bar]

#     while running:
        
#         delta_time = clock.tick(90) / 1000

#         for event in pygame.event.get():
#             if event.type == pygame.QUIT:
#                 running = False

#             elif event.type == pygame.VIDEORESIZE:
  
#                 old_screen_width, old_screen_height = new_screen_width, new_screen_height
#                 new_screen_width, new_screen_height = event.w, event.h
#                 old_visualizer_rect = visualizer_rect
#                 screen = pygame.display.set_mode((new_screen_width, new_screen_height), pygame.RESIZABLE)

#                 ui_width = new_screen_width * 0.25
#                 ui_height = new_screen_height
#                 visualizer_width = new_screen_width - ui_width
#                 visualizer_height = min(new_screen_height, visualizer_width / aspect_ratio)
#                 visualizer_x = ui_width
#                 visualizer_y = (new_screen_height - visualizer_height) // 2
#                 visualizer_rect = pygame.Rect(visualizer_x, visualizer_y, visualizer_width, visualizer_height) 
                
              

#                 for key in keys:
#                     resize_objects(key, old_screen_width, old_screen_height, new_screen_width, new_screen_height, visualizer_rect, old_visualizer_rect, True)
#                 for note in visible_notes:
                    
#                     resize_objects(note, old_screen_width, old_screen_height, new_screen_width, new_screen_height, visualizer_rect, old_visualizer_rect, True)
#                     note.max_glow_layers = round(20 * (visualizer_rect.height / 337.5))
#                     note.note_image = note.create_radial_glow_surface(note.width, note.height, note.color, note.max_glow_layers, note.glow_intensity, note.blend_power)
                   
#                     for particle in note.particles:
                   
#                         resize_objects(particle, old_screen_width, old_screen_height, new_screen_width, new_screen_height, visualizer_rect, old_visualizer_rect, True)


#                 resize_objects(video, old_screen_width, old_screen_height, new_screen_width, new_screen_height, visualizer_rect, old_visualizer_rect, True)
           
#                 print("RESIZED ###################################################################################################################")
                    

#             elif event.type == pygame.KEYDOWN:
#                 if event.key == pygame.K_p:
#                     paused = not paused
#                     if paused:
#                         pause_audio()
#                         video.pause()
#                     else:
#                         resume_audio()
#                         video.play()

#                 if event.key == pygame.K_RETURN:
#                     color = color_input.get_value("tuple")
#                     video.rotation_angle = float(video_rotation_input.get_value("number"))
#                     video.scale_factor = float(video_scaling_input.get_value("number"))
#                     video.brightness = float(video_brightness_input.get_value("number"))
                    


#             for input in inputs:
#                 input.handle_event(event)
#             for button in buttons:
#                 button.handle_event(event)
#             for seek_bar in seek_bars:
#                 seek_bar.handle_event(event)

#         if not paused:
           
#             current_time += delta_time
#             screen.fill((0, 0, 0))

#             #UI
#             ui_surface = pygame.Surface((ui_width, ui_height), pygame.SRCALPHA)
#             ui_surface.fill((50, 50, 50, 200))
#             screen.blit(ui_surface, (0, 0))

#             # visualizer
#             clip_rect = pygame.Rect(visualizer_x, visualizer_y, visualizer_width, keys[0].y_position + keys[0].height - visualizer_y)
#             screen.set_clip(clip_rect)
    
#             pygame.draw.rect(screen, (0, 0, 0), visualizer_rect) 
#             draw_notes(notes, current_time, speed, screen, visualizer_width, old_screen_height, visualizer_height, color, visualizer_rect, delta_time)
#             piano.draw_piano()
#             screen.set_clip(None)

#             #VIDEO
#             if not video_started:
#                 video.play()
#                 video_started = True

#             frame_surf = video.get_frame()
#             if frame_surf:
                
#                 # visualize_rect içinde temizlemeyi main loop yapıyor
#                 screen.set_clip(visualizer_rect)
#                 screen.blit(frame_surf, (visualizer_rect.x + video.x_offset,
#                                         keys[0].y_position))
#                 screen.set_clip(None)
            

 
         

#             from visualizer import first_note_object
#             if first_note_object is not None:
            
#                 note_travel_distance = keys[0].y_position - visualizer_rect.y
#                 speed_px_per_sec = (visualizer_rect.height / 337.5) * speed
#                 hit_time = first_note_object.start_time + note_travel_distance / speed_px_per_sec

#                 if not audio_has_played and current_time + 100 >= hit_time:
              
#                     exceeded_time = current_time - hit_time
#                     play_audio(exceeded_time + first_note_object.start_time + 0.25)
#                     audio_has_played = True  
                 

#             for input in inputs:
#                 input.draw(screen)
#             for button in buttons:
#                 button.draw(screen)
#             for seek_bar in seek_bars:
#                 seek_bar.draw(screen, current_time - video_start_time)
#             pygame.display.flip()
#             #print(clock.get_fps())


       

#     pygame.quit()

  

# if __name__ == "__main__":
#     main()


