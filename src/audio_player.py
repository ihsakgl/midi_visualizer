from pygame import mixer 

class AudioPlayer:
    def __init__(self, buffer, current_time, visualizer_rect, speed, key_y, key_height):
        self.buffer = buffer
        self.current_time = current_time
        self.visualizer_rect = visualizer_rect
        self.speed = speed
        self.key_y = key_y
        self.key_height = key_height
        self.audio_has_started = False
        self.paused = False
   

    def load_audio(self, audio_file):
        mixer.init()
        mixer.music.load(audio_file)
    
    def play_audio(self, pos):
        mixer.music.play()
        mixer.music.set_pos(pos)
        self.audio_has_started = True

    def pause_or_resume_audio(self):
        mixer.music.unpause() if self.paused else mixer.music.pause()
        self.paused = not self.paused


    def check(self, first_note_object, current_time):
      

         if first_note_object is not None:
     
            hit_time = (self.key_y - self.visualizer_rect.y) / ((self.visualizer_rect.height / 337.5) * self.speed) + first_note_object.start_time
   
      
            if not self.audio_has_started and current_time >= hit_time:
                exceeded_time = current_time - hit_time
                pos = exceeded_time + first_note_object.start_time + self.buffer
                self.play_audio(pos)
    


  


    




