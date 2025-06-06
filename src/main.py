import moderngl
import moderngl_window as mglw
from moderngl_window import geometry
import numpy as np
import time as Time

from visualizer import Visualizer, Rect, draw_notes, keys, visible_notes
from midi_processor import load_midi_file, parse_midi
from audio_player import AudioPlayer
from video_processor import Video
from UI import UI
from utils import resize_objects
import pynvml

class VisualizerApp(mglw.WindowConfig):
    gl_version = (3, 3)
    title = "Visualizer"
    window_size = (1920, 1080)
    aspect_ratio = 16 / 9
    resizable = True
    resource_dir = 'ModernGL shaders'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.base_width, self.base_height = 1920, 1080
        self.base_visualizer_rect = Rect(self.base_width * 0.25, 0, self.base_width * 0.75, min(self.base_height, self.base_width * 0.75 / self.aspect_ratio))
        self.dimenstions_init = False
       
        
        self.title_bar_height = 32
        self.ctx.enable(moderngl.BLEND)
        self.ctx.enable(moderngl.PROGRAM_POINT_SIZE)
      

        self.ctx.blend_func = (moderngl.SRC_ALPHA, moderngl.ONE_MINUS_SRC_ALPHA)
        
        
     

        self.color = (150, 150, 150)
        self.flag1 = False
        self.current_time = 0
        self.speed = 100
        self.paused = False

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
        self.dimenstions_init = False
        self.on_resize(width, height)
        self.dimenstions_init = True


        # MIDI
        self.midi_file_path = 'assets/video/recording.mid'
        self.midi_file = load_midi_file(self.midi_file_path)
        self.notes = parse_midi(self.midi_file)  

    	# VIDEO
        self.video_has_started = False
        self.video_file_path = 'assets/video/video.mp4'
        self.video_start_time = -100.0
        self.video = Video(self.ctx, self.video_file_path, self.visualizer_rect,
                            self.video_start_time)
        
        # UI
        self.visualizer = Visualizer(self.visualizer_x, self.visualizer_y, self.visualizer_width, self.visualizer_height, self.ctx, self.color)
        self.UI = UI(self.ctx, 1920, 1080, self.video, "assets/fonts/arial.ttf")
        

        # AUDIO
        self.audio_player = None
        self.audio_file_path = 'assets/video/a.wav'
        self.audio_player = AudioPlayer(0, self.current_time, 
            self.visualizer_rect, self.speed, keys[0].y, keys[0].height)
        self.audio_player.load_audio(self.audio_file_path)

        self._last_time = 0
        self._fps = 0
        self._accumulator = 0
    
     

    def on_resize(self, width: int, height: int):
       
    
        self.new_screen_width = width
        self.new_screen_height = height

        # UI dimensions: 25% of the width is for the UI
        self.ui_width = width * 0.25
        self.ui_height = height

        # Visualizer dimensions: 75% of the width
        self.visualizer_width = self.new_screen_width * 0.75
        self.visualizer_height = min(self.new_screen_height, self.visualizer_width / self.aspect_ratio)

        self.visualizer_x = self.ui_width
        self.visualizer_y = round((self.new_screen_height - self.visualizer_height) / 2) 
 

     
        self.visualizer_rect = Rect(self.visualizer_x, self.visualizer_y, self.visualizer_width, self.visualizer_height)
  

        if self.dimenstions_init:
            resize_objects(self.visualizer, self.base_width, self.base_height, self.new_screen_width, self.new_screen_height, self.visualizer_rect, self.base_visualizer_rect, True)
            for note in visible_notes:
                resize_objects(note, self.base_width, self.base_height, self.new_screen_width, self.new_screen_height, self.visualizer_rect, self.base_visualizer_rect, True)
            for key in keys:
                resize_objects(key, self.base_width, self.base_height, self.new_screen_width, self.new_screen_height, self.visualizer_rect, self.base_visualizer_rect, True)
            resize_objects(self.UI, self.base_width, self.base_height, self.new_screen_width, self.new_screen_height, self.visualizer_rect, self.base_visualizer_rect, False)
            resize_objects(self.video, self.base_width, self.base_height, self.new_screen_width, self.new_screen_height, self.visualizer_rect, self.base_visualizer_rect, True)
            self.UI.resize(self.new_screen_width, self.new_screen_height)
       

  
      

    def on_key_event(self, key, action, modifiers):
        if action == self.wnd.keys.ACTION_PRESS:
            if key == self.wnd.keys.P:
                self.paused = not self.paused

                self.audio_player.pause_or_resume_audio()

            elif key == self.wnd.keys.SPACE:
                self.video.playing = not self.video.playing
                
            elif key == self.wnd.keys.RIGHT:
                self.video.step_forward()
                 
            elif key == self.wnd.keys.LEFT:
                self.video.step_backward() 
               
       
              
             
                


    def on_mouse_drag_event(self, x, y, dx, dy):
        self.UI.move_event(x, y)


    def on_mouse_press_event(self, x, y, button):
        self.UI.press_event(x, y)

    def on_mouse_release_event(self, x: int, y: int, button: int):
        self.UI.release_event(x, y)
        
    
    def on_render(self, time: float, frame_time: float):
        self.ctx.viewport = (0, 0, self.new_screen_width, self.new_screen_height)
      
     
        if self.paused:
            self.ctx.screen.use()
            self.ctx.clear(0.0, 0.0, 0.0, 1.0)
            self.prog["u_resolution"].value = (self.new_screen_width, self.new_screen_height)

            self.prog['u_position'].value = (0.0, 0.0)
            self.prog['u_size'].value = (self.ui_width, self.ui_height)
            self.prog['u_color'].value = (0.2, 0.2, 0.2)
            self.vao.render(mode=moderngl.TRIANGLE_STRIP)

            self.prog['u_position'].value = (self.visualizer_x, self.visualizer_y)
            self.prog['u_size'].value = (self.visualizer_width, self.visualizer_height)
            self.prog['u_color'].value = (0.1, 0.1, 0.1)
            self.vao.render(mode=moderngl.TRIANGLE_STRIP)

            draw_notes(self.notes, self.current_time, self.speed, Rect(0, 0, self.new_screen_width, self.new_screen_height),
                    self.color, self.visualizer.rect, 0.016, self.prog, self.vao, self.ctx, self.visualizer)
            self.visualizer.render(self.prog, self.vao, 0)  
            self.UI.render()

            if self.current_time > self.video_start_time:
                self.video.render(frame_time)

            # No audio update

        else:
            now = Time.time()
            self.ctx.screen.use()
            self.ctx.clear(0.0, 0.0, 0.0, 1.0)
            self.prog["u_resolution"].value = (self.new_screen_width, self.new_screen_height)

            self.current_time += frame_time

            self.prog['u_position'].value = (0.0, 0.0)
            self.prog['u_size'].value = (self.ui_width, self.ui_height)
            self.prog['u_color'].value = (0.2, 0.2, 0.2)
            self.vao.render(mode=moderngl.TRIANGLE_STRIP)

            self.prog['u_position'].value = (self.visualizer_x, self.visualizer_y)
            self.prog['u_size'].value = (self.visualizer_width, self.visualizer_height)
            self.prog['u_color'].value = (0.1, 0.1, 0.1)
            self.vao.render(mode=moderngl.TRIANGLE_STRIP)

            draw_notes(self.notes, self.current_time, self.speed, Rect(0, 0, self.new_screen_width, self.new_screen_height),
                    self.color, self.visualizer.rect, 0.016, self.prog, self.vao, self.ctx, self.visualizer)
            self.visualizer.render(self.prog, self.vao, frame_time)
            self.UI.render()

            dt = now - self._last_time
            self._accumulator += dt
            self._fps = 0.9*self._fps + 0.1*(1.0/dt)  
            self._last_time = now

            if self._accumulator >= 1.0:
                self.UI.update_fps_text(self._fps)
                
                self._accumulator = 0.0
            if self.current_time > self.video_start_time:
                self.video.render(frame_time)
                

            from visualizer import first_note_object
            self.audio_player.check(first_note_object, self.current_time)
            if self.audio_player.audio_has_started == True and not self.flag1: 
                self.paused = True
                self.audio_player.pause_or_resume_audio()
                self.flag1 = True


                    

    def close(self):
        # TODO: Release resources
        pass


if __name__ == '__main__':
    mglw.run_window_config(VisualizerApp)


