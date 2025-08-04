import PyNvVideoCodec as nvc
import torch
import OpenGL.GL as gl
import gc

import pycuda.driver as cuda
import pycuda.gl
import subprocess


class GpuRecorder:
    def __init__(self, fbo, width, height, output_path):
        self.width       = width
        self.height      = height
        self.buffer_size = width * height * 4
        self.output_path = output_path
        self.fps = 60.0
        self.frame_interval = 1 / self.fps

        # ARGB + GPU input buffer modu
        self.encoder = nvc.CreateEncoder(
            width=width, height=height,
            fmt="ARGB", 
            usecpuinputbuffer=False,
            codec="h264", 
            fps=self.fps, 
            bitrate=20_000_000, # 20 Mbit/s
            preset="P4",
            rc="cbr"
        )

        tex = fbo.color_attachments[0].glo
        self.resource = pycuda.gl.RegisteredImage(
            int(tex),
            gl.GL_TEXTURE_2D,
            pycuda.gl.graphics_map_flags.READ_ONLY
        )

        self.output_file   = open(self.output_path + '.h264', 'wb')
        self.linear_buffer = cuda.mem_alloc(self.buffer_size)
        self.torch_tensor  = torch.empty((height, width, 4), dtype=torch.uint8, device='cuda')

        self.accumulator = 0.0
        self.interval = [0.0, 1.0]
        self.frames_encoded_in_a_second = 0


  



    def try_encoding_frame(self, frame_time, current_time):

        if self.accumulator >= self.frame_interval:
            
            self.encode_frame()
            
            exceeded_time = self.accumulator - self.frame_interval
            self.accumulator = exceeded_time
            # if self.interval[0] <= current_time < self.interval[1]:
            #     self.frames_encoded_in_a_second += 1
            # else:
            #     #print(self.frames_encoded_in_a_second)
            #     self.frames_encoded_in_a_second = 0
            #     self.interval[0] += 1.0
            #     self.interval[1] += 1.0


        self.accumulator += frame_time

   

      

    def encode_frame(self):

      

        mapped   = self.resource.map()
        cu_array = mapped.array(0, 0)

        # cuArray → linear GPU buffer
        copy = cuda.Memcpy2D()
        copy.set_src_array(cu_array)
        copy.set_dst_device(self.linear_buffer)
        copy.width_in_bytes = self.width * 4
        copy.height         = self.height
        copy(aligned=False)

        # linear buffer → Torch tensor 
        cuda.memcpy_dtod(
            self.torch_tensor.data_ptr(),
            int(self.linear_buffer),
            self.buffer_size
        )
        
      
        tensor_flipped = self.torch_tensor.flip(dims=[0])
        tensor_bgra    = tensor_flipped[..., [2, 1, 0, 3]].contiguous() 
      


        # Encode doğrudan GPU tensorü
        packet = self.encoder.Encode(tensor_bgra)
        if packet:
            self.output_file.write(bytearray(packet))

        mapped.unmap()
     
    

    


    def close(self):
        packet = self.encoder.EndEncode()
        if packet:
            self.output_file.write(bytearray(packet))
        self.output_file.close()

    def convert_to_mp4(self, audio_player):
        "Converts .h264 to .mp4. Currently does not support audio. Maybe add Audio in another program..."
        # ffmpeg2 -framerate 60 -i denemeler/deneme8.h264 -c:v copy denemeler/deneme8.mp4

        print('converting to mp4...')

        subprocess.run([
            'ffmpeg2',
            '-y',
            '-framerate', str(self.fps),
            '-i', self.output_path + '.h264',
            '-c:v', 'libx264',        # encoding
            '-pix_fmt', 'yuv420p',    # pixel format
            '-preset', 'ultrafast',   
            '-crf', '18',             # qualitiy. 51 worst, 0 best
            self.output_path + '.mp4'
        ])

        # ffmpeg2 -i denemeler/deneme9.mp4 -itsoffset 0 -i "assets/video/Recording 01-11 20.45.57.wav" -map 0:v -map 1:a -c:v copy -c:a aac -shortest denemeler/deneme9_audio.mp4

        # start_pos = audio_player.hit_time - audio_player.audio_starting_pos
       

        # subprocess.run([
        #     'ffmpeg2',
        #     '-i', self.output_path + '.mp4',
        #     '-itsoffset', str(start_pos),
        #     '-i', str(audio_player.audio_file_path),
        #     '-map', '0:v',
        #     '-map', '1:a',
        #     '-c:v', 'copy',
        #     '-c:a', 'aac',
        #     '-shortest', self.output_path + '_audio.mp4'
        # ])

    def release(self):
        del self.encoder
        self.encoder = None
        gc.collect()
        