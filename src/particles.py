import random, pygame

class Particle:
    def __init__(self, x, y, screen, color, vx, vy):
        self.x_position = x
        self.y_position = y
        self.radius = 4
        self.screen = screen
        
        self.initial_lifetime = random.uniform(1, 3)
        self.lifetime = self.initial_lifetime
        self.y_speed = vy + random.uniform(-0.2, 0.2)
        self.x_speed = vx + random.uniform(-0.2, 0.2)
        self.gravity = 15
        
        self.color = (255, 255, 255, 255)
    

    def update(self, current_time, start_time, speed, new_screen_height, screen_height):
        delta_time = (current_time - start_time) / 1000
        
        self.lifetime -= delta_time
        self.radius *= 0.99
        self.y_speed -= self.gravity * delta_time

        self.y_position -= self.y_speed * (new_screen_height / screen_height) * speed / 90 
        self.x_position += self.x_speed * (new_screen_height / screen_height) * speed / 100
        
   
    def draw(self):
        self.screen.blit(self.circle_surf(), (int(self.x_position - self.radius * 2), int(self.y_position - self.radius * 2)))

    def circle_surf(self):
        surf = pygame.Surface((self.radius * 4, self.radius * 4), pygame.SRCALPHA)  # Use alpha for transparency
        center = self.radius * 2

            # Draw the glow effect with decreasing opacity
        for i in range(1, 4):
            pygame.draw.circle(
                surf,
                (self.color[0], self.color[1], self.color[2], int(100 / i)),  # Adjust alpha for layers
                (center, center),
                self.radius * i
            )

        # Draw the main particle
        pygame.draw.circle(
            surf,
            self.color,
            (center, center),
            self.radius / 2
        )

        return surf
