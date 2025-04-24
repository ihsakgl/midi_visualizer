import random, pygame, math

class Particle:
    def __init__(self, x, y, screen, color, vx, vy, visualizer_rect, hit_particle: bool):
        self.x_position = x
        self.y_position = y
        self.scale_mulitplier = ((visualizer_rect.width / 600 + visualizer_rect.height / 337.5) / 2)
        self.initial_radius = 1 * self.scale_mulitplier
        self.radius = self.initial_radius
        self.screen = screen
        self.color = color
        
      
        self.y_speed = vy + random.uniform(-1, 0) * self.scale_mulitplier
        self.x_speed = vx + random.uniform(-0.2, 0.2) * self.scale_mulitplier
        self.gravity = 0.015 * self.scale_mulitplier

        self.is_hit_particle = hit_particle
        
        self.max_x_speed = self.x_speed * 6
        self.min_y_speed = self.y_speed * 3
        self.x_acceleration = 0.015 * self.scale_mulitplier
        self.y_acceleration = 0.04 * (1 / self.scale_mulitplier)

    def update(self, elapsed_time_in_sec):
   
        self.radius *= 0.993

        if self.is_hit_particle:
            if self.x_speed < self.max_x_speed: self.x_speed += self.x_acceleration
            if self.y_speed > self.min_y_speed: self.y_speed += self.y_acceleration
    

     

        self.y_position += self.y_speed
        self.x_position += self.x_speed
        
  
    def draw(self):
        pygame.draw.circle(self.screen, self.color, (self.x_position + self.radius / 2, self.y_position + self.radius / 2), self.radius)

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
