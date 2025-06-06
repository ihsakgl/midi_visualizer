import numpy as np
from PIL import Image, ImageDraw, ImageFont
import moderngl
from utils import is_colliding

class UI:
    def __init__(self, ctx, width, height, video, font_path="arial.ttf"):
        self.ctx = ctx
        self.width = width
        self.height = height
        self.fps_counter = Text(ctx, width, height, font_path=font_path, font_size=24)
        self.video_seeker = SeekBar(self.ctx, 50, 300, 400, 50, video)
        

    def update_fps_text(self, fps):
        self.fps_counter.update_text(f"FPS: {fps:.2f}")

    def render(self):
        self.fps_counter.render(100, 500)
        self.video_seeker.render()

    def press_event(self, x, y):
        if is_colliding(self.video_seeker, x, y): self.video_seeker.mouse_press(x, y)
    
    def release_event(self, x, y):
        if self.video_seeker.dragging: self.video_seeker.mouse_release()

    def move_event(self, x, y):
        if is_colliding(self.video_seeker, x, y): self.video_seeker.mouse_move(x, y)

    def resize(self, width, height):
        self.video_seeker.update_window_size(width, height)


class Text:
    def __init__(self, ctx: moderngl.Context, screen_width: int, screen_height: int,
                 font_path: str = "arial.ttf", font_size: int = 24, color=(255, 255, 255)):
        self.ctx = ctx
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.font_path = font_path
        self.font_size = font_size
        self.color = color

        self.current_text = None
        self.texture = None
        self.text_width = 0
        self.text_height = 0

        # Shader program
        self.prog = self.ctx.program(
            vertex_shader="""
                #version 330
                uniform vec2 screen_size;
                in vec2 in_position;
                in vec2 in_texcoord;
                out vec2 v_texcoord;
                void main() {
                    vec2 pos = in_position;
                    pos.y = screen_size.y - pos.y;  // y'yi ters çevir
                    pos = (pos / screen_size) * 2.0 - 1.0;
                    gl_Position = vec4(pos.x, pos.y, 0.0, 1.0);
                    v_texcoord = in_texcoord;
                }
            """,
            fragment_shader="""
                #version 330
                uniform sampler2D tex;
                in vec2 v_texcoord;
                out vec4 frag_color;
                void main() {
                    vec4 color = texture(tex, v_texcoord);
                    frag_color = color;
                }
            """
        )

        self.quad_buffer = self.ctx.buffer(reserve=4 * 4 * 4)  # 4 vertex * (2+2) float32
        self.vao = self.ctx.vertex_array(
            self.prog,
            [(self.quad_buffer, "2f 2f", "in_position", "in_texcoord")]
        )

    def update_text(self, text: str):
        if text == self.current_text:
            return  # Aynıysa tekrar oluşturma

        self.current_text = text
        font = ImageFont.truetype(self.font_path, self.font_size)
        bbox = font.getbbox(text)
        width = bbox[2] - bbox[0]
        height = bbox[3] - bbox[1]

        self.text_width = width
        self.text_height = height

        image = Image.new("RGBA", (width, height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(image)
        draw.text((0, -bbox[1]), text, font=font, fill=self.color + (255,))

        img_data = np.array(image)[..., ::-1].copy()  # RGBA -> ABGR

        if self.texture:
            self.texture.release()

        self.texture = self.ctx.texture((width, height), 4, img_data.tobytes())
        self.texture.build_mipmaps()

    def render(self, x: int = 10, y: int = 10):
        if self.texture is None:
            return

        px, py = x, self.screen_height - y - self.text_height  # üstten 0, soldan 0 koordinat sistemi

        vertices = np.array([
            px,     py,     0.0, 0.0,
            px + self.text_width, py,     1.0, 0.0,
            px,     py + self.text_height, 0.0, 1.0,
            px + self.text_width, py + self.text_height, 1.0, 1.0,
        ], dtype='f4')

        self.quad_buffer.write(vertices.tobytes())
        self.prog['screen_size'].value = (self.screen_width, self.screen_height)

        self.texture.use()
        self.vao.render(moderngl.TRIANGLE_STRIP)

class SeekBar:
    def __init__(self, ctx: moderngl.Context, x: int, y: int, width: int, height: int, video):
        self.ctx = ctx
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.position = 0.0       # current play position in seconds
        self.relative_x = 0.0
        self.progress = 0.0
        self.video = video
        self.dragging = False

        self.bg_color = (0.5, 0.4, 0.4)
        self.fill_color = (0.7, 0.7, 0.7)
        self.thumb_color = (1.0, 1.0, 1.0)

        # Load shader program
        self.prog = self.ctx.program(
            vertex_shader='''
                #version 330
                in vec2 in_position;
                uniform vec2 u_position;
                uniform vec2 u_size;
                uniform vec2 u_window_size;
                void main() {
                    vec2 pos = in_position * u_size + u_position;
                    // Normalize to clip space (-1 to 1)
                    vec2 clip = pos / u_window_size * 2.0 - 1.0;
                    // Flip Y axis (OpenGL coordinates)
                    clip.y = -clip.y;
                    gl_Position = vec4(clip, 0.0, 1.0);
                }
            ''',
            fragment_shader='''
                #version 330
                uniform vec3 u_color;
                out vec4 f_color;
                void main() {
                    f_color = vec4(u_color, 1.0);
                }
            '''
        )

        vertices = np.array([
            0.0, 0.0,
            1.0, 0.0,
            0.0, 1.0,
            1.0, 1.0,
        ], dtype='f4')

        self.vbo = self.ctx.buffer(vertices.tobytes())
        self.vao = self.ctx.simple_vertex_array(self.prog, self.vbo, 'in_position')

        self.window_size = (ctx.screen.width, ctx.screen.height)


    def update_window_size(self, width, height):
        self.window_size = (width, height)

    def set_position(self, pos_sec):
        # Clamp to duration
        self.position = max(0.0, min(pos_sec, self.video.duration))

    def get_position(self):
        return self.position

    def render(self):
        if not self.dragging:
            self.position = self.video.timestamp
            self.progress = self.position / self.video.duration

        self.prog['u_position'].value = (self.x, self.y + self.height / 3)
        self.prog['u_size'].value = (self.width, self.height / 3)
        self.prog['u_color'].value = self.bg_color
        self.prog['u_window_size'].value = self.window_size
        self.vao.render(moderngl.TRIANGLE_STRIP)

        # Draw filled bar 
        fill_width = (self.position / self.video.duration) * self.width
        self.prog['u_position'].value = (self.x, self.y + self.height / 3)
        self.prog['u_size'].value = (fill_width, self.height / 3)
        self.prog['u_color'].value = self.fill_color
        self.vao.render(moderngl.TRIANGLE_STRIP)

        # Draw thumb 
        thumb_size = self.height
        thumb_x = self.x + fill_width - thumb_size / 2
        thumb_y = self.y

        self.prog['u_position'].value = (thumb_x, thumb_y)
        self.prog['u_size'].value = (thumb_size, thumb_size)
        self.prog['u_color'].value = self.thumb_color
        self.vao.render(moderngl.TRIANGLE_STRIP)
    
       

    def mouse_press(self, x, y):
        # Thumb dragging
        if self._point_in_thumb(x, y):
            self.dragging = True
            return True
        # Update pos when clicking bar
        if self._point_in_bar(x, y):
            self._update_position_from_x(x)
            return True
        return False

    def mouse_release(self):
        self.dragging = False
        self.video.seek(self.progress * self.video.duration, not self.video.playing)


    def mouse_move(self, x, y):
        if self.dragging:
            self._update_position_from_x(x)
            return True
        return False

    def _point_in_thumb(self, px, py):
        fill_width = (self.position / self.video.duration) * self.width
        thumb_size = self.height
        thumb_x = self.x + fill_width - thumb_size / 2
        thumb_y = self.y
        return (thumb_x <= px <= thumb_x + thumb_size) and (thumb_y <= py <= thumb_y + thumb_size)

    def _point_in_bar(self, px, py):
        return (self.x <= px <= self.x + self.width) and (self.y <= py <= self.y + self.height)

    def _update_position_from_x(self, px):
        relative_x = px - self.x
        relative_x = max(0, min(relative_x, self.width))
        self.position = (relative_x / self.width) * self.video.duration
        self.progress = relative_x / self.width


