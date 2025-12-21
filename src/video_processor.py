import os, sys 
# Adding .dll directories
os.add_dll_directory(r"C:\Users\ihsan\Projects\Synthesia\opencv\build\install\x64\vc17\bin")
os.add_dll_directory(r"C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v12.8\bin")
sys.path.insert(0, r"C:\Users\ihsan\Projects\Synthesia\opencv\build\python_loader\cv2\python-3.12")  

# system link required: 
# Type in cmd: 
# mklink "C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v12.8\bin\cudart64_120.dll" "C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v12.8\bin\cudart64_12.dll"

os.environ["CUDA_LAUNCH_BLOCKING"] = "1" # for seeing error messages

import cv2
import cv2.cuda
import cv2.cudacodec
import numpy as np
from visualizer import keys
import threading
import queue
import time
os.add_dll_directory(r"C:\libs\FFmpeg\bin")
sys.path.insert(0, r"C:\Users\ihsan\Projects\Synthesia\VideoProcessingFramework\build\src\PyNvCodec\Release")  
import _PyNvCodec as nvc # type: ignore
import moderngl
import gc
from collections import deque



class Video:
    def __init__(self, ctx, video_file_path, visualizer_rect, start_time: float):
        if os.path.exists(video_file_path) == False:
            self.is_valid = False
            return
        self.video_file_path = video_file_path
        self.ctx = ctx
        self.visualizer_rect = visualizer_rect
        self.start_time = -start_time
        
        self.timestamp = 0.0
        self.current_frame_index = -1
        self.max_len_recent_frames = 120
        self.recent_frames = deque(maxlen=self.max_len_recent_frames)
        self.frame_index = 0
        self.rendered_frames = 0

        # Thread safe locks
        self.decoder_lock = threading.Lock()
        self.demuxer_lock = threading.Lock()
        self.processor_lock = threading.Lock()

        with self.demuxer_lock:
            self.demuxer = nvc.PyFFmpegDemuxer(self.video_file_path)
        with self.decoder_lock:
            self.video_capture = nvc.PyNvDecoder(video_file_path, 0, {'pixel_format': 'nv12'})

        self.video_fps = 60.06
        self.frame_interval = 1.0 / self.video_fps
   

        self.seek_in_progress = threading.Event()
        self.seek_done = threading.Event()
        self.seek_done.set()
        

        self.use_cudacodec = False # currently only works with PyNvCodec
        self.is_valid = True
        self.stream = cv2.cuda_Stream() if self.use_cudacodec else nvc.CudaStream()
        self.video_frame_processor = nvc.VideoFrameProcessor()

        self.processing_done = threading.Event()
        
        self.updating_texture = False
        self._init_cuda()
        self._init_video_parameters() 
        self._init_opengl()

        

        self.converter = nvc.PySurfaceConverter(self.width, self.height, nvc.PixelFormat.NV12, nvc.PixelFormat.RGB, 0)
        self.cc_ctx = nvc.ColorspaceConversionContext(nvc.ColorSpace.BT_709, nvc.ColorRange.MPEG)
        
      

        self.frame_queue = queue.Queue(maxsize=30)
        self.frame_buffer = None
        self.playing = True
        self.pending_surface = None
        self.pending_frame = None

        self.duration = self.get_video_duration()

        self.frame_count = 0
        self.render_timer = 0
        self.video_start_time = time.perf_counter()
        
        

    
        # Buffer seek after initializing the program 
        if self.start_time > 0: self.seek(abs(self.start_time))
        

        self.frames_rendered_in_a_second = 0
        self.last_surface_index = 0
        self.interval = [0, 1]

        if self.start_time > 0:
            self.start_video()
        else:
            timer = threading.Timer(self.start_time, self.start_video)
            timer.start()

        self.recording = False
        

    def _init_cuda(self):
        try:
            self.device_id = 0
            cv2.cuda.setDevice(self.device_id)
            self.cuda_enabled = cv2.cuda.getCudaEnabledDeviceCount() > 0
            if self.cuda_enabled:
                print(f"CUDA enabled, using device {self.device_id}: {cv2.cuda.getDevice()}")
            else:
                print("CUDA enabled, but no devices found.")
        except cv2.error as e:
            print(f"Error initializing CUDA: {e}")
            self.cuda_enabled = False

    def _init_video_parameters(self):
        self.rotation_angle = 180.0
        self.scale_factor = 1.12
        self.crop_top = 150
        self.crop_bottom = 0
        self.x_offset = -85
        self.brightness = 0.4

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
        self._update_texture(False)
   
    def _update_texture(self, texture_is_init):
        
        self.updating_texture = True
   
        
        
        self.texture_width = int(self.visualizer_rect.width * self.scale_factor) + 1
        self.texture_height = int((self.visualizer_rect.height) * self.scale_factor) + 1 # NEEDS OPTIMIZATION

        with self.processor_lock:
            del self.video_frame_processor
            gc.collect()
            self.video_frame_processor = nvc.VideoFrameProcessor()
            self.video_frame_processor.set_output_size(self.texture_width, self.texture_height)

        if texture_is_init: 
            
            self.texture.release()
            
        self.texture = self.ctx.texture((self.texture_width, self.texture_height), components=4, dtype='f1')
        # print(self.texture.width, self.texture.height)
        self.texture.repeat_x = False
        self.texture.repeat_y = False
        self.texture.filter = (moderngl.LINEAR, moderngl.LINEAR)
        self.texture_id = self.texture.glo
        try:
            self.video_frame_processor.bind_to_gl_texture(self.texture_id)
        except Exception as e:
            print("bind_to_gl_texture failed:", e)
            self.is_valid = False

        self.updating_texture = False
        self.render_after_seek = False

    def _process_video(self):
        pkt = np.empty(0, dtype=np.uint8)
  

        while self.is_valid:
            if self.seek_in_progress.is_set():
                self.seek_done.wait()

            if not self.playing or self.frame_queue.full() or self.updating_texture:
                time.sleep(0.01)
                continue

            # now = time.perf_counter()
            # expected_time = self.video_start_time + self.frame_count * self.frame_interval
            # delay = expected_time - now

            # if delay > 0:
            #     time.sleep(delay)
            # elif delay < -0.1:
            #     # Zaman çizelgesinden sapma büyükse resetle
            #     #print(f"Gecikme tespit edildi: {abs(delay):.3f}s — zaman sıfırlanıyor.")
            #     self.video_start_time = time.perf_counter()
            #     self.frame_count = 0
            #     continue

            try:
                self.processing_done.clear()
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
                                
                                
                        except Exception as decode_err:
                            with self.decoder_lock:
                                print(f"Resetting decoder because of error: {decode_err}")
                                self.video_capture = nvc.PyNvDecoder(
                                    self.video_file_path, self.device_id, {'pixel_format': 'nv12'}
                                )
                            continue

                        if surface.Empty() or self.updating_texture:
                            #print("Surface empty")
                            continue

                        surface = self.converter.Execute(surface, self.cc_ctx)
                        self.recent_frames.append(surface.Clone())
                        with self.decoder_lock:
                            self.pending_surface = surface
                            self._process_nvcodec_frame(self.pending_surface)

                self.current_frame_index = min(self.current_frame_index + 1, self.max_len_recent_frames - 1)
                if self.frame_queue.full():
                    print("Surface getting nowait, queue is full")
                    self.frame_queue.get_nowait()
               
                self.frame_queue.put(self.pending_surface)
                self.processing_done.set()

           
            except Exception as e:
                print(f"Error in _process_video: {e}")
                self.is_valid = False
                self.playing = False
                return

            self.frame_count += 1

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
        with self.processor_lock:
            if hasattr(self, 'video_frame_processor'):
                self.video_frame_processor.update(surface)
                self.video_frame_processor.rotate(self.rotation_angle, self.stream)
                self.video_frame_processor.resize(int(self.visualizer_rect.width), int(self.visualizer_rect.height), self.stream)
                self.video_frame_processor.crop(0, int(self.visualizer_rect.width), int(self.crop_top), int(self.visualizer_rect.height), self.stream)
                self.video_frame_processor.scale(self.scale_factor, self.stream)
                self.video_frame_processor.adjustBrightness(self.brightness, 0, self.stream)
                self.video_frame_processor.convertColor(cv2.COLOR_RGB2RGBA, self.stream)
       
    def get_frame(self):
        try:
           # print(f"Getting surface: {self.current_frame_index}" )
            return self.frame_queue.get_nowait()
        except:
            self.render_timer += self.frame_interval
            self.timestamp += self.frame_interval
            print("Queue is empty, returning None")
            return None

    def render(self, delta_time, current_time):
        #print(f"Queue size: {self.frame_queue.qsize()}")
        #print(f"Frame index: {self.frame_index} at timestamp {self.timestamp} at current time: {current_time}")

        ## NOTE: Hizli encode modunda video 30 fps e düsüyor. Nedenini bul.

        if not self.is_valid:
            return
        
        if self.render_timer >= self.frame_interval:
            self.pending_frame = self.get_frame()
            if self.pending_frame.Empty(): print("Frame is empty")
            self.frame_index += 1
            exceeded_time = self.render_timer - self.frame_interval
            self.render_timer = exceeded_time
            self.rendered_frames += 1
            # print(f"Rendered frames: {self.rendered_frames} at time {current_time:.3f}s")  


        if self.recording and self.timestamp + self.start_time < current_time:
            self.step_forward()
            print("Stepping forward")


        if self.pending_frame is not None and self.is_valid:
            self.processing_done.wait()
            self.video_frame_processor.copy_to_texture() 

     
        self.texture.use(location=0)
        self.prog['screen_size'].value = (1920, 1080)
        self.prog['position'].value = (self.visualizer_rect.x + self.x_offset, keys[0].y)
        self.prog['size'].value = (self.texture_width, self.texture_height)
        self.prog['frame_pos'].value = (self.visualizer_rect.x, keys[0].y)
        self.prog['frame_size'].value = (self.texture_width, keys[0].y - self.visualizer_rect.y)
        self.vao.render(moderngl.TRIANGLE_STRIP)

        if self.playing:
            self.timestamp += delta_time 
            self.render_timer += delta_time 



  
    def start_video(self):
        self.process_thread = threading.Thread(target=self._process_video, daemon=True)
        self.process_thread.start()
  

    def seek(self, seconds: float):
        "Seek to timestamp"
        
        start = time.perf_counter()

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
            seeked_time_in_seconds = seek_ctx.out_frame_pts * self.demuxer.Timebase()
            self.timestamp = seeked_time_in_seconds
            self.frame_index = int(seeked_time_in_seconds / self.frame_interval)
        if not success:
           
            self.playing = True
            self.seek_in_progress.clear()
            self.seek_done.set()
            return
        with self.decoder_lock:
            if self.video_capture is not None:
                del self.video_capture
                self.video_capture = None
                gc.collect()
            self.video_capture = nvc.PyNvDecoder(self.video_file_path, 0, {'pixel_format': 'nv12'})


        last_decoded_surface = None

        try:
            with self.decoder_lock:
                last_decoded_surface = self.video_capture.DecodeSurfaceFromPacket(pkt)
            if not last_decoded_surface.Empty():
                # Update timestamp based on decoded surface PTS if available and accurate

                self.timestamp += self.frame_interval # Fallback if PTS not available/reliable
                self.frame_index += 1
                #print(f"Decoded I-frame for precise seek: {self.timestamp:.3f}s")
        except Exception as e:
            print(f"[seek] Error decoding initial I-frame packet: {e}")
            last_decoded_surface = None # Discard if decode failed

    
        while self.timestamp + self.frame_interval < seconds:
            with self.demuxer_lock:
                # If DemuxSinglePacket returns False, it means end of stream or error
                if not self.demuxer.DemuxSinglePacket(pkt):
                    print("[seek] Demux error or end of stream during precise forward decoding.")
                    break # Exit loop if no more packets
            
            try:
                with self.decoder_lock:
                    current_surface = self.video_capture.DecodeSurfaceFromPacket(pkt)
                
                if not current_surface.Empty():
                    last_decoded_surface = current_surface # Keep track of the last successful decode
                    if hasattr(last_decoded_surface, 'Pts') and self.demuxer.Timebase() > 0:
                        self.timestamp = last_decoded_surface.Pts() * self.demuxer.Timebase()
                    else:
                        self.timestamp += self.frame_interval 
                    self.frame_index += 1
                    # print(f"Forward decoded frame: {self.timestamp:.3f}s")
                else:
                    # print("Decoded empty surface during precise forward decoding, continuing.")
                    pass # Keep trying to decode until a valid surface is found
                    
            except Exception as decode_err:
                print(f"[seek] Error during precise forward decoding: {decode_err}. Resetting decoder and continuing.")
                with self.decoder_lock:
                    self.video_capture = nvc.PyNvDecoder(self.video_file_path, self.device_id, {'pixel_format': 'nv12'})
                pass # Try to demux and decode next packet
      
     
    

        self.playing = True if was_playing else False
        self.seek_in_progress.clear()
        self.seek_done.set()

        end = time.perf_counter()
        delta = end - start
      

        return delta
     
     




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
                success = self.demuxer.DemuxSinglePacket(pkt)
                if not success:
                    return
                
            

            with self.decoder_lock:
                try:
                    surface = self.video_capture.DecodeSurfaceFromPacket(pkt)
                    
                    self.frame_index += 1
                except Exception:
                    self.video_capture = nvc.PyNvDecoder(self.video_file_path, self.device_id, {'pixel_format': 'nv12'})
                    return
            
            if surface.Empty(): ########################################
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
       



    def get_video_duration(self):
        cap = cv2.VideoCapture(self.video_file_path)
        fps = cap.get(cv2.CAP_PROP_FPS)
        frame_count = cap.get(cv2.CAP_PROP_FRAME_COUNT)
        cap.release()
        return frame_count / fps

    def release(self):
        del self.video_capture
        self.video_capture = None
        gc.collect()




    