import moderngl
import numpy as np
import time
from utils import to_ndc

class Saber:
    def __init__(self, ctx, x, y, visualizer_rect, color1, color2, left_cutoff, right_cutoff, saber_y, speed=1.0):
        self.ctx = ctx
        self.x = x
        self.y = y
        self.visualizer_rect = visualizer_rect
        self.width = self.visualizer_rect.width
        self.height = 320
        self.color1 = color1
        self.color2 = color2
        self.left_cutoff = left_cutoff
        self.right_cutoff = right_cutoff
        self.speed = speed
        self.saber_y = 1 - (saber_y / 1080)

        self.start_time = time.time()

        self.prog = self.ctx.program(
            vertex_shader=open("ModernGL shaders/saber.vert").read(),
            fragment_shader=open("ModernGL shaders/saber.frag").read(),
        )


        self.prog['color1'].value = self.color1
        self.prog['color2'].value = self.color2
        self.prog['leftCutoff'].value = self.left_cutoff
        self.prog['rightCutoff'].value = self.right_cutoff
        self.prog['speed'].value = self.speed
        self.prog['saber_y'].value = self.saber_y

       

        x_left_ndc, y_top_ndc = to_ndc(self.x, self.y)
        x_right_ndc, _ = to_ndc(self.x + self.width, self.y)
        _, y_bottom_ndc = to_ndc(self.x, self.y + self.height)

       


        vertices = np.array([
            x_left_ndc,  y_top_ndc,
            x_right_ndc, y_top_ndc,
            x_left_ndc,  y_bottom_ndc,
            x_right_ndc, y_bottom_ndc,
        ], dtype='f4')

        self.vbo = self.ctx.buffer(vertices.tobytes())
        self.vao = self.ctx.simple_vertex_array(self.prog, self.vbo, 'in_pos')

    def render(self):
       # self.ctx.enable(moderngl.BLEND)
        elapsed = time.time() - self.start_time
        self.prog['time'].value = elapsed
        self.prog['color1'].value = self.color1
        self.prog['color2'].value = self.color2
        self.prog['leftCutoff'].value = self.left_cutoff
        self.prog['rightCutoff'].value = self.right_cutoff
        self.prog['speed'].value = self.speed
        self.prog['saber_y'].value = self.saber_y
        self.vao.render(moderngl.TRIANGLE_STRIP)
