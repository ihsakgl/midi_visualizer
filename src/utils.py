"Here are some functions that I needed frequently"

def resize_objects(obj, base_width, base_height, new_width, new_height,
                   new_visualizer_rect, base_visualizer_rect, is_visualizer_element: bool):
    # Calculate scaling factors
    visualizer_scale_x = new_visualizer_rect.width / base_visualizer_rect.width
    visualizer_scale_y = new_visualizer_rect.height / base_visualizer_rect.height
    screen_scale_x = new_width / base_width
    screen_scale_y = new_height / base_height
    avg_screen_scale = (screen_scale_x + screen_scale_y) / 2

    # Decide which scale is going to be used
    scale_x = visualizer_scale_x if is_visualizer_element else screen_scale_x
    scale_y = visualizer_scale_y if is_visualizer_element else screen_scale_y

    # Update screen attributes
    if hasattr(obj, "screen_width"):
        obj.screen_width = new_width
    if hasattr(obj, "screen_height"):
        obj.screen_height = new_height
    if hasattr(obj, "visualizer_rect"):
        obj.visualizer_rect = new_visualizer_rect

    # Resizing
    if hasattr(obj, "x") and obj.x is not None:
        obj.x *= scale_x
    if hasattr(obj, "y") and obj.y is not None:
        obj.y *= scale_y
    if hasattr(obj, "width") and obj.width is not None:
        obj.width *= scale_x
    if hasattr(obj, "height") and obj.height is not None:
        obj.height *= scale_y
    if hasattr(obj, "radius") and obj.radius is not None:
        obj.radius *= avg_screen_scale

    if hasattr(obj, "x_offset"):
        obj.x_offset *= scale_x
    if hasattr(obj, "crop_top"):
        obj.crop_top *= scale_y
        obj.crop_top = int(obj.crop_top)


def is_colliding(element, mx, my):
    "Checks whether user has clicked a certain element with mouse"
    return mx >= element.x and my >= element.y and mx <= element.x + element.width and my <= element.y + element.height

def to_ndc(x_px, y_px):
    ndc_x = (2.0 * x_px / 1920) - 1.0
    ndc_y = 1.0 - (2.0 * y_px / 1080)
    return ndc_x, ndc_y

def create_quad(x, y, width, height, screen_width, screen_height):
    # OpenGL için normalize edilmiş koordinatlara dönüştür
    left   = (x / screen_width) * 2.0 - 1.0
    right  = ((x + width) / screen_width) * 2.0 - 1.0
    top    = 1.0 - (y / screen_height) * 2.0
    bottom = 1.0 - ((y + height) / screen_height) * 2.0

    return np.array([
        left,  bottom,
        right, bottom,
        left,  top,
        right, top,
    ], dtype='f4')


import moderngl
import numpy as np

class FullscreenQuad:
    def __init__(self, ctx):
        self.ctx = ctx

        self.prog = ctx.program(
            vertex_shader="""
                #version 330
                in vec2 in_vert;
                in vec2 in_uv;
                out vec2 v_uv;
                void main() {
                    v_uv = in_uv;
                    gl_Position = vec4(in_vert, 0.0, 1.0);
                }
            """,
            fragment_shader="""
                #version 330
                uniform sampler2D tex;
                in vec2 v_uv;
                out vec4 fragColor;
                void main() {
                    fragColor = texture(tex, v_uv);
                }
            """
        )

        vertices = np.array([
            # x, y, u, v
            -1.0, -1.0, 0.0, 0.0,
             1.0, -1.0, 1.0, 0.0,
            -1.0,  1.0, 0.0, 1.0,
             1.0,  1.0, 1.0, 1.0,
        ], dtype='f4')

        self.vbo = ctx.buffer(vertices.tobytes())
        self.vao = ctx.vertex_array(
            self.prog,
            [(self.vbo, '2f 2f', 'in_vert', 'in_uv')]
        )

        self.texture_uniform = self.prog['tex']

    def render(self, texture):
        texture.use(0)  # Texture'u bind et (slot 0)
        self.texture_uniform.value = 0
        self.vao.render(moderngl.TRIANGLE_STRIP)
