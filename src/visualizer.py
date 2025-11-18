import random
import math
from particles import Particle, ParticleSystem, Background
from saber import Saber
import moderngl
import numpy as np
import gc
from light import LightManager, Light

WHITE_KEYS = [0, 2, 4, 5, 7, 9, 11] * 7 + [0, 2, 3]  # MIDI notes for white keys
BLACK_KEYS = [1, 3, 6, 8, 10] * 7 + [1]  # MIDI notes for black keys
POSITION_OF_BLACK_KEYS = [1, 3, 4, 6, 7]

octaves = 8

white_key_pattern = [0, 2, 3, 5, 7, 8, 10]  # Relative positions of white keys
black_key_pattern = [1, 4, 6, 9, 11]        # Relative positions of black keys
white_key_indices = []
black_key_indices = []


for octave in range(octaves):
    white_key_indices += [i + octave * 12 for i in white_key_pattern]
    black_key_indices += [i + octave * 12 for i in black_key_pattern]
for i in range(octaves - 2):
    POSITION_OF_BLACK_KEYS.extend([x + 7 for x in POSITION_OF_BLACK_KEYS])
POSITION_OF_BLACK_KEYS.append(POSITION_OF_BLACK_KEYS[-1] + 1)

NUM_WHITE_KEYS = 52
NUM_BLACK_KEYS = 36


first_note_object = None

keys = []

class Rect:
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height

class Visualizer:
    def __init__(self, app, x, y, width, height, ctx, offscreen_fbo, lighting_fbo, video, normalized_piano_y):
        self.app = app
        self.x = x
        self.y = y
        self.width = int(width)
        self.height = int(height)
        self.ctx = ctx 
        self.offscreen_fbo = offscreen_fbo
        self.lighting_fbo = lighting_fbo
        self.video = video
        self.normalized_piano_y = normalized_piano_y

        self.colors = {
            0: (0 / 255, 156 / 255, 119 / 255), # Needs to get colors from ColorSelector
            1: (30 / 255, 76 / 255, 94 / 255),
        }

        self.left_cutoff = 0.2
        self.right_cutoff = 0.8

        self.particle_radius = 3.0

        self.rect = Rect(self.x, self.y, self.width, self.height)
        self.piano = Piano(self.ctx, self.rect, self.normalized_piano_y)
        self.particle_system = ParticleSystem(self.ctx, self.rect, 1000)
        self.background = Background(self.ctx, self.offscreen_fbo, self.width, self.height, self.particle_system, self.colors[0], self.colors[1], self.left_cutoff, self.right_cutoff, self.particle_radius)
        self.saber = Saber(self.ctx, keys[0].x, keys[0].y - 160, self.rect, self.colors[0], self.colors[1], self.left_cutoff, self.right_cutoff, keys[0].y, 5.0)

        self.light_manager = LightManager(self.ctx, 1920, 1080)


    def render(self, delta_time, current_time, paused=False):
 
    
        self.piano.draw(self.left_cutoff, self.right_cutoff)
        
        if self.video.is_valid and current_time > -self.video.start_time:
            self.video.render(delta_time, current_time)
        self.particle_system.update(delta_time)
        self.saber.render()
        self.background.render(delta_time if not paused else 0)



        self.lighting_fbo.use()
        self.light_manager.render(self.offscreen_fbo.color_attachments[0])
        
    
    def reload_classes(self, old_visualizer_width, old_visualizer_height, visual_mode):

        del self.particle_system, self.background, self.saber, self.light_manager
        gc.collect()

        if visual_mode:
          
        
       
            self.particle_system = ParticleSystem(self.ctx, self.rect, 1000)
            self.background = Background(self.ctx, self.offscreen_fbo, self.width, self.height, self.particle_system, self.colors[0], self.colors[1], self.left_cutoff, self.right_cutoff, self.particle_radius)
           
            self.saber = Saber(self.ctx, keys[0].x, keys[0].y - 80, self.rect, self.colors[0], self.colors[1], self.left_cutoff, self.right_cutoff, keys[0].y, 5.0)
            self.light_manager = LightManager(self.ctx, 1920, 1080)
 
 
            if self.video.is_valid:
                self.video.visualizer_rect = self.rect
                self.video.x_offset *= self.rect.width / old_visualizer_width
                self.video.crop_top *= self.rect.height / old_visualizer_height
                #self.video.scale_factor *= self.rect.width / old_visualizer_width
                self.video._update_texture(True)

        else:
     
    
            self.particle_system = ParticleSystem(self.ctx, self.rect, 1000)
            self.background = Background(self.ctx, self.offscreen_fbo, self.width, self.height, self.particle_system, self.colors[0], self.colors[1], self.left_cutoff, self.right_cutoff, self.particle_radius)
            self.saber = Saber(self.ctx, keys[0].x, keys[0].y - 160, self.rect, self.colors[0], self.colors[1], self.left_cutoff, self.right_cutoff, keys[0].y, 5.0)
            self.light_manager = LightManager(self.ctx, 1920, 1080)
       

            if self.video.is_valid:
                self.video.visualizer_rect = self.rect
                self.video.x_offset *= self.rect.width / old_visualizer_width
                self.video.crop_top *= self.rect.height / old_visualizer_height
                #self.video.scale_factor *= self.rect.width / old_visualizer_width
                self.video._update_texture(True)

    def update_colors(self, color1, color2):
        self.colors[0] = color1
        self.colors[1] = color2
        for note in visible_notes:
            note.color1 = color1
            note.color2 = color2

        self.saber.color1 = color1
        self.saber.color2 = color2

        self.background.smoke_color1 = color1
        self.background.smoke_color2 = color2



    

    
        
    
class PianoKey:
    def __init__(self, ctx, index, visualizer_rect, normalized_piano_y):
        self.ctx = ctx
        self.index = index
        self.visualizer_rect = visualizer_rect

        self.INITIAL_COLOR = (1.0, 1.0, 1.0) if index in white_key_indices else (0.0, 0.0, 0.0)
        self.color1 = self.INITIAL_COLOR
        self.color2 = self.INITIAL_COLOR

        self.width = visualizer_rect.width / NUM_WHITE_KEYS
        self.height = visualizer_rect.height * 0.2

        if index in white_key_indices:
            self.x = white_key_indices.index(index) * self.width + visualizer_rect.x
        elif index in black_key_indices:
            nearest_left = max([i for i in white_key_indices if i < index], default=0)
            nearest_right = min([i for i in white_key_indices if i > index], default=0)
            x_left = visualizer_rect.x + (visualizer_rect.width / NUM_WHITE_KEYS) * white_key_indices.index(nearest_left)
            x_right = visualizer_rect.x + (visualizer_rect.width / NUM_WHITE_KEYS) * white_key_indices.index(nearest_right)
            self.x = (x_left + x_right) / 2
            self.height *= 0.6
            self.width *= 0.8
            self.x += 5

        self.y = visualizer_rect.height * normalized_piano_y + visualizer_rect.y
        self.lines_activated = False


    # def setup_opengl(self):
    #     with open("ModernGL shaders/key.vert", "r", encoding="utf-8") as f:
    #         vertex_shader = f.read()
    #     with open("ModernGL shaders/key.frag", "r", encoding="utf-8") as f:
    #         fragment_shader = f.read()

    #     self.prog = self.ctx.program(
    #         vertex_shader=vertex_shader,
    #         fragment_shader=fragment_shader
    #     )
    #     self.prog['u_resolution'].value = (1920, 1080)
    #     vertices = np.array([
    #         0.0, 0.0,
    #         1.0, 0.0,
    #         0.0, 1.0,
    #         1.0, 1.0,
    #     ], dtype='f4')
    #     self.vbo = self.ctx.buffer(vertices.tobytes())
    #     self.vao = self.ctx.simple_vertex_array(self.prog, self.vbo, 'in_position')

    # def draw(self, left_cutoff, right_cutoff):


    #     #print(self.width / self.visualizer_rect.height)



    #     if self.index in white_key_indices:
    #         self.prog['u_position'].value = (self.x, self.y)
    #         self.prog['u_size'].value = (self.width, self.height)
    #         self.prog['color1'].value = (c for c in self.color1)
    #         self.prog['color2'].value = (c for c in self.color2)
    #         self.prog['leftCutoff'].value = left_cutoff
    #         self.prog['rightCutoff'].value = right_cutoff
    #         self.vao.render(mode=moderngl.TRIANGLE_STRIP)

    #         self.prog['u_position'].value = (self.x, self.y)
    #         self.prog['u_size'].value = (4, self.height)
    #         self.prog['color1'].value = (0.0, 0.0, 0.0)
    #         self.prog['color2'].value = (0.0, 0.0, 0.0)
    #         self.vao.render(mode=moderngl.TRIANGLE_STRIP)
    
    #     elif self.index in black_key_indices:
            
    #         self.prog['u_position'].value = (self.x + 5, self.y)
    #         self.prog['u_size'].value = (self.width * 0.8, self.height)
    #         self.prog['color1'].value = (c for c in self.color1)
    #         self.prog['color2'].value = (c for c in self.color2)
    #         self.prog['leftCutoff'].value = left_cutoff
    #         self.prog['rightCutoff'].value = right_cutoff
    #         self.vao.render(mode=moderngl.TRIANGLE_STRIP)

    #     # Draws white vertical lines when the note is a C 
    #     if self.lines_activated and (self.index - 3) % 12 == 0:
    #         self.prog['u_position'].value = (self.x, self.y)
    #         self.prog['u_size'].value = (1, self.visualizer_rect.y - self.y) 
    #         self.prog['color1'].value = (1.0, 1.0, 1.0) 
    #         self.prog['color2'].value = (1.0, 1.0, 1.0) 
    #         self.vao.render(mode=moderngl.TRIANGLE_STRIP)
    
class Piano:
    def __init__(self, ctx, visualizer_rect, normalized_piano_y):
        self.ctx = ctx
        self.visualizer_rect = visualizer_rect
        self.normalized_piano_y = normalized_piano_y
        with open("ModernGL shaders/key.vert", "r", encoding="utf-8") as f:
            vertex_shader = f.read()
        with open("ModernGL shaders/key.frag", "r", encoding="utf-8") as f:
            fragment_shader = f.read()

        self.prog = self.ctx.program(
            vertex_shader=vertex_shader,
            fragment_shader=fragment_shader
        )
        self.prog['u_resolution'].value = (1920, 1080)

        vertices = np.array([
            0.0, 0.0,
            1.0, 0.0,
            0.0, 1.0,
            1.0, 1.0,
        ], dtype='f4')

        self.vbo = self.ctx.buffer(vertices.tobytes())
        self.vao = self.ctx.simple_vertex_array(self.prog, self.vbo, 'in_position')


        for i in range(NUM_WHITE_KEYS):
            keys.append(PianoKey(ctx, white_key_indices[i], self.visualizer_rect, normalized_piano_y))
        for i in range(NUM_BLACK_KEYS):
            keys.append(PianoKey(ctx, black_key_indices[i], self.visualizer_rect, normalized_piano_y))
        
    def draw(self, left_cutoff, right_cutoff):
        prog = self.prog
        vao = self.vao

        for key in keys:
            prog['u_position'].value = (key.x, key.y)
            prog['u_size'].value = (key.width, key.height)
            prog['u_resolution'].value = (1920, 1080)
            prog['color1'].value = key.color1
            prog['color2'].value = key.color2
            prog['leftCutoff'].value = left_cutoff
            prog['rightCutoff'].value = right_cutoff
            prog['whiteKeyWidth'].value = 1920 / NUM_WHITE_KEYS
            prog['gap'].value = 0.1


            vao.render(mode=moderngl.TRIANGLE_STRIP)

class Note: 
    def __init__(self, note, start_time, velocity, screen_rect, duration, speed, index, visualizer_rect, ctx, visualizer, scale_multiplier):
        self.note = note
        self.key_index = self.note - 21
        self.start_time = start_time
        self.velocity = velocity
        self.screen_rect = screen_rect
        self.duration = duration
        self.speed = speed
        self.index = index

        self.visualizer_rect = visualizer_rect

        
        self.is_white = True if self.key_index in white_key_indices else False
        self.width = screen_rect.width / NUM_WHITE_KEYS if self.is_white else screen_rect.width / NUM_WHITE_KEYS * 0.6 
        self.height = duration * speed 
        self.x = self.key_index * self.width + self.visualizer_rect.x
        self.y = self.visualizer_rect.y - self.height
        self.on_screen = True

        self.glow_radius = 30.0 + random.uniform(-10.0, 10.0)
        self.glow_strength = 1.5 + random.uniform(-0.3, 0.3)
        self.intensity = 90
        self.blend_power = 4
        self.border_radius = 9

        self.ctx = ctx
        self.visualizer = visualizer

        self.color1 = self.visualizer.colors[0]
        self.color2 = self.visualizer.colors[1]

        self._setup_shader()
        self._setup_geometry()

        self.phase = random.uniform(0, math.pi * 2)
        self.seed = random.uniform(0, 100)


       
        self.particle_timer = 0
        self.has_light = None

        self.scale_multiplier = scale_multiplier

        self.particle_radius = self.visualizer.particle_radius

    

      


    def _setup_shader(self):
        self.shader_name = "note"
        with open(f"ModernGL shaders/{self.shader_name}.vert", "r", encoding="utf-8") as f:
            vertex_shader = f.read()
        with open(f"ModernGL shaders/{self.shader_name}.frag", "r", encoding="utf-8") as f:
            fragment_shader = f.read()
        self.prog = self.ctx.program(vertex_shader=vertex_shader, fragment_shader=fragment_shader)
       
    def _setup_geometry(self):
        vertices = np.array([
            0.0, 0.0,
            1.0, 0.0,
            0.0, 1.0,
            1.0, 1.0,
        ], dtype='f4')
        vbo = self.ctx.buffer(vertices.tobytes())
        self.vao = self.ctx.simple_vertex_array(
            self.prog, vbo, 
            'in_uv' 
)


    def update(self, current_time, delta_time):
        elapsed_time = current_time - self.start_time
 
        self.y = self.visualizer_rect.y - self.height + self.speed * elapsed_time
        self.particle_timer += delta_time


        if self.y + self.height > keys[0].y and self.on_screen:
            if not self.has_light:
               
                self.visualizer.light_manager.add_light(Light((self.x + self.width / 2, keys[0].y), (1.0, 1.0, 1.0), 1.0, 150.0, self.key_index, self.scale_multiplier))
                self.has_light = True

            key = keys[next((i for i, obj in enumerate(keys) if obj.index == self.key_index), None)]
            key.color1 = self.color1   
            key.color2 = self.color2
          

            if self.particle_timer >= (0.19 + random.uniform(-0.1, 0.1)) * self.scale_multiplier:
                self.visualizer.particle_system.add_particle(Particle(self.x + self.width / 2, keys[0].y, 20.0, -500.0, self.particle_radius, True, self.width, self.scale_multiplier))
                self.visualizer.particle_system.add_particle(Particle(self.x + self.width / 2, keys[0].y, -20.0, -500.0, self.particle_radius, True, self.width, self.scale_multiplier))
                self.particle_timer = 0

        if random.uniform(0, 1) < 0.005 * self.scale_multiplier and self.x is not None and self.on_screen:
            self.visualizer.particle_system.add_particle(Particle(self.x + self.width / 2, self.y + self.height / 2, 50.0, 300.0, self.particle_radius + 1.0, False, self.width, self.scale_multiplier))
        
        if self.y > keys[0].y and self.on_screen:
            key = keys[next((i for i, obj in enumerate(keys) if obj.index == self.key_index), None)]
            key.color1 = key.INITIAL_COLOR
            key.color2 = key.INITIAL_COLOR
            self.on_screen = False
            self.visualizer.light_manager.lights = [light for light in self.visualizer.light_manager.lights if light.key_index != self.key_index]
            self.has_light = False
          
    def draw(self, current_time, left_cutoff, right_cutoff):
        if self.is_white:
            self.width = self.visualizer_rect.width / NUM_WHITE_KEYS
            self.x = self.width * white_key_indices.index(self.key_index) + self.visualizer_rect.x
        else:
            self.width = self.visualizer_rect.width / NUM_WHITE_KEYS * 0.6 
            # Find the nearest two white keys (left and right) surrounding the black key
            nearest_white_key_index_left = max([i for i in white_key_indices if i < self.key_index], default=0)
            nearest_white_key_index_right = min([i for i in white_key_indices if i > self.key_index], default=0)

            # Get their x coordinates
            x_left = self.visualizer_rect.x + (self.visualizer_rect.width / NUM_WHITE_KEYS) * white_key_indices.index(nearest_white_key_index_left)
            x_right = self.visualizer_rect.x + (self.visualizer_rect.width / NUM_WHITE_KEYS) * white_key_indices.index(nearest_white_key_index_right)

            # Position black key at the center between the left and right white keys
            self.x = (x_left + x_right) / 2 + 5

        if self.shader_name == "note":
         
            self.prog['notePosition'].value     = (self.x, self.y)
            self.prog['noteSize'].value         = (self.width, self.height)
            self.prog['screenResolution'].value = (self.screen_rect.width, self.screen_rect.height)
            self.prog['noteColor1'].value        = (self.color1[0], self.color1[1], self.color1[2], 1.0)
            self.prog['noteColor2'].value        = (self.color2[0], self.color2[1], self.color2[2], 1.0)
            self.prog['leftCutoff'].value = left_cutoff * self.screen_rect.width
            self.prog['rightCutoff'].value = right_cutoff * self.screen_rect.width
            
            self.prog['borderRadius'].value     = self.border_radius
            
            self.prog['glowRadius'].value     = self.glow_radius
            self.prog['glowStrength'].value   = self.glow_strength
            self.prog['blendPower'].value   = self.blend_power
            self.prog['time'].value = float(current_time * 0.3)
            self.prog['phase'].value = float(self.phase)
            self.prog['noteSeed'].value = float(self.seed)

            self.vao.render(mode=moderngl.TRIANGLE_STRIP)
        elif self.shader_name == "electric_note":
            self.prog["iTime"].value = current_time
            self.prog["iResolution"].value = (self.screen_rect.width, self.screen_rect.height)

            self.vao.render(mode=moderngl.TRIANGLE_STRIP)
    










    



visible_notes = []
visible_notes_indices = set()
first_note_is_init = False

def draw_notes(notes, current_time, speed, screen_rect, visualizer_rect, delta_time, prog, vao, ctx, visualizer, scale_multiplier, left_cutoff, right_cutoff):
    global first_note_is_init, visible_notes, visible_notes_indices


    # Reset visible notes when rewinding
    last_time = getattr(draw_notes, "last_time", None)
    if last_time is not None and current_time < last_time:
        visible_notes.clear()
        visible_notes_indices.clear()
        first_note_is_init = False
        #print("time rewind detected, resetting notes")

    draw_notes.last_time = current_time

    if not first_note_is_init:
        first_note = notes[0]
        global first_note_object
        first_note_object = Note(first_note['note'], first_note['start_time'], first_note['velocity'], screen_rect, first_note['duration'], speed, 0, visualizer_rect, ctx, visualizer, scale_multiplier)
        visible_notes.append(first_note_object)
        visible_notes_indices.add(0)
        first_note_is_init = True

    for index, note in enumerate(notes):
        if current_time + 1 >= note['start_time'] and index not in visible_notes_indices:
            if index == 0: continue
            visible_notes.append(Note(note['note'], note['start_time'], note['velocity'], screen_rect, note['duration'], speed, index, visualizer_rect, ctx, visualizer, scale_multiplier))
            visible_notes_indices.add(index)

    piano_y = keys[0].y
    notes_to_remove = []

    for note_object in visible_notes:
        note_object.update(current_time, delta_time)
        note_object.draw(current_time, left_cutoff, right_cutoff)

        if note_object.y >= piano_y:
            notes_to_remove.append(note_object)

    for note in notes_to_remove:
        visible_notes.remove(note)

        


    


