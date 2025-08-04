import moderngl
import moderngl_window as mglw
from moderngl_window import geometry
import numpy as np
import time as Time
from moderngl_window.conf import settings
settings.WINDOW['class'] = 'moderngl_window.context.pyglet.Window'

from visualizer import Visualizer, Rect, draw_notes, keys, visible_notes, visible_notes_indices
from midi_processor import load_midi_file, parse_midi
from audio_player import AudioPlayer
from video_processor import Video
from UI import UI
from utils import resize_objects, FullscreenQuad
from video_writer import GpuRecorder
   



class VisualizerApp(mglw.WindowConfig):
    gl_version = (3, 3)
    title = "Midi Visualizer"
    window_size = (1920, 1080)
    aspect_ratio = 16 / 9
    resizable = False
    fullscreen = False
    resource_dir = 'ModernGL shaders'

   


    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        import pycuda.autoprimaryctx


        self.normalized_visualizer_width = 0.70
        self.normalized_ui_width = 1.0 - self.normalized_visualizer_width

        self.base_width, self.base_height = 1920, 1080
        self.base_visualizer_rect = Rect(self.base_width * self.normalized_ui_width, 0, self.base_width * self.normalized_visualizer_width, 
                                         min(self.base_height, self.base_width * self.normalized_visualizer_width / self.aspect_ratio))

      


        self.dimenstions_init = False
       
        
        self.title_bar_height = 32
        self.ctx.enable(moderngl.BLEND)
        self.ctx.enable(moderngl.PROGRAM_POINT_SIZE)
      

        self.ctx.blend_func = (moderngl.SRC_ALPHA, moderngl.ONE_MINUS_SRC_ALPHA)

        
     


        self.flag1 = False
        self.current_time = 0
        self.speed = 200 # default: 250
        self.paused = False
        self.visual_mode = False

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

   
  

        # offscreen fbo
        self.offscreen_fbo = self.ctx.framebuffer(
            color_attachments=[self.ctx.texture((self.new_screen_width, self.new_screen_height), 4)]
        )

        self.lighting_fbo = self.ctx.framebuffer(
            color_attachments=[self.ctx.texture((self.new_screen_width, self.new_screen_height), 4)]
        )

        self.fullscreen_quad = FullscreenQuad(self.ctx)


        # MIDI
        self.midi_file_path = 'assets/Kara Main Theme/kara main theme 4.mid'
        self.midi_file = load_midi_file(self.midi_file_path)
        self.notes = parse_midi(self.midi_file)  

    	# VIDEO
        self.video_has_started = False
        self.video_file_path = 'assets/Kara Main Theme/kara main theme 4.mp4'
        self.video_start_time = -3.3982
        self.video = Video(self.ctx, self.video_file_path, self.visualizer_rect,
                            self.video_start_time)
        
        self.video_writer = GpuRecorder(self.lighting_fbo, self.new_screen_width, self.new_screen_height, 'denemeler/Kara Main Theme')
        self.encoding = False
        self.recording_frame_index = 0
        
        # UI AND VISUALIZER
        self.normalized_piano_y = 0.53
        
        self.visualizer = Visualizer(self, self.visualizer_x, self.visualizer_y, self.visualizer_width, self.visualizer_height, self.ctx, self.offscreen_fbo, self.lighting_fbo, self.video, self.normalized_piano_y)
        self.UI = UI(self.ctx, 1920, 1080, self.video, self, "assets/fonts/arial.ttf")
        
        
        self.start_time = Time.perf_counter()
        self.scale_multiplier = 1.0
        

        # AUDIO
        self.audio_file_path = 'assets/Kara Main Theme/kara main theme 4.wav'
        self.audio_player = AudioPlayer(0.1, self.visualizer.rect, self.speed, keys[0].y, keys[0].height)
        self.audio_player.load_audio(self.audio_file_path)


        self.UI.video_seeker.audio_player = self.audio_player

        self._last_time = 0
        self._fps = 0
        self._accumulator = 0
        
        self.paused_time = 0.0
        self.navigated_time = 0.0

        self.recording = False

        self.interval = [0, 1]
        self.frames_rendered_in_a_second = 0
     

       

    def on_resize(self, width: int, height: int):
       
    
        self.new_screen_width = width
        self.new_screen_height = height

        # UI dimensions: 25% of the width is for the UI
        self.ui_width = width * self.normalized_ui_width
        self.ui_height = height

        # Visualizer dimensions: 75% of the width
        self.visualizer_width = self.new_screen_width * self.normalized_visualizer_width
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
                self.visualizer.video.playing = not self.visualizer.video.playing
            elif key == self.wnd.keys.RIGHT:
                self.visualizer.video.step_forward() 
            elif key == self.wnd.keys.LEFT:
                self.visualizer.video.step_backward() 
            elif key == self.wnd.keys.A:
                self.visualizer.video.playing = not self.visualizer.video.playing
                self.paused = not self.paused
                self.audio_player.pause_or_resume_audio()
            elif key == self.wnd.keys.F:
                self.switch_fullscreen()
            elif key == self.wnd.keys.T: # test 
                pass
            elif key == self.wnd.keys.Z: # test
                pass     
            elif key == self.wnd.keys.E: # starts video encoding
                if self.recording:
                    self.encoding = True
                    self.video_writer.close()
                    self.video_writer.convert_to_mp4(self.audio_player)
                    self.recording = False       
            elif key == self.wnd.keys.R:  # starts video recording
                self.recording = not self.recording
                self.recording_frame_index = round(self.current_time * 60)
                self.audio_player.pause_or_resume_audio()
                self.switch_fullscreen()
                self.video.recording = not self.video.recording
             
                print("Recording mode:", "ON" if self.recording else "OFF")

            self.UI.keyboard_event(key, action, self.wnd)
           
           
       
              
             
                
    def on_mouse_position_event(self, x, y, dx, dy):
        return super().on_mouse_position_event(x, y, dx, dy)

    def on_mouse_drag_event(self, x, y, dx, dy):
        self.UI.move_event(x, y)

    def on_mouse_press_event(self, x, y, button):
        self.UI.press_event(x, y)

    def on_mouse_release_event(self, x: int, y: int, button: int):
        self.UI.release_event(x, y)
        
    
    def on_render(self, time: float, frame_time: float):
        if self.encoding: return





        #if frame_time > 0: print(1.0 / frame_time)
        if self.recording:
            time_step = 1.0 / self.video_writer.fps # calculate anywhere else??
 


        now = Time.time()
        dt = now - self._last_time
        self._accumulator += dt
        self._fps = 0.9*self._fps + 0.1*(1.0/dt)  
        self._last_time = now

        if self._accumulator >= 0.1:
            self.UI.update(self._fps)
            self._accumulator = 0.0
        self.ctx.viewport = (0, 0, self.new_screen_width, self.new_screen_height)


        self.offscreen_fbo.use()
        self.ctx.clear(0.0, 0.0, 0.0, 1.0)
        self.prog["u_resolution"].value = (self.new_screen_width, self.new_screen_height)

        self.prog['u_position'].value = (0.0, 0.0)
        self.prog['u_size'].value = (self.ui_width, self.ui_height)
        self.prog['u_color'].value = (0.2, 0.2, 0.2)
        self.vao.render(mode=moderngl.TRIANGLE_STRIP)

        self.prog['u_position'].value = (self.visualizer_x, self.visualizer_y)
        self.prog['u_size'].value = (self.visualizer_width, self.visualizer_height)
        self.prog['u_color'].value = (0.0, 0.0, 0.0)
        self.vao.render(mode=moderngl.TRIANGLE_STRIP)

 
       
        draw_notes(self.notes, self.current_time, self.speed, Rect(0, 0, self.new_screen_width, self.new_screen_height),
                self.visualizer.rect, frame_time, self.prog, self.vao, self.ctx, self.visualizer, self.scale_multiplier, self.visualizer.left_cutoff, self.visualizer.right_cutoff)



        
        
        if self.paused:
            self.paused_time += frame_time
            
            self.UI.render()
            self.visualizer.render(frame_time, self.current_time, paused=True)  
            
            self.ctx.screen.use()
            self.fullscreen_quad.render(self.lighting_fbo.color_attachments[0])
            
            # no audio update here

        else:
            
            
        

          
            if not self.recording:
                self.current_time = Time.perf_counter() - self.start_time - self.paused_time + self.navigated_time 
            else:
                self.current_time = Time.perf_counter() - self.start_time - self.paused_time + self.navigated_time 
                # self.current_time += time_step
                # self.recording_frame_index += 1


            self.UI.render()
            self.visualizer.render(frame_time, self.current_time)

            self.ctx.screen.use()
            self.fullscreen_quad.render(self.lighting_fbo.color_attachments[0])

           
            if self.recording:
                self.video_writer.try_encoding_frame(frame_time, self.current_time)


            
            

            from visualizer import first_note_object
            self.audio_player.update(first_note_object, self.current_time)

            # pause when first note hits the keyboard (for testing purposes)
            # if first_note_object.y + first_note_object.height >= keys[0].y and not self.flag1: 
            #     self.paused = True
            #     self.audio_player.pause_or_resume_audio()
            #     self.video.playing = False
            #     self.flag1 = True
            
        #print(self.video.timestamp, self.current_time)

        # if self.interval[0] < self.current_time <= self.interval[1]:
        #     self.frames_rendered_in_a_second += 1
        # else:
        #     self.interval[0] += 1.0; self.interval[1] += 1.0
        #     print(self.frames_rendered_in_a_second)
        #     self.frames_rendered_in_a_second = 0

            
    def on_close(self):
        # Release resources
        self.UI.save_input_settings()
        self.video.release()
        self.video_writer.release()
       


    def switch_fullscreen(self): 
        self.visual_mode = not self.visual_mode
              
        self.base_ui_width, self.base_ui_height = self.ui_width, self.ui_height
        self.base_visualizer_width, self.base_visualizer_height = self.visualizer.rect.width, self.visualizer.rect.height
        self.base_visualizer_x, self.base_visualizer_y = self.visualizer.rect.x, self.visualizer.rect.y

        if self.visual_mode:
            self.UI.is_active = False
            self.visualizer.x


            self.visualizer.rect.width, self.visualizer.rect.height = self.wnd.width, self.wnd.height
            self.visualizer.x, self.visualizer.y = 0, 0
            self.ui_width, self.ui_height = 0, 0
            self.visualizer.rect = Rect(0, 0, 1920, 1080)

            # print("VISUAL MODE")
            # print(f"base: {self.base_ui_width, self.base_ui_height, self.base_visualizer_x, self.base_visualizer_y, self.base_visualizer_width, self.base_visualizer_height}")
            # print(f"new: {self.ui_width, self.ui_height, self.visualizer.rect.x, self.visualizer.rect.y, self.visualizer.rect.width, self.visualizer.rect.height}")

    
            self.scale_multiplier = (self.visualizer.rect.width / self.base_visualizer_width + self.visualizer.rect.height / self.base_visualizer_height) / 2

            for key in keys:
                
                key.x -= self.base_ui_width
                key.x *= self.visualizer.rect.width / self.base_visualizer_width
            
                key.width *= self.visualizer.rect.width / self.base_visualizer_width
                key.visualizer_rect = self.visualizer.rect        
                key.y = self.visualizer.rect.height * self.normalized_piano_y + self.visualizer.rect.y       
            
            for note in visible_notes:
                note.x -= self.base_ui_width
                note.x *= self.visualizer.rect.width / self.base_visualizer_width
                note.width *= self.visualizer.rect.width / self.base_visualizer_width
                note.visualizer_rect = self.visualizer.rect
                note.y *= self.visualizer.rect.height / self.base_visualizer_height
                note.speed *= self.visualizer.rect.height / self.base_visualizer_height
                note.height *= self.visualizer.rect.height / self.base_visualizer_height

            self.speed *= self.visualizer.rect.height / self.base_visualizer_height
    
            self.audio_player.visualizer_rect = self.visualizer.rect
            self.audio_player.key_y = keys[0].y
            self.audio_player.speed *= self.visualizer.rect.height / self.base_visualizer_height 
            

            self.visualizer.x, self.visualizer.y = 0, 0
            self.visualizer.width, self.visualizer.height = 1920, 1080
            self.visualizer.reload_classes(self.base_visualizer_width, self.base_visualizer_height, self.visual_mode)



        else:
            self.UI.is_active = True

            
            self.visualizer.rect.width, self.visualizer.rect.height = self.base_width * self.normalized_visualizer_width, min(self.base_height, self.base_width * self.normalized_visualizer_width / self.aspect_ratio)
            self.ui_width, self.ui_height = self.base_width * self.normalized_ui_width, self.wnd.height
            self.visualizer.rect.x, self.visualizer.rect.y = self.ui_width, round((self.base_height - self.visualizer.rect.height) / 2) 
            self.visualizer.rect = Rect(self.visualizer.rect.x, self.visualizer.rect.y, self.visualizer.rect.width, self.visualizer.rect.height)


            # print("UI MODE")
            # print(f"base: {self.base_ui_width, self.base_ui_height, self.base_visualizer_x, self.base_visualizer_y, self.base_visualizer_width, self.base_visualizer_height}")
            # print(f"new: {self.ui_width, self.ui_height, self.visualizer.rect.x, self.visualizer.rect.y, self.visualizer.rect.width, self.visualizer.rect.height}")
            self.scale_multiplier = 1.0

            for key in keys:
                
                
                key.x *= self.visualizer.rect.width / self.base_visualizer_width
                key.x += self.ui_width
                key.width *= self.visualizer.rect.width / self.base_visualizer_width
                key.visualizer_rect = self.visualizer.rect        
                key.y = self.visualizer.rect.height * self.normalized_piano_y + self.visualizer.rect.y       
            
            for note in visible_notes:
                
                note.x *= self.visualizer.rect.width / self.base_visualizer_width
                note.x += self.ui_width
                note.width *= self.visualizer.rect.width / self.base_visualizer_width
                note.visualizer_rect = self.visualizer.rect
                note.y *= self.visualizer.rect.height / self.base_visualizer_height
                note.speed *= self.visualizer.rect.height / self.base_visualizer_height
                note.height *= self.visualizer.rect.height / self.base_visualizer_height

            self.speed *= self.visualizer.rect.height / self.base_visualizer_height
    
            self.audio_player.visualizer_rect = self.visualizer.rect
            self.audio_player.key_y = keys[0].y
            self.audio_player.speed *= self.visualizer.rect.height / self.base_visualizer_height 
            

            self.visualizer.x, self.visualizer.y = self.ui_width, self.ui_height
            self.visualizer.width, self.visualizer.height = 1920, 1080
            self.visualizer.reload_classes(self.base_visualizer_width, self.base_visualizer_height, self.visual_mode)


if __name__ == '__main__':
    mglw.run_window_config(VisualizerApp)


