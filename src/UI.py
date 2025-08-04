import numpy as np
from PIL import Image, ImageDraw, ImageFont
import moderngl
import json
import os

from utils import is_colliding
import time
from color_picker import ColorPicker, ColorSelector

class UI:
    def __init__(self, ctx, width, height, video, app, font_path="arial.ttf"):
        self.ctx = ctx
        self.width = width
        self.height = height
        self.app = app
        self.is_active = True
        self.fps_counter = Text(ctx, width, height, font_path=font_path, font_size=11)
        self.video_seeker = SeekBar(self.ctx, self.app.visualizer.rect.x + 50, self.app.visualizer.rect.y + self.app.visualizer.rect.height + 75, self.app.visualizer.rect.width - 100, 50, video, self.app)
        self.current_time_text = Text(ctx, width, height, font_path=font_path, font_size=11)

       
        self.video_x_offset_input = InputField(self.ctx, 50, 50, 100, 25, "number", str(video.x_offset), "X offset")
        self.video_x_offset_input.action = lambda input_field: setattr(video, "x_offset", float(input_field.current_text))

        self.rotation_angle_input = InputField(self.ctx, 50, 100, 100, 25, "number", str(video.rotation_angle), "Rotation angle")
        self.rotation_angle_input.action = lambda input_field: setattr(video, "rotation_angle", float(input_field.current_text))

        self.scale_factor_input = InputField(self.ctx, 50, 150, 100, 25, "number", str(video.scale_factor), "Scale factor")
        self.scale_factor_input.action = lambda input_field: (setattr(video, "scale_factor", float(input_field.current_text)), video._update_texture(True))

        self.crop_top_input = InputField(self.ctx, 200, 50, 100, 25, "number", str(video.crop_top), "Crop from top")
        self.crop_top_input.action = lambda input_field: setattr(video, "crop_top", float(input_field.current_text))

        self.brightness_input = InputField(self.ctx, 200, 100, 100, 25, "number", str(video.brightness), "Brightness")
        self.brightness_input.action = lambda input_field: setattr(video, "brightness", float(input_field.current_text))

        self.inputs = [
            self.video_x_offset_input, 
            self.rotation_angle_input,
            self.scale_factor_input,
            self.crop_top_input,
            self.brightness_input
        ]

        self.color_picker = ColorPicker(self.ctx, 50, 200, 300, 300)
        self.color_selector = ColorSelector(self.ctx, 50, 550, 300, 30, 5, self)

        self.load_input_settings()

        self.video_timestamp_text = Text(self.ctx, width, height, font_path=font_path, font_size=11)

    def update(self, fps):
        if not self.is_active: return
        self.fps_counter.update_text(f"FPS: {fps:.2f}")
        self.current_time_text.update_text(f"Current time: {self.app.current_time:.4f}")
        self.video_timestamp_text.update_text(f"Video timestamp: {self.app.video.timestamp:.4f}")

    def render(self):
        if not self.is_active: return
        self.fps_counter.render(20, 1000)
        self.current_time_text.render(120, 1000)
        self.video_timestamp_text.render(270, 1000)

        self.video_seeker.render()
        self.color_picker.render()
        self.color_selector.render()

        for input in self.inputs:
            input.render()

    def press_event(self, x, y):
        if not self.is_active: return
        if is_colliding(self.video_seeker, x, y): self.video_seeker.mouse_press(x, y)

        for input in self.inputs:
            if is_colliding(input, x, y):
                input.mouse_press(x, y)
            else:
                input.deactivate()

        if is_colliding(self.color_picker, x, y):
            color = self.color_picker.get_color_at_pixel(x, y)
            self.color_selector.set_selected_color(color)
            self.app.visualizer.colors[self.color_selector.get_active_selection_index()] = color
            self.app.visualizer.update_colors(self.color_selector.get_selected_color(0), self.color_selector.get_selected_color(1))


        selected_index = self.color_selector.contains_point_for_selection(x, y)
        if not is_colliding(self.color_picker, x, y):
            self.color_selector.set_active_selection_index(selected_index)
    
    def release_event(self, x, y):
        if not self.is_active: return
        if self.video_seeker.dragging: self.video_seeker.mouse_release()

    def move_event(self, x, y):
        if not self.is_active: return
        if is_colliding(self.video_seeker, x, y): self.video_seeker.mouse_move(x, y)
        if is_colliding(self.color_picker, x, y): 
            color = self.color_picker.get_color_at_pixel(x, y)
            self.color_selector.set_selected_color(color)
            self.app.visualizer.colors[self.color_selector.get_active_selection_index()] = color
            self.app.visualizer.update_colors(self.color_selector.get_selected_color(0), self.color_selector.get_selected_color(1))

    def resize(self, width, height):
        if not self.is_active: return
        self.video_seeker.update_window_size(width, height)

    def keyboard_event(self, key, action, wnd):
        if not self.is_active: return
        for input in filter(lambda input: input.active, self.inputs):
            input.keyboard_input(key, action, wnd)

    def load_input_settings(self, path="settings/settings.json"):
        if os.path.exists(path):
            with open(path, "r") as f:
                try:
                    settings = json.load(f)

                    # Load inputs
                    for input_field in self.inputs:
                        label = input_field.label.current_text
                        if label in settings:
                            input_field.set_text(str(settings[label]))
                            input_field.action(input_field)  # Apply input values

                    # Upload colors
                    if "colors" in settings and isinstance(settings["colors"], list):
                        color_list = settings["colors"]
                        if len(color_list) == 2:
                            self.app.visualizer.update_colors(color_list[0], color_list[1])
                            self.color_selector.selected_colors = [color_list[0], color_list[1]]

                except json.JSONDecodeError:
                    print("Ayarlar dosyası okunamadı. Biçimi bozulmuş olabilir.")

    def save_input_settings(self, path="settings/settings.json"):
        settings = {}
        for input_field in self.inputs:
            label = input_field.label.current_text
            settings[label] = input_field.get_text()

        settings["colors"] = [
            list(self.app.visualizer.colors[0]), 
            list(self.app.visualizer.colors[1]),
        ]

        with open(path, "w") as f:
            json.dump(settings, f, indent=4)

  






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
            return

        self.current_text = text
        font = ImageFont.truetype(self.font_path, self.font_size)
        ascent, descent = font.getmetrics()
        height = ascent + descent

        # En fazla genişliği almak için gerçek metin genişliğini kullanıyoruz
        bbox = font.getbbox(text)
        width = bbox[2] - bbox[0]

        self.text_width = width
        self.text_height = height

        # bbox[1] genelde negatif olabilir (ascender için)
        image = Image.new("RGBA", (width, height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(image)
        draw.text((0, descent // 2), text, font=font, fill=self.color + (255,))

        img_data = np.array(image).copy()  # RGBA -> ABGR

        if self.texture:
            self.texture.release()

        self.texture = self.ctx.texture((width, height), 4, img_data.tobytes())
        self.texture.filter = (moderngl.NEAREST, moderngl.NEAREST)
        self.texture.repeat_x = False
        self.texture.repeat_y = False
        self.texture.build_mipmaps()



    def render(self, x: int = 10, y: int = 10):
        self.ctx.enable(moderngl.BLEND)
        self.ctx.blend_func = (
            moderngl.SRC_ALPHA,
            moderngl.ONE_MINUS_SRC_ALPHA,
            moderngl.ONE,
            moderngl.ONE_MINUS_SRC_ALPHA
        )
        if self.texture is None:
            return

      

        vertices = np.array([
            x,     y,     0.0, 0.0,
            x + self.text_width, y,     1.0, 0.0,
            x,     y + self.text_height, 0.0, 1.0,
            x + self.text_width, y + self.text_height, 1.0, 1.0,
        ], dtype='f4')

        self.quad_buffer.write(vertices.tobytes())
        self.prog['screen_size'].value = (self.screen_width, self.screen_height)

        self.texture.use()
        
        
        self.vao.render(moderngl.TRIANGLE_STRIP)

class SeekBar:
    def __init__(self, ctx: moderngl.Context, x: int, y: int, width: int, height: int, video, app):
        self.ctx = ctx
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.position = 0.0       # current play position in seconds
        self.relative_x = 0.0
        self.progress = 0.0
        self.video = video
        self.app = app
       


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



        desired_time = self.progress * self.video.duration


        old_ts = self.video.timestamp
        seeking_took = self.video.seek(desired_time)
        new_ts = self.video.timestamp

        delta = new_ts - old_ts

        self.app.navigated_time += delta
    
        self.audio_player.seek_relative(delta)

        

    

   

 


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
                                            
class InputField:
    
    def __init__(self, ctx, x, y, width, height, input_type, initial_text, label_text, font_path="assets/fonts/arial.ttf", font_size=24, 
                 text_color=(255, 255, 255), background_color=(0.0, 0.0, 0.0), border_color=(1.0, 1.0, 1.0)):
        self.ctx = ctx
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.input_type = input_type
        self.padding = self.height * 0.2
        self.font_size = self.height - 2 * self.padding
        self.text_color = text_color
        self.background_color = background_color
        self.border_color = border_color
        
        self.text_renderer = Text(ctx, ctx.screen.width, ctx.screen.height, font_path=font_path, font_size=self.font_size, color=text_color)
        self.label = Text(self.ctx, ctx.screen.width, ctx.screen.height, font_path=font_path, font_size=self.font_size, color=text_color)
        self.label.update_text(label_text)
        
        self.current_text = initial_text
        

        self.active = False
        self.cursor_visible = True
        self.last_cursor_toggle_time = time.time()
        self.cursor_blink_rate = 0.5 # seconds
        self.cursor_position = 0 # Index in self.current_text

        # Shader program for drawing the background rectangle
        self.prog_rect = self.ctx.program(
            vertex_shader='''
                #version 330
                in vec2 in_position;
                uniform vec2 u_position;
                uniform vec2 u_size;
                uniform vec2 u_window_size;
                void main() {
                    vec2 pos = in_position * u_size + u_position;
                    vec2 clip = pos / u_window_size * 2.0 - 1.0;
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
        rect_vertices = np.array([
            0.0, 0.0,
            1.0, 0.0,
            0.0, 1.0,
            1.0, 1.0,
        ], dtype='f4')
        self.rect_vbo = self.ctx.buffer(rect_vertices.tobytes())
        self.rect_vao = self.ctx.simple_vertex_array(self.prog_rect, self.rect_vbo, 'in_position')
        self._update_rendered_text()

    def activate(self):
        self.active = True
        self.cursor_visible = True
        self.last_cursor_toggle_time = time.time() # Reset cursor blink on activation
   

    def deactivate(self):
        self.active = False
        self.cursor_visible = False # Hide cursor when inactive

    def get_text(self):
        return self.current_text

    def set_text(self, text: str):
        self.current_text = text
        self.cursor_position = len(text)
        self._update_rendered_text()

    def _update_rendered_text(self):
        display_text = self.current_text
        if self.active and self.cursor_visible:
            # Insert cursor character for display
            display_text = display_text[:self.cursor_position] + "|" + display_text[self.cursor_position:]
        self.text_renderer.update_text(display_text)

    def keyboard_input(self, key, action, wnd):

        # Key press events
        if action == wnd.keys.ACTION_PRESS:
            if key == wnd.keys.BACKSPACE: 
                if self.cursor_position > 0:
                    self.current_text = self.current_text[:self.cursor_position - 1] + self.current_text[self.cursor_position:]
                    self.cursor_position -= 1
            elif key == wnd.keys.DELETE: 
                if self.cursor_position < len(self.current_text):
                    self.current_text = self.current_text[:self.cursor_position] + self.current_text[self.cursor_position + 1:]
            elif key == wnd.keys.LEFT: 
                self.cursor_position = max(0, self.cursor_position - 1)
            elif key == wnd.keys.RIGHT: 
                self.cursor_position = min(len(self.current_text), self.cursor_position + 1)
            elif key == wnd.keys.ENTER: 
                if len(self.current_text) > 0: self.action(self)
            else:
                char_key = chr(key)
                if self.input_type == "text" and char_key.isalpha():
                    pass
                elif self.input_type == "number" and (char_key.isdigit() or (char_key == "-" and self.cursor_position == 0) or (char_key == "." and not self.current_text.__contains__("."))):
                    pass
                else: 
                    char_key = ""
                    
                    
                self.current_text = self.current_text[:self.cursor_position] + char_key + self.current_text[self.cursor_position:]
                if char_key != "": self.cursor_position += 1
            
            self._update_rendered_text() # Update text after any modification
            self.cursor_visible = True # Reset cursor blink on key press
            self.last_cursor_toggle_time = time.time()

    def mouse_press(self, x, y):
        # Check if the click is within the input field's bounds
        if self.x <= x <= self.x + self.width and self.y <= y <= self.y + self.height:
            self.activate()
            # You could add logic here to set the cursor position based on click x
            # For simplicity, cursor goes to end of text on click for now.
            self.cursor_position = len(self.current_text)
            self._update_rendered_text()
            return True
        return False

    def render(self):
        # Update cursor blink state
        if self.active:
            if time.time() - self.last_cursor_toggle_time > self.cursor_blink_rate:
                self.cursor_visible = not self.cursor_visible
                self.last_cursor_toggle_time = time.time()
                self._update_rendered_text() # Re-render text to show/hide cursor

        # Draw background
        self.prog_rect['u_position'].value = (self.x, self.y)
        self.prog_rect['u_size'].value = (self.width, self.height)
        self.prog_rect['u_color'].value = self.background_color
        self.prog_rect['u_window_size'].value = (self.ctx.screen.width, self.ctx.screen.height)
        self.rect_vao.render(moderngl.TRIANGLE_STRIP)

        
        # Draw border if active
        if self.active:
            border_thickness = 2
            # Draw top border
            self.prog_rect['u_position'].value = (self.x, self.y)
            self.prog_rect['u_size'].value = (self.width, border_thickness)
            self.prog_rect['u_color'].value = self.border_color
            self.rect_vao.render(moderngl.TRIANGLE_STRIP)
            # Draw bottom border
            self.prog_rect['u_position'].value = (self.x, self.y + self.height - border_thickness)
            self.prog_rect['u_size'].value = (self.width, border_thickness)
            self.prog_rect['u_color'].value = self.border_color
            self.rect_vao.render(moderngl.TRIANGLE_STRIP)
            # Draw left border
            self.prog_rect['u_position'].value = (self.x, self.y)
            self.prog_rect['u_size'].value = (border_thickness, self.height)
            self.prog_rect['u_color'].value = self.border_color
            self.rect_vao.render(moderngl.TRIANGLE_STRIP)
            # Draw right border
            self.prog_rect['u_position'].value = (self.x + self.width - border_thickness, self.y)
            self.prog_rect['u_size'].value = (border_thickness, self.height)
            self.prog_rect['u_color'].value = self.border_color
            self.rect_vao.render(moderngl.TRIANGLE_STRIP)

        # Render text (with cursor if active)
        # Calculate text rendering position to be centered vertically and left-aligned
        text_x = self.x + 5 # Small padding from left
        text_y = self.y 
        self.text_renderer.render(text_x, text_y)
        self.label.render(self.x + 5, self.y - self.height)