import time
import io
from pydub import AudioSegment
from pygame import mixer
import threading

class AudioPlayer:
    def __init__(self, buffer, visualizer_rect, speed, key_y, key_height):
        self.buffer = buffer
        self.visualizer_rect = visualizer_rect
        self.speed = speed
        self.key_y = key_y
        self.key_height = key_height

        self.audio_has_started = False
        self.paused = False
        self.original_audio = None
        self.current_sound = None
        self.channel = None
        self.delay_timer = None

    
        self.play_start_pos = 0.0
        self.manual_delay_offset = 0.0
   

        mixer.init()

    def load_audio(self, audio_file):
        self.original_audio = AudioSegment.from_file(audio_file)
        self.audio_file_path = audio_file

    def play_audio(self, pos):
        if self.delay_timer is not None:
            self.delay_timer.cancel()
            self.delay_timer = None

        if self.channel is not None:
            self.channel.stop()

        if self.original_audio is None:
            raise ValueError("Audio not loaded.")

        if pos < 0.0:
            self.pending_playing = True
            self.pending_play_start_time = time.perf_counter()
            self.pending_play_delay = -pos
            self.pending_play_remaining_time = -pos

            def delayed_start():
                self.pending_playing = False
                self.play_audio(0.0)

            self.delay_timer = threading.Timer(self.pending_play_remaining_time, delayed_start)
            self.delay_timer.start()
            return

        pos = max(0.0, min(pos, self.get_audio_duration()))
        trimmed_audio = self.original_audio[int(pos * 1000):]

        self.manual_delay_offset = pos
        buffer = io.BytesIO()
        trimmed_audio.export(buffer, format="wav")
        buffer.seek(0)

        self.current_sound = mixer.Sound(buffer)
        self.channel = self.current_sound.play()
    
        self.audio_has_started = True
        self.paused = False
        self.play_start_time = time.perf_counter()
        self.play_start_pos = 0.0

        # Bekleyen oynatma varsa temizle
        self.pending_play = False

    def pause_or_resume_audio(self):
        if self.delay_timer is not None or self.pending_playing:
            if not self.paused:
                self.pending_play_remaining_time = self.pending_play_remaining_time - (time.perf_counter() - self.pending_play_start_time)
                self.delay_timer.cancel()
            else:
                self.pending_play_start_time = time.perf_counter()

                def delayed_start():
                    self.pending_playing = False
                    self.play_audio(0.0)

                self.delay_timer = threading.Timer(self.pending_play_remaining_time, delayed_start)
                self.delay_timer.start()
                #print(f"Started delay timer with remaining: {self.pending_play_remaining_time}")

            self.paused = not self.paused
            return

  

        if self.paused:
            self.channel.unpause()
            self.play_start_time = time.perf_counter()
        else:
            self.channel.pause()
            self.play_start_pos = self.get_current_pos() - self.manual_delay_offset
            self.play_start_time = None

        self.paused = not self.paused
    


    def get_current_pos(self):
        if self.channel is None:
            if self.pending_playing:
                elapsed = time.perf_counter() - self.pending_play_start_time
                return -self.pending_play_delay + elapsed
            return self.manual_delay_offset

        if self.paused:
            return self.manual_delay_offset + self.play_start_pos

        elapsed = time.perf_counter() - self.play_start_time
        return self.manual_delay_offset + self.play_start_pos + elapsed



    def get_audio_duration(self):
        return self.original_audio.duration_seconds if self.original_audio else 0.0

    def seek_relative(self, delta_seconds):
        current_pos = self.get_current_pos()
        new_pos = current_pos + delta_seconds
        new_pos = max(-100.0, min(new_pos, self.get_audio_duration()))
        was_paused = self.paused

        # If delay timer exists, cancel it
        if self.delay_timer is not None:
            self.delay_timer.cancel()
            self.delay_timer = None
            self.pending_playing = False

        

        # Update offset if was paused
        if was_paused:
            self.manual_delay_offset = new_pos
            self.play_start_pos = 0.0
            self.paused = True  
            self.play_audio(new_pos)
            self.channel.pause() 
            self.pause_or_resume_audio()
        else:
            self.play_audio(new_pos)

        
    def seek_absolute(self, global_time):
        
        audio_time = global_time - self.fall_time

        # Clamp
        audio_time = min(audio_time, self.get_audio_duration())

        was_paused = self.paused
        self.play_audio(audio_time)
        if was_paused:
            self.pause_or_resume_audio()


    def update(self, first_note_object, current_time):
     

        # Calculate fall time of notes
        travel_distance = self.key_y - self.visualizer_rect.y
        velocity = self.speed
        self.fall_time = travel_distance / velocity

        self.seconds_until_hit = (first_note_object.start_time + self.fall_time) - current_time
      

        if not self.audio_has_started:
         
            self.play_audio(-self.fall_time + self.buffer) ## burayi init icine alabilirim
            self.audio_has_started = True


       
