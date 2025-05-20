import os, sys
os.add_dll_directory(r"C:\Users\ihsan\Projects\Synthesia\opencv\build\install\x64\vc17\bin")
os.add_dll_directory(r"C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v12.8\bin")
sys.path.insert(0, r"C:\Users\ihsan\Projects\Synthesia\opencv\build\python_loader\cv2\python-3.12")  
# system link required: 
# 
# 
# in cmd: mklink 
# "C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v12.8\bin\cudart64_120.dll" "C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v12.8\bin\cudart64_12.dll"


import cv2
import cv2.cuda
import cv2.cudacodec
import numpy as np
import pygame
from visualizer import keys
import threading
import queue
import time
os.add_dll_directory(r"C:\libs\FFmpeg\bin")
import _PyNvCodec as nvc
import ctypes
import moderngl





class Video:
    def __init__(self, video_file_path, screen, visualizer_rect, start_time, ctx):
        self.video_file_path = video_file_path
        self.video_capture = nvc.PyNvDecoder(self.video_file_path, 0, {'pixel_format': 'rgb'})
        self.cudacodec = cv2.cudacodec.createVideoReader(video_file_path)
        self.video_fps = 60.06
        self.frame_interval = 1.0 / self.video_fps
        self.is_valid = True
        self.screen = screen
        self.visualizer_rect = visualizer_rect
        self.duration = self.get_video_duration()
        self.use_cudacodec = False
        if self.use_cudacodec: 
            self.stream = cv2.cuda_Stream()
        else:
            self.stream = nvc.CudaStream()
        # Initialize CUDA
        try: 
            self.device_id = 0
            cv2.cuda.setDevice(self.device_id)
            
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
        self.start_time = start_time
        frames_to_skip = int(start_time * self.video_fps)
        for frame in range(frames_to_skip):
            ret = self.video_capture.nextFrame(stream=self.stream)

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
        self.scale_factor = 1.08
        self.crop_top = 77
        self.crop_bottom = 0
        self.x_offset = -10
        self.brightness = 0.5
  
        
        
       
        self.ctx = ctx
        self.width = self.video_capture.Width()
        self.height = self.video_capture.Height()
        self.texture = ctx.texture((self.video_capture.Width(), self.video_capture.Height()), components=4, dtype='f1')
        self.texture.filter = (moderngl.LINEAR, moderngl.LINEAR)

       
      

    def _process_video(self):
        
        
        while self.is_valid:
            start_time = time.perf_counter()
            if not self.playing:
                time.sleep(0.01)
                continue

            init_time = time.time()

            if self.use_cudacodec:
                ret, frame = self.cudacodec.nextFrame()
            else:
                decode_time_start = time.time()
                surface = self.video_capture.DecodeSingleSurface()
                decode_time = time.time() - decode_time_start

                color_time_start = time.time()
                width = self.video_capture.Width()
                height = self.video_capture.Height()

                converter = nvc.PySurfaceConverter(width, height, nvc.PixelFormat.NV12, nvc.PixelFormat.RGBA, 0)
                cc_ctx = nvc.ColorspaceConversionContext(nvc.ColorSpace.BT_709, nvc.ColorRange.MPEG)
                surface = converter.Execute(surface, cc_ctx)
                color_time = time.time() - color_time_start
            
                convert_time_start = time.time()
                processor = nvc.VideoFrameProcessor(surface)
                convert_time = time.time() - convert_time_start
         

            
           
            try:
                if self.use_cudacodec:
                    width, height = frame.size()
                    frame = cv2.cuda.transpose(frame, stream=self.stream) # rotate
                    # frame = cv2.cuda.flip(frame, 0, stream=self.stream) # flip
                    width, height = height, width
                    center = (width / 2, height / 2)
                    M = cv2.getRotationMatrix2D(center, self.rotation_angle, 1)
                    frame = cv2.cuda.warpAffine(frame, M, (width, height), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT, stream=self.stream)
                    target_width = self.visualizer_rect.width
                    target_height = self.visualizer_rect.height
                    frame = cv2.cuda.resize(frame, (target_height, target_width), interpolation=cv2.INTER_LINEAR, stream=self.stream)
                    frame = frame.colRange(self.crop_top, frame.size()[0])
                    frame = cv2.cuda.resize(frame, dsize=(0, 0), fx=self.scale_factor, fy=self.scale_factor, interpolation=cv2.INTER_LINEAR, stream=self.stream)
                    frame = cv2.cuda.cvtColor(frame, cv2.COLOR_BGRA2RGB, stream=self.stream) # convert color
                    frame = cv2.cuda.addWeighted(frame, self.brightness, frame, 0, 0, stream=self.stream) # adjust brightness
                    download_time_start = time.time()
                    frame = frame.download()
                    download_time = time.time() - download_time_start
                else: 
                    rotate_time_start = time.time()
                    processor.rotate_90_ccw(self.stream)
                    processor.rotate(self.rotation_angle, self.stream)
                    rotate_time = time.time() - rotate_time_start
                    resize_time_start = time.time()
                    target_width = self.visualizer_rect.width
                    target_height = self.visualizer_rect.height
                    processor.resize(target_height, target_width, self.stream)
                    resize_time = time.time() - resize_time_start
                    flip_time_start = time.time()
                    processor.flip(0, self.stream)
                    flip_time = time.time() - flip_time_start
                    crop_time_start = time.time()
                    processor.crop(0, target_width, self.crop_top, target_height, self.stream)
                    crop_time = time.time() - crop_time_start    
                    scale_time_start = time.time()
                    processor.scale(self.scale_factor, self.stream)
                    scale_time = time.time() - scale_time_start
                    brightness_time_start = time.time()
                    processor.adjustBrightness(self.brightness, 0, self.stream)
                    brightness_time = time.time() - brightness_time_start
                    
                    texture_id = processor.bindToGLTexture()




                
           



                if self.frame_queue.full():
                    self.frame_queue.get_nowait()
                self.frame_queue.put(frame)

      


                total_time = time.time() - init_time
                # print(f"Decode: {decode_time}")
                # print(f"Color: {color_time}")
                # print(f"Convert: {convert_time}")
                # print(f"Rotate: {rotate_time}")
                # print(f"Resize: {resize_time}")
                # print(f"Flip: {flip_time}")
                # print(f"Crop: {crop_time}")
                # print(f"Scale: {resize_time}")
                # print(f"Brightness: {brightness_time}")
                
                print(f"Final: {total_time}")

                print(" ")
               

            except Exception as e:
                print(f"Error in _process_video: {e}")
                self.is_valid = False
                self.playing = False
             
                return
        
           
                

            # FPS sınırlama: Gerekirse bekle
            elapsed = time.perf_counter() - start_time
            sleep_time = self.frame_interval - elapsed
           
        
            if sleep_time > 0:
                time.sleep(sleep_time)


    def get_frame(self):
        if not self.is_valid:
            return

        if not self.frame_queue.empty():
            self.frame_buffer = self.frame_queue.get_nowait()

        return self.frame_buffer

    def play(self):
        self.playing = True

    def pause(self):
        self.playing = False
    def forward(self, seconds):
        frames_to_skip = int(seconds * self.video_fps)
        for _ in range(frames_to_skip):
            ret = self.video_capture.nextFrame(stream=self.stream)
    def rewind(self, seconds):
        self.video_capture = cv2.cudacodec.createVideoReader(self.video_file_path)
        self.forward(seconds)

    def get_video_duration(self):
        cap = cv2.VideoCapture(self.video_file_path)
        fps = cap.get(cv2.CAP_PROP_FPS)
        frame_count = cap.get(cv2.CAP_PROP_FRAME_COUNT)
        cap.release()
        print(frame_count / fps)
        return frame_count / fps
       



    def release(self):
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



















                