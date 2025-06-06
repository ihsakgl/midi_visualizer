import random
import math
from particles import Particle, ParticleSystem, Background
import moderngl
import numpy as np


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
particles = []
keys = []

class Rect:
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height

class Visualizer:
    def __init__(self, x, y, width, height, ctx, bg_color):
        self.x = x
        self.y = y
        self.width = int(width)
        self.height = int(height)
        self.ctx = ctx
        self.rect = Rect(self.x, self.y, self.width, self.height)
        self.piano = Piano(self.rect)
        self.particle_system = ParticleSystem(self.ctx, self.rect, 1000)
        self.background = Background(self.ctx, self.width, self.height, self.particle_system, bg_color)



    def render(self, prog, vao, delta_time):
        self.piano.draw(prog, vao)
        self.particle_system.update()
        self.background.render(delta_time)
        ...

class PianoKey:
    def __init__(self, index, visualizer_rect):
        self.index = index
        self.visualizer_rect = visualizer_rect
        self.INITIAL_COLOR = (255, 255, 255) if self.index in white_key_indices else (0, 0, 0)
        self.color = self.INITIAL_COLOR
        self.width = visualizer_rect.width / NUM_WHITE_KEYS
        self.height = visualizer_rect.height * 0.2

        if white_key_indices.__contains__(self.index):
            self.x = white_key_indices.index(self.index) * self.width + self.visualizer_rect.x 
        elif black_key_indices.__contains__(self.index):
            nearest_white_key_index_left = max([i for i in white_key_indices if i < self.index], default=0)
            nearest_white_key_index_right = min([i for i in white_key_indices if i > self.index], default=0)
            x_left = self.visualizer_rect.x + (self.visualizer_rect.width / NUM_WHITE_KEYS) * white_key_indices.index(nearest_white_key_index_left)
            x_right = self.visualizer_rect.x + (self.visualizer_rect.width / NUM_WHITE_KEYS) * white_key_indices.index(nearest_white_key_index_right)
            self.x = (x_left + x_right) / 2 
            self.height *= 0.6
        self.y = self.visualizer_rect.height * 0.65 + visualizer_rect.y
        
    def draw(self, prog, vao):

        if self.index in white_key_indices:
            prog['u_position'].value = (self.x, self.y)
            prog['u_size'].value = (self.width, self.height)
            prog['u_color'].value = (self.color[0] / 255, self.color[1] / 255, self.color[2] / 255)
            vao.render(mode=moderngl.TRIANGLE_STRIP)

            prog['u_position'].value = (self.x, self.y)
            prog['u_size'].value = (4, self.height)
            prog['u_color'].value = (0.0, 0.0, 0.0)
            vao.render(mode=moderngl.TRIANGLE_STRIP)
    
        elif self.index in black_key_indices:
            
            prog['u_position'].value = (self.x + 5, self.y)
            prog['u_size'].value = (self.width * 0.8, self.height)
            prog['u_color'].value = (self.color[0] / 255, self.color[1] / 255, self.color[2] / 255)
            vao.render(mode=moderngl.TRIANGLE_STRIP)

            # pygame.draw.rect(self.screen, self.color, (self.x + 5, self.y, self.width * 0.8, self.height * 0.6))

        # if (self.index - 3) % 12 == 0:
        
        #     pygame.draw.line(self.screen, "white", (self.x, self.y), (self.x, self.visualizer_rect.y), 1)
    
class Piano:
    def __init__(self, visualizer_rect):

        self.visualizer_rect = visualizer_rect
        for i in range(NUM_WHITE_KEYS):
            keys.append(PianoKey(white_key_indices[i], self.visualizer_rect))
        for i in range(NUM_BLACK_KEYS):
            keys.append(PianoKey(black_key_indices[i], self.visualizer_rect))
        
    def draw(self, prog, vao):
        for key in keys:
            key.draw(prog, vao)

class Note: 
    def __init__(self, note, start_time, velocity, screen_rect, duration, speed, index, color, visualizer_rect, ctx, visualizer):
        self.note = note
        self.key_index = self.note - 21
        self.start_time = start_time
        self.velocity = velocity
        self.screen_rect = screen_rect
        self.duration = duration
        self.speed = speed
        self.index = index
        self.color = color
        self.visualizer_rect = visualizer_rect

        self.INITIAL_COLOR = self.color
        self.is_white = True if self.key_index in white_key_indices else False
        self.width = screen_rect.width / NUM_WHITE_KEYS if self.is_white else screen_rect.width / NUM_WHITE_KEYS * 0.6 
        self.height = duration * speed * (self.visualizer_rect.height / 337.5)
        self.x = self.key_index * self.width + self.visualizer_rect.x
        self.y = self.visualizer_rect.y - self.height
        self.on_screen = True

        self.glow_radius = 50.0 + random.uniform(-10.0, 10.0)
        self.glow_strength = 2.0 + random.uniform(-0.3, 0.3)
        self.intensity = 120
        self.blend_power = 9
        self.border_radius = 8

        self.ctx = ctx
        self.visualizer = visualizer
        self._setup_shader()
        self._setup_geometry()

        self.phase = random.uniform(0, math.pi * 2)
        self.seed = random.uniform(0, 100)


       
        self.particle_timer = 0



    def _setup_shader(self):
        with open("ModernGL shaders/note.vert", "r", encoding="utf-8") as f:
            vertex_shader = f.read()
        with open("ModernGL shaders/note.frag", "r", encoding="utf-8") as f:
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
        self.y = self.visualizer_rect.y - self.height + (self.visualizer_rect.height / 337.5) * self.speed * elapsed_time
        self.particle_timer += delta_time

            

        if self.index == 0: 
            global first_note_object
            first_note_object = self
      
        
        if self.y + self.height > keys[0].y and self.on_screen:
            key = keys[next((i for i, obj in enumerate(keys) if obj.index == self.key_index), None)]
            key.color = self.color   
          

            if self.particle_timer >= 0.20 + random.uniform(-0.1, 0.1):
                self.visualizer.particle_system.add_particle(Particle(self.x + self.width / 2, keys[0].y, self.color, 0.1, -5.00, self.visualizer_rect, True, self.width))
                self.visualizer.particle_system.add_particle(Particle(self.x + self.width / 2, keys[0].y, self.color, -0.1, -5.00, self.visualizer_rect, True, self.width))
                self.particle_timer = 0

        if random.uniform(0, 1) < 0.005 and self.x is not None and self.on_screen:
            self.visualizer.particle_system.add_particle(Particle(self.x, self.y, self.color, random.uniform(-0.2, 0.2), random.uniform(-0.4, 0.4), self.visualizer_rect, False, self.width))
        
        if self.y > keys[0].y and self.on_screen:
            key = keys[next((i for i, obj in enumerate(keys) if obj.index == self.key_index), None)]
            key.color = key.INITIAL_COLOR
            self.on_screen = False
          
            


 
        




    def draw(self, current_time):
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

        self.prog['notePosition'].value     = (self.x, self.y)
        self.prog['noteSize'].value         = (self.width, self.height)
        self.prog['screenResolution'].value = (self.screen_rect.width, self.screen_rect.height)
        
        self.prog['noteColor'].value        = (self.color[0] / 255, self.color[1] / 255, self.color[2] / 255, 1.0)
        self.prog['blendPower'].value       = self.blend_power
        self.prog['borderRadius'].value     = self.border_radius

        self.prog['glowRadius'].value     = self.glow_radius
        self.prog['glowStrength'].value   = self.glow_strength

        self.prog['time'].value = float(current_time)
        self.prog['phase'].value = float(self.phase)
        self.prog['noteSeed'].value = float(self.seed)

        self.vao.render(mode=moderngl.TRIANGLE_STRIP)
      
    










    



visible_notes = []
visible_notes_indices = set()
def draw_notes(notes, current_time, speed, screen_rect, color, visualizer_rect, delta_time, prog, vao, ctx, visualizer):
   
    for index, note in enumerate(notes):
        if current_time + 1 >= note['start_time'] and index not in visible_notes_indices:
            visible_notes.append(Note(note['note'], note['start_time'], note['velocity'], screen_rect, note['duration'], speed, index, color, visualizer_rect, ctx, visualizer))
            visible_notes_indices.add(index)
    

    piano_y = keys[0].y
    notes_to_remove = []

    for note_object in visible_notes:
 
       
        note_object.update(current_time, delta_time)
        note_object.draw(current_time)

        if note_object.y >= piano_y:
            notes_to_remove.append(note_object)
        
    for note in notes_to_remove:
        visible_notes.remove(note)
        


    


