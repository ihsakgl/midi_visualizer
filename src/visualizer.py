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

        self.particle_radius = 5.0

        self.rect = Rect(self.x, self.y, self.width, self.height)
        self.piano = Piano(self.ctx, self.rect, self.normalized_piano_y)
        self.note_manager = NoteManager(self.ctx, self.app.screen_rect, self.rect)
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
        self.background.render(delta_time if not paused else 0, current_time)



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
        for note in self.note_manager.notes:
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
            self.x = (x_left + x_right) / 2 + 5
            self.height *= 0.6
            self.width *= 0.8
            

        self.y = visualizer_rect.height * normalized_piano_y + visualizer_rect.y
        self.lines_activated = False


   


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
    """Stores GPU data for a single falling note rectangle."""
    def __init__(self, note, start_time, velocity, duration, speed, key_index, visualizer_rect, colors, visualizer, scale_multiplier):
        self.note = note
        self.key_index = key_index
        self.start_time = start_time
        self.velocity = velocity
        self.duration = duration
        self.speed = speed
        self.visualizer_rect = visualizer_rect
        self.visualizer = visualizer
        self.scale_multiplier = scale_multiplier

        self.is_white = key_index in white_key_indices
 
        self.height = duration * speed

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
        
        self.y = visualizer_rect.y - self.height

        self.color1 = tuple(c / 255.0 for c in colors[0])  # convert 0..255 -> 0..1
        self.color2 = tuple(c / 255.0 for c in colors[1])
        self.phase = np.random.rand() * np.pi * 2.0
        self.seed = np.random.rand() * 100.0
        self.on_screen = True

        self.particle_timer = 0.0
        self.particle_radius = self.visualizer.particle_radius

        self.has_light = False

        self.counter = 0

    def update(self, current_time, delta_time):
        elapsed = current_time - self.start_time
        self.y = self.visualizer_rect.y - self.height + self.speed * elapsed
        self.particle_timer += delta_time

        if self.y + self.height > keys[0].y and self.on_screen:
            if not self.has_light:
               
                self.visualizer.light_manager.add_light(Light((self.x + self.width / 2, keys[0].y), (1.0, 1.0, 1.0), 1.0, 150.0, self.key_index, self.scale_multiplier))
                self.has_light = True

            key = keys[next((i for i, obj in enumerate(keys) if obj.index == self.key_index), None)]
            key.color1 = self.color1    
            key.color2 = self.color2





   

     
            if self.particle_timer >= (0.19 + random.uniform(-0.1, 0.1)) * self.scale_multiplier:
            
                self.visualizer.particle_system.add_particle(Particle(self.x + self.width / 2, keys[0].y, 20.0, -700.0, self.particle_radius, True, self.width, self.scale_multiplier))
                self.visualizer.particle_system.add_particle(Particle(self.x + self.width / 2, keys[0].y, -20.0, -700.0, self.particle_radius, True, self.width, self.scale_multiplier))
                self.particle_timer = 0
        if random.uniform(0, 1) < 0.005 * self.scale_multiplier * delta_time * 140 and self.x is not None and self.on_screen:
            self.counter += 1
           
            self.visualizer.particle_system.add_particle(Particle(self.x + self.width / 2, self.y + self.height / 2, 50.0, 300.0, self.particle_radius + 1.0, False, self.width, self.scale_multiplier))
        if self.y > keys[0].y and self.on_screen:
            key = keys[next((i for i, obj in enumerate(keys) if obj.index == self.key_index), None)]
            key.color1 = key.INITIAL_COLOR
            key.color2 = key.INITIAL_COLOR
            self.on_screen = False
            self.visualizer.light_manager.lights = [light for light in self.visualizer.light_manager.lights if light.key_index != self.key_index]
            self.has_light = False


          

 
 #     def update(self, current_time, delta_time):
#         elapsed_time = current_time - self.start_time
 
#         self.y = self.visualizer_rect.y - self.height + self.speed * elapsed_time
#         self.particle_timer += delta_time


#         if self.y + self.height > keys[0].y and self.on_screen:
#             if not self.has_light:
               
#                 self.visualizer.light_manager.add_light(Light((self.x + self.width / 2, keys[0].y), (1.0, 1.0, 1.0), 1.0, 150.0, self.key_index, self.scale_multiplier))
#                 self.has_light = True

#             key = keys[next((i for i, obj in enumerate(keys) if obj.index == self.key_index), None)]
#             key.color1 = self.color1   
#             key.color2 = self.color2
          

#             if self.particle_timer >= (0.19 + random.uniform(-0.1, 0.1)) * self.scale_multiplier:
#                 self.visualizer.particle_system.add_particle(Particle(self.x + self.width / 2, keys[0].y, 20.0, -500.0, self.particle_radius, True, self.width, self.scale_multiplier))
#                 self.visualizer.particle_system.add_particle(Particle(self.x + self.width / 2, keys[0].y, -20.0, -500.0, self.particle_radius, True, self.width, self.scale_multiplier))
#                 self.particle_timer = 0

#         if random.uniform(0, 1) < 0.005 * self.scale_multiplier and self.x is not None and self.on_screen:
#             self.visualizer.particle_system.add_particle(Particle(self.x + self.width / 2, self.y + self.height / 2, 50.0, 300.0, self.particle_radius + 1.0, False, self.width, self.scale_multiplier))
        
#         if self.y > keys[0].y and self.on_screen:
#             key = keys[next((i for i, obj in enumerate(keys) if obj.index == self.key_index), None)]
#             key.color1 = key.INITIAL_COLOR
#             key.color2 = key.INITIAL_COLOR
#             self.on_screen = False
#             self.visualizer.light_manager.lights = [light for light in self.visualizer.light_manager.lights if light.key_index != self.key_index]
#             self.has_light = False
        




class NoteManager:
    def __init__(self, ctx, screen_rect, visualizer_rect):
        self.ctx = ctx
        self.screen_rect = screen_rect
        self.visualizer_rect = visualizer_rect

        with open("ModernGL shaders/note_instanced.vert") as f:
            vs = f.read()
        with open("ModernGL shaders/note_instanced.frag") as f:
            fs = f.read()
        self.prog = self.ctx.program(vertex_shader=vs, fragment_shader=fs)

        quad = np.array([
            0.0, 0.0,
            1.0, 0.0,
            0.0, 1.0,
            1.0, 1.0,
        ], dtype='f4')
        self.vbo = self.ctx.buffer(quad.tobytes())

        # 3) instance buffer reserve (float32 per instance)
        # layout: pos.x,pos.y (2), size.x,size.y (2), color1.r,g,b,a (4), color2.r,g,b,a (4), 
        self.instance_floats = 14
        self.max_instances = 4096
        empty = np.zeros((self.max_instances, self.instance_floats), dtype=np.float32)
        self.instance_vbo = self.ctx.buffer(empty.tobytes())

        # 4) VAO with per-instance attributes (note the '/i' for instanced)
        self.vao = self.ctx.vertex_array(
            self.prog,
            [
                (self.vbo, '2f', 'in_uv'),
                (self.instance_vbo, '2f 2f 4f 4f f f/i', 'i_pos', 'i_size', 'i_color1', 'i_color2', 'i_seed', 'i_phase')
            ]
        )
        # uniforms
        self.prog['u_resolution'].value = (screen_rect.width, screen_rect.height)
        
        self.prog['leftCutoff'].value = 0.0
        self.prog['rightCutoff'].value = 1.0
        self.prog['borderRadius'].value = 8.0
        self.prog['glowRadius'].value = 30.0
        self.prog['glowStrength'].value = 1.5
        self.prog['blendPower'].value = 4.0
      

        # note list
        self.notes = []

    def spawn_note(self, *args, **kwargs):
        note = Note(*args, **kwargs)
        self.notes.append(note)

    def update_notes(self, t, dt):
        # update and filter visible notes
        visible = []
        for n in self.notes:
            n.update(t, dt)
            if n.on_screen:
                visible.append(n)
        self.notes = [n for n in self.notes if n.on_screen]  # keep as needed
        return visible

    def upload_and_draw(self, current_time, delta_time):
        visible = self.update_notes(current_time, delta_time)
        
        N = len(visible)
        if N == 0:
            return

        # prepare numpy array (vectorized where possible)
        arr = np.empty((N, self.instance_floats), dtype=np.float32)
        for i, note in enumerate(visible):
            arr[i,0] = note.x
            arr[i,1] = note.y
            arr[i,2] = note.width
            arr[i,3] = note.height
            arr[i,4:8] = (*note.color1, 1.0)
            arr[i,8:12] = (*note.color2, 1.0)
            arr[i,12] = note.seed
            arr[i,13] = note.phase
         

        # upload only used portion
        self.instance_vbo.write(arr.tobytes())

        # set per-frame uniforms (if changed)
        # self.prog['leftCutoff'].value = ...
        # self.prog['rightCutoff'].value = ...
        self.prog['time'].value = float(current_time * 1.3)

        # render all instances in one draw call
        self.vao.render(mode=moderngl.TRIANGLE_STRIP, instances=N)


    



visible_notes = []
visible_notes_indices = set()
first_note_is_init = False

def draw_notes(notes, current_time, speed, screen_rect, visualizer_rect, delta_time, prog, vao, ctx, visualizer, scale_multiplier, left_cutoff, right_cutoff):
    global first_note_is_init, visible_notes, visible_notes_indices


    # Reset visible notes when rewinding
    last_time = getattr(draw_notes, "last_time", None)
    if last_time is not None and current_time < last_time:
        visualizer.note_manager.notes.clear()
        visible_notes_indices.clear()
        first_note_is_init = False
        #print("time rewind detected, resetting notes")

    draw_notes.last_time = current_time

    if not first_note_is_init:
        first_note = notes[0]
        global first_note_object
        first_note_object = Note(
            note=first_note['note'],
            start_time=first_note['start_time'],
            velocity=first_note['velocity'],
            duration=first_note['duration'],
            speed=speed,
            key_index=first_note['note'] - 21,
            visualizer_rect=visualizer_rect,
            colors=(tuple(int(c*255) for c in visualizer.colors[0]), tuple(int(c*255) for c in visualizer.colors[1])),
            visualizer=visualizer,
            scale_multiplier=scale_multiplier
        )
      
        visualizer.note_manager.notes.append(first_note_object)
        visible_notes_indices.add(0)
        first_note_is_init = True

    for index, note in enumerate(notes):
        if current_time + 1 >= note['start_time'] and index not in visible_notes_indices:
            if index == 0: continue
            # visible_notes.append(Note(note['note'], note['start_time'], note['velocity'], screen_rect, note['duration'], speed, index, visualizer_rect, ctx, visualizer, scale_multiplier))
            visible_notes_indices.add(index)
            visualizer.note_manager.spawn_note(
                note=note['note'],
                start_time=note['start_time'],
                velocity=note['velocity'],
                duration=note['duration'],
                speed=speed,
                key_index=note['note'] - 21,
                visualizer_rect=visualizer_rect,
                colors=(tuple(int(c*255) for c in visualizer.colors[0]), tuple(int(c*255) for c in visualizer.colors[1])),
                visualizer=visualizer,
                scale_multiplier=scale_multiplier
            )


    notes_to_remove = []

    visualizer.note_manager.upload_and_draw(current_time, delta_time)
       

   

    for note in notes_to_remove:
        visualizer.note_manager.notes.remove(note)

        


    


