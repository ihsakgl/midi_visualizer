import pygame

class Button:
    def __init__(self, rect, color, text, font, action=None, parameters=None):
        self.rect = pygame.Rect(rect)
        self.color = color
        self.text = text
        self.font = font
        self.action = action
        self.parameters = parameters

    def draw(self, surface):
        pygame.draw.rect(surface, self.color, self.rect)
        text_surf = self.font.render(self.text, True, (255, 255, 255))
        surface.blit(text_surf, (self.rect.x + 5, self.rect.y + 5))

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and self.rect.collidepoint(event.pos):
            if self.action:
                self.action(self.parameters)

class InputBox:
    def __init__(self, x, y, w, h, text=''):
        self.rect = pygame.Rect(x, y, w, h)
        self.color_inactive = "white"
        self.color_active = "lightblue"
        self.color = self.color_inactive
        self.text = text
        self.font = pygame.font.Font(None, 32)
        self.txt_surface = self.font.render(text, True, self.color)
        self.active = False

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            # Toggle active state when clicked
            if self.rect.collidepoint(event.pos):
                self.active = not self.active
            else:
                self.active = False
            self.color = self.color_active if self.active else self.color_inactive

        if event.type == pygame.KEYDOWN:
            if self.active:
                if event.key == pygame.K_RETURN:
                    print(f"Entered: {self.text}")
                elif event.key == pygame.K_BACKSPACE:
                    self.text = self.text[:-1]
                else:
                    self.text += event.unicode
                self.txt_surface = self.font.render(self.text, True, (255, 255, 255))

    def draw(self, screen):
        # Draw text
        screen.blit(self.txt_surface, (self.rect.x+5, self.rect.y+5))
        # Draw rectangle
        pygame.draw.rect(screen, self.color, self.rect, 2)
     
    def get_value(self, type):
        if type == "tuple":
            """Returns the text content as a color tuple"""
            try:
                parts = [int(v.strip()) for v in self.text.split(',')]
                if len(parts) == 3 and all(0 <= v <= 255 for v in parts):
                    return tuple(parts)
            except:
                pass
            return None
        elif type == "number":
            return self.text
            

class SeekBar:
    def __init__(self, x, y, width, height, video_duration, action=None):
        self.rect = pygame.Rect(x, y, width, height)
        self.handle_radius = height // 2
        self.video_duration = video_duration
        self.position = 0.0  # Current position in seconds
        self.dragging = False
        self.action = action
  


    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.dragging = True
                self._update_position(event.pos[0])

        elif event.type == pygame.MOUSEBUTTONUP:
            
            if self.dragging: self.action(self.video_duration * (self.position / self.rect.width))
            self.dragging = False


        elif event.type == pygame.MOUSEMOTION and self.dragging:
            self._update_position(event.pos[0])

    def _update_position(self, mouse_x):
        relative_x = max(min(mouse_x, self.rect.right), self.rect.left)
        percent = (relative_x - self.rect.left) / self.rect.width
        self.position = percent * self.video_duration
    

    def draw(self, screen, video_play_time):
        # Bar
        pygame.draw.rect(screen, (180, 180, 180), self.rect)
        
        # Handle
        handle_x = int(self.rect.left + (self.position / self.video_duration) * self.rect.width)
        handle_x += self.rect.width * (video_play_time / self.video_duration)
        handle_y = self.rect.centery
        pygame.draw.circle(screen, (255, 0, 0), (handle_x, handle_y), self.handle_radius)


    def get_time(self):
        return self.position
