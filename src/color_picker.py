import numpy as np
import moderngl

# Built with ChatGPT

class ColorPicker:
    """
    Handles the rendering of the color gradient and picking a color from it.
    It does NOT manage selected colors or display rectangles.
    """
    def __init__(self, ctx: moderngl.Context, x: int, y: int, width: int, height: int):
        self.ctx = ctx
        self.x = x
        self.y = y
        self.width = width
        self.height = height

        # Framebuffer for color picking. Its dimensions match the picker.
        self.fbo = ctx.framebuffer(
            color_attachments=[ctx.texture((width, height), 4)]
        )

        # Vertices for a unit quad (0-1 range)
        self.quad = ctx.buffer(np.array([
            0.0, 0.0,  # Top-left
            1.0, 0.0,  # Top-right
            0.0, 1.0,  # Bottom-left
            1.0, 1.0,  # Bottom-right
        ], dtype='f4'))

        # Shader Program for generating the Color Picker gradient into FBO.
        # This shader's primary role is to draw the gradient INTO our FBO.
        self.fbo_render_prog = ctx.program(
            vertex_shader='''
                #version 330
                in vec2 in_vert;
                out vec2 uv;

                void main() {
                    uv = in_vert; // uv directly maps to in_vert for FBO texture generation
                    gl_Position = vec4(in_vert * 2.0 - 1.0, 0.0, 1.0); // Map to [-1,1] clip space
                }
            ''',
            fragment_shader='''
                #version 330
                in vec2 uv;
                out vec4 color;

                void main() {
                    color = vec4(uv.x, uv.y, 1.0 - uv.x * uv.y, 1.0);
                }
            '''
        )
        self.fbo_render_vao = ctx.simple_vertex_array(self.fbo_render_prog, self.quad, 'in_vert')

        # Shader Program for Displaying the FBO Texture on Screen.
        # This shader will simply draw a textured quad.
        self.display_prog = ctx.program(
            vertex_shader='''
                #version 330
                in vec2 in_vert;
                out vec2 uv;

                uniform vec2 screen_size;
                uniform vec4 display_rect; // x, y, width, height of where to draw the texture

                void main() {
                    uv = in_vert;

                    vec2 pixel_pos = vec2(
                        display_rect.x + in_vert.x * display_rect.z,
                        display_rect.y + in_vert.y * display_rect.w
                    );

                    vec2 ndc_pos = vec2(
                        (pixel_pos.x / screen_size.x) * 2.0 - 1.0,
                        1.0 - (pixel_pos.y / screen_size.y) * 2.0
                    );

                    gl_Position = vec4(ndc_pos, 0.0, 1.0);
                }
            ''',
            fragment_shader='''
                #version 330
                uniform sampler2D color_texture; // The texture from our FBO
                in vec2 uv;
                out vec4 color;

                void main() {
                    color = texture(color_texture, uv); // Sample the color from the texture
                }
            '''
        )
        self.display_vao = ctx.simple_vertex_array(self.display_prog, self.quad, 'in_vert')

        # Render the color gradient into the FBO ONCE during initialization
        self._render_picker_to_fbo()


    def _render_picker_to_fbo(self):
        """
        Renders the color picker gradient into its FBO.
        This should only be called once, or when picker dimensions change.
        """
        current_fbo = self.ctx.fbo
        current_viewport = self.ctx.viewport

        self.fbo.use()
        self.ctx.viewport = (0, 0, self.width, self.height)
        self.ctx.clear(0.0, 0.0, 0.0, 0.0)

        self.fbo_render_vao.render(moderngl.TRIANGLE_STRIP)

        current_fbo.use()
        self.ctx.viewport = current_viewport


    def render(self):
        """Renders the color picker widget to the screen."""
        # Display the Color Picker (from FBO texture)
        self.fbo.color_attachments[0].use(0) # Use texture unit 0

        self.display_prog['color_texture'].value = 0 # Tell shader to use texture from unit 0
        self.display_prog['screen_size'].value = self.ctx.screen.size
        self.display_prog['display_rect'].value = (self.x, self.y, self.width, self.height)
        # The viewport for rendering the widget itself should be the entire screen
        self.ctx.viewport = (0, 0, self.ctx.screen.width, self.ctx.screen.height)
        self.display_vao.render(moderngl.TRIANGLE_STRIP)


    def get_color_at_pixel(self, mouse_x: int, mouse_y: int) -> tuple[float, float, float] | None:
        """
        Reads the color from the FBO at the given mouse coordinates,
        relative to the picker's position.
        """
        # Convert mouse_x, mouse_y to coordinates relative to picker's top-left
        rel_x = int(mouse_x - self.x)
        rel_y = int(mouse_y - self.y)

        # Check if relative coordinates are within the picker's bounds
        if not (0 <= rel_x < self.width and 0 <= rel_y < self.height):
            return None

        # FBO's internal Y-axis is bottom-left, so we invert the relative Y for reading.
        

        data = self.fbo.read(components=3, alignment=1)
        img = np.frombuffer(data, dtype=np.uint8).reshape((self.height, self.width, 3))

        r, g, b = img[rel_y, rel_x]

        return (r / 255.0, g / 255.0, b / 255.0)

    def contains_point(self, x: int, y: int) -> bool:
        """Checks if a given point (x, y) is within the picker's bounds."""
        return (self.x <= x < self.x + self.width and
                self.y <= y < self.y + self.height)

    @property
    def rect(self):
        """Returns the (x, y, width, height) tuple for the picker's bounds."""
        return (self.x, self.y, self.width, self.height)

# --- ColorSelector Class ---
class ColorSelector:
    """
    Manages two selected colors, their display, active selection, and borders.
    It depends on a Moderngl context for rendering.
    """
    def __init__(self, ctx: moderngl.Context, x: int, y: int, width: int, display_height, gap, UI):
        self.ctx = ctx
        self.x = x
        self.y = y # Base Y position for the first color display
        self.width = width
        self.display_height = display_height
        self.gap = gap
        self.UI = UI
        self.border_thickness = 1

        # Store two selected colors, initialized to white
        self.selected_colors = [self.UI.app.visualizer.colors[0], self.UI.app.visualizer.colors[0]]
        # 0 for the first color, 1 for the second.
        self.active_selection_index = None

        # Vertices for a unit quad (0-1 range) - shared
        self.quad = ctx.buffer(np.array([
            0.0, 0.0,  # Top-left
            1.0, 0.0,  # Top-right
            0.0, 1.0,  # Bottom-left
            1.0, 1.0,  # Bottom-right
        ], dtype='f4'))

        # Shader Program for the Selected Color Displays (now two of them)
        self.color_display_prog = ctx.program(
            vertex_shader='''
                #version 330
                in vec2 in_vert;

                uniform vec2 screen_size;
                uniform vec4 display_rect; // x, y, width, height of the color display area

                void main() {
                    vec2 pixel_pos = vec2(
                        display_rect.x + in_vert.x * display_rect.z,
                        display_rect.y + in_vert.y * display_rect.w
                    );

                    vec2 ndc_pos = vec2(
                        (pixel_pos.x / screen_size.x) * 2.0 - 1.0,
                        1.0 - (pixel_pos.y / screen_size.y) * 2.0
                    );

                    gl_Position = vec4(ndc_pos, 0.0, 1.0);
                }
            ''',
            fragment_shader='''
                #version 330
                out vec4 color;
                uniform vec3 display_color;

                void main() {
                    color = vec4(display_color, 1.0);
                }
            '''
        )
        self.color_display_vao = ctx.simple_vertex_array(self.color_display_prog, self.quad, 'in_vert')

        # Shader Program for drawing Borders
        self.border_prog = ctx.program(
            vertex_shader='''
                #version 330
                in vec2 in_vert;

                uniform vec2 screen_size;
                uniform vec4 border_rect; // x, y, width, height of the border area (including thickness)

                void main() {
                    vec2 pixel_pos = vec2(
                        border_rect.x + in_vert.x * border_rect.z,
                        border_rect.y + in_vert.y * border_rect.w
                    );

                    vec2 ndc_pos = vec2(
                        (pixel_pos.x / screen_size.x) * 2.0 - 1.0,
                        1.0 - (pixel_pos.y / screen_size.y) * 2.0
                    );

                    gl_Position = vec4(ndc_pos, 0.0, 1.0);
                }
            ''',
            fragment_shader='''
                #version 330
                out vec4 color;
                uniform vec3 border_color;

                void main() {
                    color = vec4(border_color, 1.0);
                }
            '''
        )
        self.border_vao = ctx.simple_vertex_array(self.border_prog, self.quad, 'in_vert')

    def render(self):
        """Renders the two selected color display rectangles and the active border."""
        self.ctx.blend_func = (moderngl.SRC_ALPHA, moderngl.ONE_MINUS_SRC_ALPHA)
        self.ctx.enable(moderngl.BLEND)
        self.ctx.viewport = (0, 0, self.ctx.screen.width, self.ctx.screen.height) # Ensure full screen viewport

       
        # Calculate positions for the two color displays
        color1_display_y = self.y
        color2_display_y = color1_display_y + self.display_height + self.gap

                # --- Render Borders for Active Selection ---
        self.border_prog['screen_size'].value = self.ctx.screen.size
        self.border_prog['border_color'].value = (1.0, 1.0, 1.0) # White border

        # --- Render Borders (only if an active selection exists) ---
        if self.active_selection_index is not None:
            self.border_prog['screen_size'].value = self.ctx.screen.size
            self.border_prog['border_color'].value = (1.0, 1.0, 1.0)

            border_x = self.x - self.border_thickness
            border_w = self.width + 2 * self.border_thickness
            border_h = self.display_height + 2 * self.border_thickness

            if self.active_selection_index == 0:
                border_y = color1_display_y - self.border_thickness
                self.border_prog['border_rect'].value = (border_x, border_y, border_w, border_h)
                self.border_vao.render(moderngl.TRIANGLE_STRIP)
            elif self.active_selection_index == 1:
                border_y = color2_display_y - self.border_thickness
                self.border_prog['border_rect'].value = (border_x, border_y, border_w, border_h)
                self.border_vao.render(moderngl.TRIANGLE_STRIP)
 



        # Render first color display
        self.color_display_prog['screen_size'].value = self.ctx.screen.size
        self.color_display_prog['display_rect'].value = (self.x, color1_display_y, self.width, self.display_height)
        if self.selected_colors[0] is not None: self.color_display_prog['display_color'].value = self.selected_colors[0]
        self.color_display_vao.render(moderngl.TRIANGLE_STRIP)

        # Render second color display
        self.color_display_prog['display_rect'].value = (self.x, color2_display_y, self.width, self.display_height)
        if self.selected_colors[1] is not None: self.color_display_prog['display_color'].value = self.selected_colors[1]
        self.color_display_vao.render(moderngl.TRIANGLE_STRIP)


    def set_selected_color(self, color: tuple[float, float, float]):
        """Sets the selected color for the currently active slot."""
        if self.active_selection_index is not None:
            self.selected_colors[self.active_selection_index] = color

    def get_selected_color(self, index: int | None = None) -> tuple[float, float, float]:
        """Gets a selected color by index, or the active one if no index is given."""
        if index is None:
            return self.selected_colors[self.active_selection_index]
        elif index in [0, 1]:
            return self.selected_colors[index]
        else:
            raise ValueError("Invalid color index. Must be 0 or 1.")

    def set_active_selection_index(self, index: int | None):
        """Sets which color slot is currently active, or None for no active selection."""
        if index is None or index in [0, 1]:
            self.active_selection_index = index
        else:
            raise ValueError("Invalid selection index. Must be 0, 1, or None.")

    def get_active_selection_index(self) -> int:
        """Returns the current active selection index."""
        return self.active_selection_index

    def contains_point_for_selection(self, x: int, y: int) -> int | None:
        """
        Checks if a point (x, y) is within either color display rectangle.
        Returns the index (0 or 1) if found, otherwise None.
        """
        color1_display_y = self.y
        color2_display_y = color1_display_y + self.display_height + self.gap

        if (self.x <= x < self.x + self.width and
            color1_display_y <= y < color1_display_y + self.display_height):
            return 0
        elif (self.x <= x < self.x + self.width and
              color2_display_y <= y < color2_display_y + self.display_height):
            return 1
        return None

    @property
    def rects(self):
        """Returns the (x, y, width, height) tuples for both display rects."""
        color1_display_y = self.y
        color2_display_y = color1_display_y + self.display_height + self.gap
        return [
            (self.x, color1_display_y, self.width, self.display_height),
            (self.x, color2_display_y, self.width, self.display_height)
        ]

# import numpy as np
# import moderngl

# class ColorPicker:
#     def __init__(self, ctx: moderngl.Context, x, y, width, height):
#         self.ctx = ctx
#         self.x = x
#         self.y = y
#         self.width = width
#         self.height = height

#         self.selected_color = (1.0, 1.0, 1.0)

#         # Framebuffer for color picking
#         # Its dimensions should match the picker's width and height
#         self.fbo = ctx.framebuffer(
#             color_attachments=[ctx.texture((width, height), 4)]
#         )

#         # Vertices for a unit quad (0-1 range)
#         self.quad = ctx.buffer(np.array([
#             0.0, 0.0,  # Top-left
#             1.0, 0.0,  # Top-right
#             0.0, 1.0,  # Bottom-left
#             1.0, 1.0,  # Bottom-right
#         ], dtype='f4'))

#         # --- Shader Program for the Color Picker ---
#         # This shader is used for both on-screen rendering and FBO rendering for picking
#         self.picker_prog = ctx.program(
#             vertex_shader='''
#                 #version 330
#                 in vec2 in_vert;
#                 out vec2 uv;

#                 uniform vec2 target_size;  // This will be screen_size for screen, or FBO size for FBO
#                 uniform vec4 target_rect;  // This will be picker_rect for screen, or (0,0,width,height) for FBO

#                 void main() {
#                     uv = in_vert;

#                     vec2 pixel_pos = vec2(
#                         target_rect.x + in_vert.x * target_rect.z,
#                         target_rect.y + in_vert.y * target_rect.w
#                     );

#                     vec2 ndc_pos = vec2(
#                         (pixel_pos.x / target_size.x) * 2.0 - 1.0,
#                         1.0 - (pixel_pos.y / target_size.y) * 2.0
#                     );

#                     gl_Position = vec4(ndc_pos, 0.0, 1.0);
#                 }
#             ''',
#             fragment_shader='''
#                 #version 330
#                 in vec2 uv;
#                 out vec4 color;

#                 void main() {
#                     color = vec4(uv.x, uv.y, 1.0 - uv.x * uv.y, 1.0);
#                 }
#             '''
#         )
#         self.picker_vao = ctx.simple_vertex_array(self.picker_prog, self.quad, 'in_vert')


#         # --- Shader Program for the Selected Color Display ---
#         self.color_display_prog = ctx.program(
#             vertex_shader='''
#                 #version 330
#                 in vec2 in_vert;

#                 uniform vec2 screen_size;
#                 uniform vec4 display_rect;

#                 void main() {
#                     vec2 pixel_pos = vec2(
#                         display_rect.x + in_vert.x * display_rect.z,
#                         display_rect.y + in_vert.y * display_rect.w
#                     );

#                     vec2 ndc_pos = vec2(
#                         (pixel_pos.x / screen_size.x) * 2.0 - 1.0,
#                         1.0 - (pixel_pos.y / screen_size.y) * 2.0
#                     );

#                     gl_Position = vec4(ndc_pos, 0.0, 1.0);
#                 }
#             ''',
#             fragment_shader='''
#                 #version 330
#                 out vec4 color;
#                 uniform vec3 display_color;

#                 void main() {
#                     color = vec4(display_color, 1.0);
#                 }
#             '''
#         )
#         self.color_display_vao = ctx.simple_vertex_array(self.color_display_prog, self.quad, 'in_vert')


#     def render(self):
#         self.ctx.blend_func = (moderngl.SRC_ALPHA, moderngl.ONE_MINUS_SRC_ALPHA)
#         self.ctx.enable(moderngl.BLEND)

#         # --- Render the Color Picker to the screen ---
#         # Set uniforms for screen rendering
#         self.picker_prog['target_size'].value = self.ctx.screen.size
#         self.picker_prog['target_rect'].value = (self.x, self.y, self.width, self.height)
#         self.ctx.viewport = (0, 0, self.ctx.screen.width, self.ctx.screen.height)
#         self.picker_vao.render(moderngl.TRIANGLE_STRIP)

#         # --- Render the Selected Color Display ---
#         display_height = 30
#         display_y = self.y + self.height + 5

#         self.color_display_prog['screen_size'].value = self.ctx.screen.size
#         self.color_display_prog['display_rect'].value = (self.x, display_y, self.width, display_height)
#         if self.selected_color is not None: self.color_display_prog['display_color'].value = self.selected_color
#         self.color_display_vao.render(moderngl.TRIANGLE_STRIP)


#     def pick_color(self, mouse_x, mouse_y):
#         if not (self.x <= mouse_x < self.x + self.width and self.y <= mouse_y < self.y + self.height):
#             return None

#         rel_x = int(mouse_x - self.x)
#         rel_y = int(mouse_y - self.y)

#         # --- IMPORTANT FIX START ---

#         # 1. Store the current active framebuffer and viewport
#         current_fbo = self.ctx.fbo
#         current_viewport = self.ctx.viewport

#         # 2. Activate our FBO for drawing
#         self.fbo.use()
#         # Set viewport to match the FBO's full dimensions
#         self.ctx.viewport = (0, 0, self.width, self.height)

#         # 3. Clear the FBO's color buffer before drawing
#         self.ctx.clear(0.0, 0.0, 0.0, 0.0) # Clear to transparent black

#         # 4. Set uniforms for the picker_prog *specifically for rendering into the FBO*
#         # When rendering to the FBO, the FBO itself is our "target screen"
#         self.picker_prog['target_size'].value = (self.width, self.height)
#         # We want to render the picker to fill the entire FBO, so its rect is (0,0,width,height)
#         self.picker_prog['target_rect'].value = (0, 0, self.width, self.height)

#         # 5. Render the color palette into the FBO
#         self.picker_vao.render(moderngl.TRIANGLE_STRIP)

#         # 6. Read pixels from the FBO
#         # The FBO's internal Y-axis is still bottom-left, so we invert the mouse Y.
#         fbo_y_for_picking = self.height - 1 - rel_y
#         data = self.fbo.read(components=3, alignment=1)
#         img = np.frombuffer(data, dtype=np.uint8).reshape((self.height, self.width, 3))

#         # 7. Restore the original framebuffer and viewport
#         current_fbo.use()
#         self.ctx.viewport = current_viewport

#         # --- IMPORTANT FIX END ---

#         # Get the color at the calculated position
#         if not (0 <= rel_x < self.width and 0 <= fbo_y_for_picking < self.height):
#             print(f"Warning: Click coordinates ({rel_x},{rel_y}) out of bounds after adjustment for picking.")
#             return None

#         r, g, b = img[fbo_y_for_picking, rel_x]

#         self.selected_color = (r / 255.0, g / 255.0, b / 255.0)
#         return self.selected_color