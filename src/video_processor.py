import cv2
import cv2.cuda
import numpy as np
import pygame
from visualizer import keys
import threading
import queue
import time

class Video:
    def __init__(self, video_file_path, screen, visualizer_rect):
        self.video_capture = cv2.VideoCapture(video_file_path)
        self.video_fps = self.video_capture.get(cv2.CAP_PROP_FPS)
        self.frame_interval = 1.0 / self.video_fps
        if not self.video_capture.isOpened():
            print("Error: Could not open video file.")

        self.screen = screen
        self.visualizer_rect = visualizer_rect

        self.is_valid = True
        self.playing = True
        self.needs_update = True
        self.frame_buffer = None
        self.frame_queue = queue.Queue(maxsize=30)

        self.process_thread = threading.Thread(target=self._process_video, daemon=True)
        self.process_thread.start()

        # Video parameters
        self.target_fps = 60
        self.dropped_frames = 0

        self.rotation_angle = 179.4
        self.scale_factor = 1.076
        self.crop_top = 245
        self.crop_bottom = 0
        self.x_offset = -18
        self.brightness = 0.5

        self.width = None
        self.height = None
        self.cropped_height = None

    def _process_video(self):
        next_frame_time = time.time()

        while self.is_valid:
            if not self.playing:
                time.sleep(0.01)
                continue

            current_time = time.time()
            if current_time < next_frame_time:
                time.sleep(0.001)
                continue

            ret, frame = self.video_capture.read()
            if not ret:
                self.is_valid = False
                self.playing = False
                self.video_capture.release()
                return

            # Convert to RGB
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            (height, width) = frame.shape[:2]

            # Rotate with OpenCV
            center = (width / 2, height / 2)
            M = cv2.getRotationMatrix2D(center, self.rotation_angle, 1.0)
            frame = cv2.warpAffine(frame, M, (width, height))

            # Rotate 90° CCW then flip vertically
            frame = np.rot90(frame)
            frame = np.flipud(frame)
        
            # Crop from top and bottom (now reliable!)
            frame = frame[0:width, self.crop_top:height]

            # Adjust brightness
            #frame = np.clip(frame * self.brightness, 0, 255).astype(np.uint8)

          #  cropped_height, cropped_width = adjusted_frame.shape[:2]
            target_width = int(self.visualizer_rect.width * self.scale_factor)
            target_height = int(self.visualizer_rect.height * (frame.shape[1] / height) * self.scale_factor)


            # Convert to Pygame surface
            pygame_frame = pygame.surfarray.make_surface(frame)

            # Resize the Pygame surface to fit target size
            pygame_frame = pygame.transform.scale(pygame_frame, (target_width, target_height))


            

            

            # Put frame in queue (replace old if necessary)
            if self.frame_queue.full():
                self.frame_queue.get_nowait()
            self.frame_queue.put(pygame_frame)

            next_frame_time += self.frame_interval


    def update(self):
        if not self.is_valid:
            return

        if not self.frame_queue.empty():
            try:
                self.frame_buffer = self.frame_queue.get_nowait()
               # print(f"Queue size after get: {self.frame_queue.qsize()}")
            except queue.Empty:
                pass

        if self.frame_buffer is not None:
            x_pos = self.visualizer_rect.x + self.x_offset
            y_pos = keys[0].y_position
            self.screen.set_clip(self.visualizer_rect)
            self.screen.blit(self.frame_buffer, (x_pos, y_pos))
            self.screen.set_clip(None)

    # Setters to update parameters dynamically
    def set_rotation_angle(self, angle):
        self.rotation_angle = angle
        self.needs_update = True

    def set_scale_factor(self, scale):
        self.scale_factor = scale
        self.needs_update = True

    def set_crop_top(self, top):
        self.crop_top = top
        self.needs_update = True

    def set_crop_bottom(self, bottom):
        self.crop_bottom = bottom
        self.needs_update = True

    def set_x_offset(self, offset):
        self.x_offset = offset
        self.needs_update = True

    def set_brightness(self, brightness):
        self.brightness = brightness
        self.needs_update = True

    def play(self):
        if not self.is_valid:
            return
        self.playing = True

    def pause(self):
        if not self.is_valid:
            return
        self.playing = False

    def release(self):
        if self.is_valid:
            self.playing = False
            self.video_capture.release()
            self.is_valid = False
