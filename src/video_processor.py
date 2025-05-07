import os, sys
os.add_dll_directory(r"C:\Users\ihsan\Projects\Synthesia\opencv\build\install\x64\vc17\bin")
os.add_dll_directory(r"C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v12.8\bin")
sys.path.insert(0, r"C:\Users\ihsan\Projects\Synthesia\opencv\build\python_loader\cv2\python-3.12")  
# system link required: in cmd: mklink "C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v12.8\bin\cudart64_120.dll" "C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v12.8\bin\cudart64_12.dll"


import cv2
import cv2.cuda
import cv2.cudacodec
print(cv2.cuda.getCudaEnabledDeviceCount())
import numpy as np
import pygame
from visualizer import keys
import threading
import queue
import time






class Video:
    def __init__(self, video_file_path, screen, visualizer_rect):
        self.video_capture = cv2.cudacodec.createVideoReader(video_file_path)
        self.video_fps = 60
        self.frame_interval = 1.0 / self.video_fps
        self.is_valid = True
        self.screen = screen
        self.visualizer_rect = visualizer_rect
        
        # Initialize CUDA
        try: 
            self.device_id = 0
            cv2.cuda.setDevice(self.device_id)
            self.stream = cv2.cuda_Stream()
            # Check if CUDA is actually available and a device is set
            if cv2.cuda.getCudaEnabledDeviceCount() > 0:
                print(f"CUDA enabled, using device {self.device_id}: {cv2.cuda.getDevice()}")
                self.cuda_enabled = True
            else:
                print("CUDA enabled, but no devices found. Falling back to CPU processing.")
                self.cuda_enabled = False
        except cv2.error as e:
            print(f"Error initializing CUDA: {e}")
            print("CUDA disabled. Falling back to CPU processing.")
            self.cuda_enabled = False
        else:
            self.cuda_enabled = True #redundant, but good to be explicit
       

        self.playing = True
        self.needs_update = True
        self.frame_buffer = None
        self.frame_queue = queue.Queue(maxsize=30)
        self.process_thread = threading.Thread(target=self._process_video, daemon=True)
        self.process_thread.start()

        # Video parameters
        self.target_fps = 60
        self.dropped_frames = 0

        self.rotation_angle = 180.5
        self.scale_factor = 1.08
        self.crop_top = 77
        self.crop_bottom = 0
        self.x_offset = -16.8
        self.brightness = 0.5
        self.brightness_mat = None

        self.width = None
        self.height = None
        self.cropped_height = None

       
      

    def _process_video(self):
        next_frame_time = time.time()
        
        while self.is_valid:
            if not self.playing:
                time.sleep(0.01)
                continue

            init_time = time.time()
            ret, frame = self.video_capture.nextFrame(stream=self.stream)
            if not ret:
                self.is_valid = False
                self.playing = False
          
                return

            try:

                rotate_time_start = time.time()
                width, height = frame.size()
                
                
                frame = cv2.cuda.transpose(frame, stream=self.stream) # rotate
                # frame = cv2.cuda.flip(frame, 0, stream=self.stream) # flip
                
                width, height = height, width
                
                center = (width / 2, height / 2)
                M = cv2.getRotationMatrix2D(center, self.rotation_angle, 1)
                frame = cv2.cuda.warpAffine(frame, M, (width, height), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT, stream=self.stream)
                rotate_time = time.time() - rotate_time_start

                resize_time_start = time.time()
                target_width = self.visualizer_rect.width
                target_height = self.visualizer_rect.height
                frame = cv2.cuda.resize(frame, (target_height, target_width), interpolation=cv2.INTER_LINEAR, stream=self.stream)
                resize_time = time.time() - resize_time_start
                
                crop_time_start = time.time()
                frame = frame.colRange(self.crop_top, frame.size()[0])
                crop_time = time.time() - crop_time_start

                resize_time2_start = time.time()
                frame = cv2.cuda.resize(frame, dsize=(0, 0), fx=self.scale_factor, fy=self.scale_factor, interpolation=cv2.INTER_LINEAR, stream=self.stream)
                resize_time += time.time() - resize_time2_start
                
                color_time_start = time.time()
                frame = cv2.cuda.cvtColor(frame, cv2.COLOR_BGRA2RGB, stream=self.stream) # convert color
                color_time = time.time() - color_time_start

                brightness_time_start = time.time()
                frame = cv2.cuda.addWeighted(frame, self.brightness, frame, 0, 0, stream=self.stream) # adjust brightness
                brightness_time = time.time() - brightness_time_start

              
        
               
          

        
                download_time_start = time.time()
                frame = frame.download()
                download_time = time.time() - download_time_start

                make_surface_time_start = time.time()
                pygame_frame = pygame.surfarray.make_surface(frame)
                make_surface_time = time.time() - make_surface_time_start

                total_time = time.time() - init_time
           
                if self.frame_queue.full():
                    self.frame_queue.get_nowait()
                self.frame_queue.put(pygame_frame)

                next_frame_time += self.frame_interval

                print(f"Color: {color_time}")
                print(f"Rotate: {rotate_time}")
                print(f"Crop: {crop_time}")
                print(f"Upload: {0.0}")
                print(f"Brightness: {brightness_time}")
                print(f"Download: {download_time}")
                print(f"Surface_Make: {make_surface_time}")
                print(f"Scale: {resize_time}")
                print(f"Final: {total_time}")

                print(" ")

            except Exception as e:
                print(f"Error in _process_video: {e}")
                self.is_valid = False
                self.playing = False
             
                return
            sleep_time = next_frame_time - time.time()
            if sleep_time > 0:
                time.sleep(sleep_time)
            else:
                # Frame işlenmesi gecikti, FPS yetişemiyor olabilir
                self.dropped_frames += 1
                next_frame_time = time.time()


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
            x_pos =  self.visualizer_rect.x + self.x_offset
            y_pos =  keys[0].y_position
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
            self.is_valid = False




                #  # Convert to RGB
                # frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                # (height, width) = frame.shape[:2]
                # color_time = time.time() - color_start_time

                # rotate_start_time = time.time()
                # # Rotate with OpenCV
                # center = (width / 2, height / 2)
                # M = cv2.getRotationMatrix2D(center, self.rotation_angle, 1.0)
                # frame = cv2.warpAffine(frame, M, (width, height))
                

                # # Rotate 90° CCW then flip vertically
                # frame = np.rot90(frame)
                # frame = np.flipud(frame)
                # rotate_time = time.time() - rotate_start_time

                # crop_start_time = time.time()
                # # Crop from top and bottom (now reliable!)
                # frame = frame[0:width, self.crop_top:height]
                # crop_time = time.time() - crop_start_time


                

                # # Adjust brightness
                # # Upload to GPU
                # upload_time_start = time.time()
                # gpu_frame = cv2.cuda.GpuMat()
                # gpu_frame.upload(frame)
                # upload_time = time.time() - upload_time_start

                # brightness_start_time = time.time()
                # gpu_bright = cv2.cuda.addWeighted(gpu_frame, self.brightness, gpu_frame, 0, 0, stream=self.stream)
                # #frame = np.clip(frame * self.brightness, 0, 255).astype(np.uint8)
                # brightness_time = time.time() - brightness_start_time
                # # Download to CPU

                # download_start_time = time.time()
                # frame = gpu_bright.download()
                # download_time = time.time() - download_start_time
                

        
                # target_width = int(self.visualizer_rect.width * self.scale_factor)
                # target_height = int(self.visualizer_rect.height * (frame.shape[1] / height) * self.scale_factor)









                # make_surface_start_time = time.time()
                # # Convert to Pygame surface
                # pygame_frame = pygame.surfarray.make_surface(frame)