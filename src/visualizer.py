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

key_height = 100

first_note_object = None




particles = []
keys = []


        

class PianoKey:
    def __init__(self, screen, screen_width, screen_height, index):
        self.screen = screen
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.height = 100
        self.width = screen_width / NUM_WHITE_KEYS
        self.index = index
        self.INITIAL_COLOR = "white" if self.index in white_key_indices else "black"
        self.color = self.INITIAL_COLOR

        self.y_position = screen_height - self.height
        if white_key_indices.__contains__(self.index):
            self.x_position = white_key_indices.index(self.index) * self.width
            
        elif black_key_indices.__contains__(self.index):
            nearest_white_key_index_left = max([i for i in white_key_indices if i < self.index], default=0)
            nearest_white_key_index_right = min([i for i in white_key_indices if i > self.index], default=0)
            x_position_left = (self.screen_width / NUM_WHITE_KEYS) * white_key_indices.index(nearest_white_key_index_left)
            x_position_right = (self.screen_width / NUM_WHITE_KEYS) * white_key_indices.index(nearest_white_key_index_right)
            self.x_position = (x_position_left + x_position_right) / 2

    def draw(self):
        if self.index in white_key_indices:
            pygame.draw.rect(self.screen, self.color, (self.x_position, self.y_position, self.width, self.height))
            pygame.draw.line(self.screen, "black", (self.x_position - 1, self.y_position), 
                                                   (self.x_position - 1 , self.screen_height),
                                                    4)
        elif self.index in black_key_indices:
            nearest_white_key_index_left = max([i for i in white_key_indices if i < self.index], default=0)
            nearest_white_key_index_right = min([i for i in white_key_indices if i > self.index], default=0)
            x_position_left = (self.screen_width / NUM_WHITE_KEYS) * white_key_indices.index(nearest_white_key_index_left)
            x_position_right = (self.screen_width / NUM_WHITE_KEYS) * white_key_indices.index(nearest_white_key_index_right)
          
            pygame.draw.rect(self.screen, self.color, ((x_position_left + x_position_right) / 2 + 5, self.y_position, self.width * 0.8, self.height * 0.6))
    

class Piano:
    def __init__(self, screen, screen_width, screen_height):
        self.screen = screen
        self.screen_width = screen_width
        self.screen_height = screen_height
  
        for i in range(NUM_WHITE_KEYS):
            keys.append(PianoKey(self.screen, self.screen_width, self.screen_height, white_key_indices[i]))
        for i in range(NUM_BLACK_KEYS):
            keys.append(PianoKey(self.screen, self.screen_width, self.screen_height, black_key_indices[i]))
        
        
    def draw_piano(self):
        for key in keys:
            key.draw()

    




class Note:
    def __init__(self, note, start_time, velocity, screen, screen_width, screen_height, new_screen_height, duration, speed, index, color):
        self.note = note
        self.key_index = self.note - 21
        self.start_time = start_time
        self.velocity = velocity
        self.height = duration * speed * (new_screen_height / screen_height)
        self.y_position = -self.height
        self.x_position = None
        self.screen = screen
        self.width = screen_width / NUM_WHITE_KEYS
        self.duration = duration
        self.index = index
        self.color = color
        self.INITIAL_COLOR = self.color
        
        self.particles = []
        self.particle_spawned = False
        self.border_radius = 10

        self.colors = [(0, 0, 50), (0, 50, 100), (0, 100, 150), (50, 150, 200)]
        self.color_index = 0
        self.transition_time = 100.0  # Time to transition between colors in seconds
        self.color_timer = 0
        self.gradual_color = None
        self.color_top = (0, 176, 194)
        self.color_bottom = (0, 176, 194)

        # glowing border
        self.glow_color = (0, 176, 194)
        self.glow_size = 10
        self.glow_images = self.create_glow_images(self.glow_color, self.glow_size, self.width, self.height, self.border_radius)
        
    def update(self, speed, current_time, new_screen_height, old_screen_height, start_time, screen):
        delta_y = speed * (new_screen_height / 600)
        self.y_position += delta_y / 60
   
        if self.index == 0: 
            global first_note_object
            first_note_object = self
        
        if self.y_position + self.height > calculate_piano_y_position(new_screen_height) and not self.particle_spawned:
            self.particle_spawned = True
            key = keys[next((i for i, obj in enumerate(keys) if obj.index == self.key_index), None)]
            key.color = self.color    
        
            for i in range(10):
                self.particles.append(Particle(self.x_position + self.width / 2, calculate_piano_y_position(new_screen_height), screen, self.color,
                                                (i - 4.5) * 0.1, -0.02 * (pow((i - 4.5), 2)) + 2)) 
                


        if random.uniform(0, 1) < 0.01 and self.x_position is not None:
            self.particles.append(Particle(self.x_position, self.y_position, screen, self.color, random.uniform(-1, 1), random.uniform(-2, 2)))



        if self.y_position > calculate_piano_y_position(new_screen_height):
            key = keys[next((i for i, obj in enumerate(keys) if obj.index == self.key_index), None)]
            key.color = key.INITIAL_COLOR
                     
    def update_particles(self, current_time, start_time, speed, new_screen_height, screen_height):
        particles_to_remove = []
        for particle in self.particles:
            particle.draw()
            particle.update(current_time, start_time, speed, new_screen_height, screen_height)
            
            if particle.y_position < 0 or particle.lifetime <= 0:
                particles_to_remove.append(particle)
                
        for particle in particles_to_remove:
            self.particles.remove(particle)
    
    def draw(self, screen, screen_width):
        
        self.x_position = self.key_index * self.width

        if self.key_index in white_key_indices:
        
            self.width = screen_width / NUM_WHITE_KEYS
            self.x_position = self.width * white_key_indices.index(self.key_index)
        elif self.key_index in black_key_indices:
            self.width = screen_width / NUM_WHITE_KEYS * 0.6 
            # Find the nearest two white keys (left and right) surrounding the black key
            nearest_white_key_index_left = max([i for i in white_key_indices if i < self.key_index], default=0)
            nearest_white_key_index_right = min([i for i in white_key_indices if i > self.key_index], default=0)

            # Get their x_positions
            x_position_left = (screen_width / NUM_WHITE_KEYS) * white_key_indices.index(nearest_white_key_index_left)
            x_position_right = (screen_width / NUM_WHITE_KEYS) * white_key_indices.index(nearest_white_key_index_right)

            # Position black key at the center between the left and right white keys
            self.x_position = (x_position_left + x_position_right) / 2 + 5
                     
            
      
        note_rect = pygame.Rect(self.x_position, self.y_position, self.width, self.height)
      
        self.glow()
        

       
        pygame.draw.rect(screen, (255, 255, 255), note_rect, 4, self.border_radius) 

   
    def glow(self):
        for i, glow_surface in enumerate(self.glow_images):
            self.screen.blit(glow_surface, (self.x_position, self.y_position))
    

    def create_glow_images(self, glow_color, glow_size, width, height, border_radius):    
       
        """Creates a list of glow images with varying sizes."""
        glow_images = []
        for i in range(1, glow_size + 1):   
                alpha = int(255 * (i / glow_size)) # layers are on top of each other causing alpha being 255
                ratio = glow_size / i
                glow_color = (glow_color[0], glow_color[1], glow_color[2], alpha)
                glow_surface = pygame.Surface((width * ratio, height * ratio), pygame.SRCALPHA)
                pygame.draw.rect(glow_surface, glow_color, (0, 0, width + ratio, height + ratio), border_radius=border_radius + i)
                glow_images.append(glow_surface)
        return glow_images        



        
    def update_dimensions(self, new_screen_width, new_screen_height, old_screen_width, old_screen_height, speed):
        self.height = self.duration * speed * (new_screen_height / 600)
        self.y_position *= (new_screen_height / old_screen_height)
        self.width = new_screen_width / 88
























def draw_notes(notes, current_time, speed, screen, screen_width, old_screen_height, new_screen_height):
    # Check if the notes list contains Note objects, if not, initialize them
    
    if not notes or not isinstance(notes[0], Note):
        # Create Note objects if notes list is initially filled with dictionaries
        notes[:] = [
            Note(note['note'], note['start_time'], note['velocity'], screen, screen_width, old_screen_height, new_screen_height,
                 note['duration'], speed, index, note['color'])
            for index, note in enumerate(notes)
        ]
    
    # for i, note_object in enumerate(notes):
    #     if i < 5:  # Check the first three notes
    #         print(f"Note {i}: Start Time: {note_object.start_time}, Y Position: {note_object.y_position}")

    # Create a list to hold notes that should be removed
    notes_to_remove = []

    for note_object in notes:
        # Update only if the current time has reached the note's start time     #problem: first three notes are not updated when initializing
        if current_time >= note_object.start_time:
            if note_object.y_position < calculate_piano_y_position(new_screen_height):
                note_object.update(speed, current_time, new_screen_height, old_screen_height, note_object.start_time, screen)
                note_object.draw(screen, screen_width)
            
              
            note_object.update_particles(current_time, note_object.start_time, speed, new_screen_height, old_screen_height)

        # Check if the note has moved off-screen and should be removed
        if note_object.y_position >= calculate_piano_y_position(new_screen_height) and note_object.particles == []:
            notes_to_remove.append(note_object)
  
            

    # Remove notes that have moved off-screen
    for note in notes_to_remove:
        notes.remove(note)

def calculate_piano_y_position(screen_height):
    return screen_height - key_height * (screen_height / 600)

def calculate_note_falling_duration(end_y, start_y, desired_duration):
    return (end_y - start_y) / desired_duration