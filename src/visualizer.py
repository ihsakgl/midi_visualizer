import pygame
import pygame.gfxdraw
import random
import math
from particles import Particle


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

        

class PianoKey:
    def __init__(self, screen, index, visualizer_rect):
        self.screen = screen
        self.index = index
        self.visualizer_rect = visualizer_rect
        self.INITIAL_COLOR = "white" if self.index in white_key_indices else "black"
        self.color = self.INITIAL_COLOR
        self.width = visualizer_rect.width / NUM_WHITE_KEYS
        self.height = visualizer_rect.height * 0.2

        if white_key_indices.__contains__(self.index):
            self.x_position = white_key_indices.index(self.index) * self.width + self.visualizer_rect.x 
        elif black_key_indices.__contains__(self.index):
            nearest_white_key_index_left = max([i for i in white_key_indices if i < self.index], default=0)
            nearest_white_key_index_right = min([i for i in white_key_indices if i > self.index], default=0)
            x_position_left = self.visualizer_rect.x + (self.visualizer_rect.width / NUM_WHITE_KEYS) * white_key_indices.index(nearest_white_key_index_left)
            x_position_right = self.visualizer_rect.x + (self.visualizer_rect.width / NUM_WHITE_KEYS) * white_key_indices.index(nearest_white_key_index_right)
            self.x_position = (x_position_left + x_position_right) / 2 
        self.y_position = self.visualizer_rect.height * 0.65 + visualizer_rect.y
        
    def draw(self):

        if self.index in white_key_indices:
            pygame.draw.rect(self.screen, self.color, (self.x_position, self.y_position, self.width, self.height))
            pygame.draw.line(self.screen, "black", (self.x_position - 1, self.y_position), 
                                                   (self.x_position - 1 , self.y_position + self.height),
                                                    4)
        elif self.index in black_key_indices:
            pygame.draw.rect(self.screen, self.color, (self.x_position + 5, self.y_position, self.width * 0.8, self.height * 0.6))

        # if (self.index - 3) % 12 == 0:
        
        #     pygame.draw.line(self.screen, "white", (self.x_position, self.y_position), (self.x_position, self.visualizer_rect.y), 1)
    

class Piano:
    def __init__(self, screen, visualizer_rect):
        self.screen = screen
        self.visualizer_rect = visualizer_rect
        for i in range(NUM_WHITE_KEYS):
            keys.append(PianoKey(self.screen, white_key_indices[i], self.visualizer_rect))
        for i in range(NUM_BLACK_KEYS):
            keys.append(PianoKey(self.screen, black_key_indices[i], self.visualizer_rect))
        
    def draw_piano(self):
        for key in keys:
            key.draw()

    




class Note:
    def __init__(self, note, start_time, velocity, screen, screen_width, duration, speed, index, color, visualizer_rect):
        self.note = note
        self.key_index = self.note - 21
        self.start_time = start_time
        self.velocity = velocity
        self.screen = screen
        self.index = index
        self.color = color
        self.INITIAL_COLOR = self.color
        if self.key_index in white_key_indices: 
            self.is_white = True
        else:
            self.is_white = False
        self.visualizer_rect = visualizer_rect ###
        
        
        self.width = screen_width / NUM_WHITE_KEYS if self.is_white else screen_width / NUM_WHITE_KEYS * 0.6 
        self.height = duration * speed * (self.visualizer_rect.height / 337.5)
        self.x_position = self.key_index * self.width + self.visualizer_rect.x
        self.y_position = self.visualizer_rect.y - self.height
        self.border_radius = 0
        
        
        self.particles = []
        self.particle_timer = 0
     
        self.on_screen = True

        # glowing
        
        self.max_glow_layers = round(20 * (self.visualizer_rect.height / 337.5))
        self.glow_intensity = 120
        self.blend_power = 4
        
        self.note_image = self.create_radial_glow_surface(self.width, self.height, self.color, self.max_glow_layers, self.glow_intensity, self.blend_power)
    
        
       
        
    def update(self, speed, current_time, delta_time):
       
        elapsed_time = current_time - self.start_time
        self.y_position = self.visualizer_rect.y - self.height + (self.visualizer_rect.height / 337.5) * speed * elapsed_time
        self.particle_timer += delta_time
       

        if self.index == 0: 
            global first_note_object
            first_note_object = self
            
        
        if self.y_position + self.height > keys[0].y_position and self.on_screen:
            
           
            key = keys[next((i for i, obj in enumerate(keys) if obj.index == self.key_index), None)]
            key.color = self.color    

            if self.particle_timer >= 0.06:
                self.particles.append(Particle(self.x_position + self.width / 2, keys[0].y_position, self.screen, (255, 255, 255), 0.2, -3.25, self.visualizer_rect, True))
                self.particles.append(Particle(self.x_position + self.width / 2, keys[0].y_position, self.screen, (255, 255, 255), -0.2, -3.25, self.visualizer_rect, True))
                self.particle_timer = 0
            
            
        
           
        
                                             


        if random.uniform(0, 1) < 0.01 and self.x_position is not None:
            self.particles.append(Particle(self.x_position, self.y_position, self.screen, self.color, random.uniform(-1, 1), random.uniform(-2, 2), self.visualizer_rect, False))



        if self.y_position > keys[0].y_position and self.on_screen:
         
            key = keys[next((i for i, obj in enumerate(keys) if obj.index == self.key_index), None)]
            key.color = key.INITIAL_COLOR
            self.on_screen = False
       
                     
    def update_particles(self, current_time, speed):
        particles_to_remove = []
        for particle in self.particles:
            particle.update((current_time - self.start_time) / 1000)
            particle.draw()
            
            
            if particle.y_position < 0 or particle.radius <= particle.initial_radius * 0.01:
                particles_to_remove.append(particle)
             
                
        for particle in particles_to_remove:
            self.particles.remove(particle)
    
    def draw(self, screen):
        
        if self.is_white:
            self.width = self.visualizer_rect.width / NUM_WHITE_KEYS
            self.x_position = self.width * white_key_indices.index(self.key_index) + self.visualizer_rect.x
        else:
            self.width = self.visualizer_rect.width / NUM_WHITE_KEYS * 0.6 
            # Find the nearest two white keys (left and right) surrounding the black key
            nearest_white_key_index_left = max([i for i in white_key_indices if i < self.key_index], default=0)
            nearest_white_key_index_right = min([i for i in white_key_indices if i > self.key_index], default=0)

            # Get their x_positions
            x_position_left = self.visualizer_rect.x + (self.visualizer_rect.width / NUM_WHITE_KEYS) * white_key_indices.index(nearest_white_key_index_left)
            x_position_right = self.visualizer_rect.x + (self.visualizer_rect.width / NUM_WHITE_KEYS) * white_key_indices.index(nearest_white_key_index_right)

            # Position black key at the center between the left and right white keys
            self.x_position = (x_position_left + x_position_right) / 2 + 5

            

       
            
        note_rect = pygame.Rect(self.x_position, self.y_position, self.width, self.height)
      
     
        

        
       
                                                   
        screen.blit(self.note_image, (
            self.x_position - self.note_image.get_width() / 2 + self.width / 2,
            self.y_position - self.note_image.get_height() / 2 + self.height / 2))

       

   
    
    def create_radial_glow_surface(self, note_width, note_height, color, max_glow, intensity, blend_power):
        # a surface twice as big so the glow can spread outside the note
        glow_surface = pygame.Surface((int(note_width*2), int(note_height*2)), pygame.SRCALPHA)
        cx, cy = glow_surface.get_width()//2, glow_surface.get_height()//2

        base = pygame.Rect(
            cx - note_width / 2,
            cy - note_height / 2,
            note_width, note_height
        )


        # Outer glow — colored
        for i in range(max_glow, 0, -1):
            fade = (1 - (i / max_glow)) ** (blend_power / 2)
            alpha = int(intensity * fade)
            col = (*color, alpha)

            growth = (i / max_glow) ** 2
            inflate_amount = growth * max_glow * 2
            r = base.inflate(inflate_amount, inflate_amount)

            if r.width > 0 and r.height > 0:
                radius = self.border_radius + int(inflate_amount // 2)
                pygame.draw.rect(glow_surface, col, r, border_radius=radius)



        
        # Inner Glow
        pixel_step = min(base.width, base.height) / (2 * max_glow)
        last_r, last_g, last_b = color[0], color[1], color[2]
        white_start = 1
        white_end = 0.85
        core_start = 0.475
        core_end = 0.4
        for i in range(max_glow, 0, -1):
            scale = (i / max_glow)  # 1 → 0
            t = scale ** blend_power  # Apply blend curve

           
            # White → Note Color
            if white_start >= scale > white_end:   # white border
                r, g, b = 255, 255, 255
            elif white_end >= scale > core_start:
                r = int(255 * t + color[0] * (1 - t))
                g = int(255 * t + color[1] * (1 - t))      # blending from white to note color
                b = int(255 * t + color[2] * (1 - t))
            elif core_start >= scale > core_end:
                r = round(last_r * 0.95)
                g = round(last_g * 0.95)                       # blending from note color to darker note color
                b = round(last_b * 0.95)
                last_r, last_g, last_b = r, g, b
            elif core_end >= scale:
                r, g, b = last_r, last_g, last_b        # filling the core with darker note color
          
                
                
           
            alpha = 255
    
        
            blended_color = (r, g, b, alpha)
            
            inset = (max_glow - i) * pixel_step

            new_x = round(base.x + inset)
            new_y = round(base.y + inset)
            new_width = round(base.width - inset * 2)
            new_height = round(base.height - inset * 2)
            

            pygame.draw.rect(
                glow_surface,
                blended_color,
                pygame.Rect(new_x, new_y, new_width, new_height),
                border_radius=int(self.border_radius + scale)
            )
        

        return glow_surface




      















visible_notes = []
visible_notes_indices = set()
def draw_notes(notes, current_time, speed, screen, screen_width, old_screen_height, new_screen_height, color, visualizer_rect, delta_time):
   
    for index, note in enumerate(notes):
        if current_time + 1 >= note['start_time'] and index not in visible_notes_indices:
            visible_notes.append(Note(note['note'], note['start_time'], note['velocity'], screen, screen_width,
                 note['duration'], speed, index, color, visualizer_rect))
            visible_notes_indices.add(index)
    

    
    

    # Create a list to hold notes that should be removed
    piano_y_position = keys[0].y_position
    notes_to_remove = []

    for note_object in visible_notes:
        # Update only if the current time has reached the note's start time     #problem: first three notes are not updated when initializing
       
        note_object.update(speed, current_time, delta_time)
        note_object.draw(screen)
        note_object.update_particles(current_time, speed)
              
            

        # Check if the note has moved off-screen and should be removed
        if note_object.y_position >= piano_y_position and not note_object.particles:
            notes_to_remove.append(note_object)
        
            

    # Remove notes that have moved off-screen
    for note in notes_to_remove:
        visible_notes.remove(note)
        


    


 