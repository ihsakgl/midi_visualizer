import numpy as np
import moderngl

class Light:
    def __init__(self, position_px, color, intensity, radius_px, key_index, scale_multiplier):
        self.position_px = position_px  # (x, y)
        self.color = color              # (r, g, b)
        self.intensity = intensity * scale_multiplier
        self.radius_px = radius_px * scale_multiplier
        self.key_index = key_index
     

class LightManager:
    MAX_LIGHTS = 88

    def __init__(self, ctx: moderngl.Context, screen_width: int, screen_height: int):
        self.ctx = ctx
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.lights = []

        with open("ModernGL shaders/light.vert") as f:
            vert_src = f.read()
        with open("ModernGL shaders/light.frag") as f:
            frag_src = f.read()
        self.program = self.ctx.program(vertex_shader=vert_src, fragment_shader=frag_src)

        quad = np.array([
            -1.0, -1.0,
             1.0, -1.0,
            -1.0,  1.0,
             1.0,  1.0,
        ], dtype='f4')
        self.quad_vbo = self.ctx.buffer(quad.tobytes())
        self.quad_vao = self.ctx.simple_vertex_array(self.program, self.quad_vbo, 'in_position')

    def add_light(self, light: Light):
        if len(self.lights) < self.MAX_LIGHTS:
            self.lights.append(light)

    def clear_lights(self):
        self.lights.clear()

  

    

    def render(self, scene_tex: moderngl.Texture):
        num = len(self.lights)
        self.program['num_lights'].value = num

        # Prepare Arrays
        pos_arr   = np.zeros((self.MAX_LIGHTS, 2), dtype='f4')
        col_arr   = np.zeros((self.MAX_LIGHTS, 3), dtype='f4')
        inten_arr = np.zeros((self.MAX_LIGHTS,),   dtype='f4')
        rad_arr   = np.zeros((self.MAX_LIGHTS,),   dtype='f4')
        
        for i, L in enumerate(self.lights):
            pos_arr[i]   = (L.position_px[0]/self.screen_width,
                            1.0 - L.position_px[1]/self.screen_height)
            col_arr[i]   = L.color
            inten_arr[i] = L.intensity
            rad_arr[i]   = L.radius_px / max(self.screen_width, self.screen_height)

        # Apply values
        self.program['u_light_pos'].value   = tuple((float(x), float(y)) for x, y in pos_arr)
        self.program['u_light_col'].value   = tuple((float(r), float(g), float(b)) for r, g, b in col_arr)
        self.program['u_light_inten'].value = tuple(float(v) for v in inten_arr)
        self.program['u_light_rad'].value   = tuple(float(v) for v in rad_arr)

        # Render
        scene_tex.use(location=0)
        self.program['screen_texture'].value = 0
        self.quad_vao.render(moderngl.TRIANGLE_STRIP)
