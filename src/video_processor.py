import os, sys
os.add_dll_directory(r"C:\Users\ihsan\Projects\Synthesia\opencv\build\install\x64\vc17\bin")
os.add_dll_directory(r"C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v12.8\bin")
sys.path.insert(0, r"C:\Users\ihsan\Projects\Synthesia\opencv\build\python_loader\cv2\python-3.12")  
# system link required: 
# 
# 
# in cmd: mklink 
# "C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v12.8\bin\cudart64_120.dll" "C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v12.8\bin\cudart64_12.dll"
os.environ["CUDA_LAUNCH_BLOCKING"] = "1"

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
sys.path.insert(0, r"C:\Users\ihsan\Projects\Synthesia\VideoProcessingFramework\build\src\PyNvCodec\Release")  
import _PyNvCodec as nvc # type: ignore
import ctypes
import moderngl
import gc
from collections import deque



class Video:
    def __init__(self, ctx, video_file_path, visualizer_rect, start_time: float):
        self.video_file_path = video_file_path
        self.ctx = ctx
        self.visualizer_rect = visualizer_rect
        self.start_time = -start_time
        
        self.timestamp = 0
        self.current_frame_index = -1
        self.max_len_recent_frames = 120
        self.recent_frames = deque(maxlen=self.max_len_recent_frames)
        self.frame_index = 0

        # Thread safe locks
        self.decoder_lock = threading.Lock()
        self.demuxer_lock = threading.Lock()

        with self.demuxer_lock:
            self.demuxer = nvc.PyFFmpegDemuxer(self.video_file_path)
        with self.decoder_lock:
            self.video_capture = nvc.PyNvDecoder(video_file_path, 0, {'pixel_format': 'nv12'})

        self.video_fps = self.video_capture.Framerate()
        self.frame_interval = 1.0 / self.video_fps
   

        self.seek_in_progress = threading.Event()
        self.seek_done = threading.Event()
        self.seek_done.set()

        self.use_cudacodec = False # currently only works with PyNvCodec
        self.is_valid = True
        self.stream = cv2.cuda_Stream() if self.use_cudacodec else nvc.CudaStream()

        self._init_cuda()
        self._init_video_parameters() 
        self._init_opengl()

        self.converter = nvc.PySurfaceConverter(self.width, self.height, nvc.PixelFormat.NV12, nvc.PixelFormat.RGB, 0)
        self.cc_ctx = nvc.ColorspaceConversionContext(nvc.ColorSpace.BT_709, nvc.ColorRange.MPEG)
        self.video_frame_processor = nvc.VideoFrameProcessor()
        self.video_frame_processor.bind_to_gl_texture(self.texture_id)

        self.frame_queue = queue.Queue(maxsize=30)
        self.frame_buffer = None
        self.playing = True
        self.pending_surface = None

        self.duration = self.get_video_duration()
        
        self.start_video()

    
        # Buffer seek after initializing the program 
        self.seek(abs(self.start_time))
        



    def _init_cuda(self):
        try:
            self.device_id = 0
            cv2.cuda.setDevice(self.device_id)
            self.cuda_enabled = cv2.cuda.getCudaEnabledDeviceCount() > 0
            if self.cuda_enabled:
                print(f"CUDA enabled, using device {self.device_id}: {cv2.cuda.getDevice()}")
            else:
                print("CUDA enabled, but no devices found. Falling back to CPU.")
        except cv2.error as e:
            print(f"Error initializing CUDA: {e}\nFalling back to CPU.")
            self.cuda_enabled = False

    def _init_video_parameters(self):
        self.rotation_angle = 179.6
        self.scale_factor = 1.06
        self.crop_top = 200
        self.crop_bottom = 0
        self.x_offset = -27
        self.brightness = 0.5
        self.target_fps = self.video_fps
        self.dropped_frames = 0

    def _init_opengl(self):
        vertices = np.array([
            0.0, 0.0, 0.0, 0.0,
            1.0, 0.0, 1.0, 0.0,
            0.0, 1.0, 0.0, 1.0,
            1.0, 1.0, 1.0, 1.0
        ], dtype='f4')

        self.prog = self.ctx.program(
            vertex_shader=open("ModernGL shaders/video.vert").read(),
            fragment_shader=open("ModernGL shaders/video.frag").read(),
        )
        self.vao = self.ctx.vertex_array(
            self.prog,
            [(self.ctx.buffer(vertices.tobytes()), '2f 2f', 'in_position', 'in_texcoord')]
        )

        self.width = self.video_capture.Width()
        self.height = self.video_capture.Height()
        self.texture_width = int(self.visualizer_rect.width * self.scale_factor)
        self.texture_height = 792
        self.texture = self.ctx.texture((self.texture_width, self.texture_height), components=4, dtype='f1')
        self.texture.repeat_x = False
        self.texture.repeat_y = False
        self.texture.filter = (moderngl.LINEAR, moderngl.LINEAR)
        self.texture_id = self.texture.glo

    def _process_video(self):
        pkt = np.empty(0, dtype=np.uint8)
        while self.is_valid:
            if self.seek_in_progress.is_set():
                self.seek_done.wait()
             

            if not self.playing:
                time.sleep(0.01)
                continue

            start_time = time.perf_counter()
            try:
                if self.use_cudacodec:
                    ret, frame = self.cudacodec.nextFrame()
                    if not ret:
                        continue
                    frame = self._process_cudacodec_frame(frame)
                    frame = frame.download()
                else:
                   
    
                    if 0 <= self.current_frame_index < len(self.recent_frames) - 1:
                        surface = self.recent_frames[self.current_frame_index]
             
                     
                
                        with self.decoder_lock:
                            self.pending_surface = surface
                       
                            self._process_nvcodec_frame(self.pending_surface)
                          
                    else:
                        with self.demuxer_lock:
                            if not self.demuxer.DemuxSinglePacket(pkt):
                                continue
                        try:
                            with self.decoder_lock:
                                surface = self.video_capture.DecodeSurfaceFromPacket(pkt)
                                self.frame_index += 1
                                
                        except Exception as decode_err:
                        
                            # Decoder'ı yeniden oluştur
                            with self.decoder_lock:
                                self.video_capture = nvc.PyNvDecoder(self.video_file_path, self.device_id, {'pixel_format':'nv12'})
                            continue
               
                        if surface.Empty():
                            continue

                        
                        
                        surface = self.converter.Execute(surface, self.cc_ctx)
                        
                        self.recent_frames.append(surface.Clone())
                        with self.decoder_lock:
                            self.pending_surface = surface
                            self._process_nvcodec_frame(self.pending_surface)
                
                self.current_frame_index = min(self.current_frame_index + 1, self.max_len_recent_frames - 1)
                if self.frame_queue.full():
                    self.frame_queue.get_nowait()
                self.frame_queue.put(self.pending_surface)
                

            except Exception as e:
                print(f"Error in _process_video: {e}")
                self.is_valid = False
                self.playing = False
                return

            

            elapsed = time.perf_counter() - start_time
            sleep_time = self.frame_interval - elapsed

          
            if sleep_time > 0:
                time.sleep(sleep_time)

    def _process_cudacodec_frame(self, frame):
        width, height = frame.size()
        frame = cv2.cuda.transpose(frame, stream=self.stream)
        width, height = height, width
        center = (width / 2, height / 2)
        M = cv2.getRotationMatrix2D(center, self.rotation_angle, 1)
        frame = cv2.cuda.warpAffine(frame, M, (width, height), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT, stream=self.stream)
        frame = cv2.cuda.resize(frame, (self.visualizer_rect.height, self.visualizer_rect.width), interpolation=cv2.INTER_LINEAR, stream=self.stream)
        frame = frame.colRange(self.crop_top, frame.size()[0])
        frame = cv2.cuda.resize(frame, dsize=(0, 0), fx=self.scale_factor, fy=self.scale_factor, interpolation=cv2.INTER_LINEAR, stream=self.stream)
        frame = cv2.cuda.cvtColor(frame, cv2.COLOR_BGRA2RGB, stream=self.stream)
        frame = cv2.cuda.addWeighted(frame, self.brightness, frame, 0, 0, stream=self.stream)
        return frame

    def _process_nvcodec_frame(self, surface):
        self.video_frame_processor.update(surface)
        self.video_frame_processor.rotate(self.rotation_angle, self.stream)
        self.video_frame_processor.resize(int(self.visualizer_rect.width), int(self.visualizer_rect.height), self.stream)
        self.video_frame_processor.crop(0, int(self.visualizer_rect.width), self.crop_top, int(self.visualizer_rect.height), self.stream)
        self.video_frame_processor.scale(self.scale_factor, self.stream)
        self.video_frame_processor.adjustBrightness(self.brightness, 0, self.stream)
        self.video_frame_processor.convertColor(cv2.COLOR_RGB2RGBA, self.stream)

    def get_frame(self):
        try:
           # print(f"Getting surface: {self.current_frame_index}" )
            return self.frame_queue.get_nowait()
        except queue.Empty:
            return None

    def render(self, frame_time):
     
        surface = self.get_frame()
        if surface is not None:
            self.video_frame_processor.copy_to_texture() 
        
        self.texture.use(location=0)
        self.prog['screen_size'].value = (1920, 1080)
        self.prog['position'].value = (self.visualizer_rect.x + self.x_offset, keys[0].y)
        self.prog['size'].value = (self.texture_width, 792)
        self.prog['frame_pos'].value = (self.visualizer_rect.x, keys[0].y)
        self.prog['frame_size'].value = (self.texture_width, 320)
        self.vao.render(moderngl.TRIANGLE_STRIP)

        if self.playing:
            self.timestamp += frame_time

 

    def start_video(self):
        self.process_thread = threading.Thread(target=self._process_video, daemon=True)
        self.process_thread.start()
  

    def seek(self, seconds: float, render_after_seek=False):
        "Seek to timestamp"
        self.timestamp = seconds
      
        self.recent_frames.clear()
        self.current_frame_index = -1
     

        self.seek_in_progress.set()
        self.seek_done.clear()
        was_playing = self.playing
        self.playing = False
        with self.frame_queue.mutex:
            self.frame_queue.queue.clear()

        pkt = np.empty(0, dtype=np.uint8)
        seek_ctx = nvc.SeekContext(seconds, nvc.SeekMode.PREV_KEY_FRAME)
        with self.demuxer_lock:
            success = self.demuxer.Seek(seek_ctx, pkt)
            self.frame_index = int((seek_ctx.out_frame_pts / 89.900) * self.frame_interval)
        if not success:
           
            self.playing = True
            self.seek_in_progress.clear()
            self.seek_done.set()
            return

       

        for _ in range(1):
            with self.decoder_lock:
                surface = self.video_capture.DecodeSurfaceFromPacket(pkt)

        if render_after_seek and not surface.Empty():
            surface = self.converter.Execute(surface, self.cc_ctx)
            self.pending_surface = surface
            self._process_nvcodec_frame(self.pending_surface)
            self.frame_queue.put(self.pending_surface)
    

        self.playing = True if was_playing else False
        self.seek_in_progress.clear()
        self.seek_done.set()
       


    def get_video_duration(self):
        cap = cv2.VideoCapture(self.video_file_path)
        fps = cap.get(cv2.CAP_PROP_FPS)
        frame_count = cap.get(cv2.CAP_PROP_FRAME_COUNT)
        cap.release()
        return frame_count / fps

    def step_forward(self):
        "Goes one frame forward"
        if self.seek_in_progress.is_set():
            return

        if self.current_frame_index < len(self.recent_frames) - 1:
            self.current_frame_index += 1
            surface = self.recent_frames[self.current_frame_index]
        else:
            pkt = np.empty(0, dtype=np.uint8)
            with self.demuxer_lock:
                if not self.demuxer.DemuxSinglePacket(pkt):
                    return

            with self.decoder_lock:
                try:
                    surface = self.video_capture.DecodeSurfaceFromPacket(pkt)
                    self.frame_index += 1
                except Exception:
                    self.video_capture = nvc.PyNvDecoder(self.video_file_path, self.device_id, {'pixel_format': 'nv12'})
                    return

            if surface.Empty():
                return

            surface = self.converter.Execute(surface, self.cc_ctx)
            surface = surface.Clone()
            self.recent_frames.append(surface)
            self.current_frame_index = len(self.recent_frames) - 1

        self.pending_surface = surface
        self._process_nvcodec_frame(surface)

        if self.frame_queue.full():
            self.frame_queue.get_nowait()
        self.frame_queue.put(surface)
        self.timestamp += self.frame_interval
   

    def step_backward(self):
        "Goes one frame backwards if recent_frames is not empty. Otherwise seeks 0.5 seconds backwards"
        if self.seek_in_progress.is_set():
            return

        if self.current_frame_index > 0:
            self.current_frame_index -= 1
            surface = self.recent_frames[self.current_frame_index]
            self.frame_index -= 1
        
            self.pending_surface = surface
            self._process_nvcodec_frame(surface)
            

            if self.frame_queue.full():
                self.frame_queue.get_nowait()
            self.frame_queue.put(surface)
            self.timestamp -= self.frame_interval
        else:
            self.seek(self.timestamp - 0.5, render_after_seek=True)
       










                
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
