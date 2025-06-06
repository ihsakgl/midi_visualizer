import random, pygame, math, numpy as np, moderngl
from moderngl_window import geometry
import copy


class ParticleSystem:
    def __init__(self, ctx, visualizer_rect, max_particles=1000):
        self.ctx = ctx
        self.visualizer_rect = visualizer_rect
        self.max_particles = max_particles
        self.particles = []

        # Empty data
        self.positions = np.zeros((self.max_particles, 2), dtype='f4')
        self.colors = np.zeros((self.max_particles, 3), dtype='f4')
        self.sizes = np.zeros((self.max_particles,), dtype='f4')


        self.position_buffer = self.ctx.buffer(self.positions.tobytes())
        self.color_buffer = self.ctx.buffer(self.colors.tobytes())
        self.size_buffer = self.ctx.buffer(self.sizes.tobytes())


        # Shaders
        with open("ModernGL shaders/particle.vert", "r", encoding="utf-8") as f:
            vertex_shader = f.read()
        with open("ModernGL shaders/particle.frag", "r", encoding="utf-8") as f:
            fragment_shader = f.read()

        self.prog = self.ctx.program(
            vertex_shader=vertex_shader,
            fragment_shader=fragment_shader
        )

        self.vao = self.ctx.vertex_array(
            self.prog,
            [
                (self.position_buffer, '2f', 'in_position'),
                (self.color_buffer, '3f', 'in_color'),
                (self.size_buffer, '1f', 'in_size'),
                
            ]
        )


    def add_particle(self, particle):
    
        self.particles.append(particle)
        #print(f"added particle at positions {particle.x, particle.y}")


    def update(self):
        #print(len(self.particles))

        # Update all particles
        for p in self.particles:
            p.update()
      

        # Delete them if they are too small
        
        self.particles = [
            p for p in self.particles 
            if p.radius >= p.initial_radius * 0.15 
        ]

        if len(self.particles) > self.max_particles:
            print("TOO MANY PARTICLES!")
            

        

    def render(self):
        if len(self.particles) == 0:
            return

        positions = []
        colors = []
        sizes = []


        for p in self.particles:
            positions.append([p.x, p.y])
            colors.append([c / 255.0 for c in p.color])
            sizes.append(p.radius)
       
     
        positions = np.array(positions, dtype='f4')
        colors = np.array(colors, dtype='f4')
        sizes = np.array(sizes, dtype='f4')
   

        self.position_buffer.write(positions.tobytes())
        self.color_buffer.write(colors.tobytes())
        self.size_buffer.write(sizes.tobytes())
   

        self.prog['screen_width'].value = 1920
        self.prog['screen_height'].value = 1080

        self.vao.render(mode=moderngl.POINTS, vertices=len(self.particles))


class Particle:
    def __init__(self, x, y, color, vx, vy, visualizer_rect, hit_particle: bool, note_width):
        self.x = x + random.uniform(-note_width / 6, note_width / 6) 
        self.y = y
        
       
        self.visualizer_rect = visualizer_rect
        self.scale_mulitplier = (visualizer_rect.width / 600 + visualizer_rect.height / 337.5) / 2
        self.initial_radius = (1.2 + random.uniform(-0.5, 0.3))* self.scale_mulitplier
        self.radius = self.initial_radius
        self.color = (255, 255, 255)
        
        if self.x < x:
            self.x_speed = vx + random.uniform(-0.1, 0) * self.scale_mulitplier 
        else:
            self.x_speed = vx + random.uniform(0, 0.1) * self.scale_mulitplier 

        self.y_speed = vy + random.uniform(-0.2, 0) * self.scale_mulitplier 

        self.gravity = 0.015 * self.scale_mulitplier

        self.is_hit_particle = hit_particle
        
        self.max_x_speed = self.x_speed * 3
        self.min_y_speed = self.y_speed * 6
        self.x_acceleration = 0.010 * self.scale_mulitplier
        self.y_acceleration = 0.08 * (1 / self.scale_mulitplier)

 

    def update(self):
        
        self.radius *= 0.993
  

        if self.is_hit_particle:
            if self.x_speed < self.max_x_speed: self.x_speed += self.x_acceleration
            if self.y_speed < -1: self.y_speed += self.y_acceleration
    

     

        self.y += self.y_speed
        self.x += self.x_speed
        
  
class Background:
    def __init__(self, ctx, width, height, particle_system, smoke_color):
        self.ctx = ctx
        self.width = int(width)
        self.height = int(height)
        self.particle_system = particle_system
        self.smoke_color = smoke_color

        self.background_texture_a = self.ctx.texture((width, height), 4, dtype='f4')
        self.background_texture_b = self.ctx.texture((width, height), 4, dtype='f4')
        self.background_fbo_a = self.ctx.framebuffer(color_attachments=[self.background_texture_a])
        self.background_fbo_b = self.ctx.framebuffer(color_attachments=[self.background_texture_b])
        self.current_texture = self.background_texture_a
        self.current_fbo = self.background_fbo_a
        # Shader programları yükle
        self.fade_program = self.load_program("fade")
        self.screen_program = self.load_program("screen")
        self.smoke_program = self.load_program("smoke")

        vertices = np.array([
            -1.0, -1.0,
            1.0, -1.0,
            -1.0,  1.0,
            1.0,  1.0,
        ], dtype='f4')

        vbo = self.ctx.buffer(vertices)
        self.quad_screen = self.ctx.vertex_array(
            self.screen_program, 
            [(vbo, '2f', 'in_vert')]
        )
        self.quad_fade = self.ctx.vertex_array(
            self.fade_program,
            [(vbo, "2f", "in_vert")]
        )
        self.quad_smoke = self.ctx.vertex_array(
            self.smoke_program,
            [(vbo, "2f", "in_vert")]
        )
  
    

    def load_program(self, name):
        with open(f"ModernGL shaders/{name}.vert") as vfile, open(f"ModernGL shaders/{name}.frag") as ffile:
            return self.ctx.program(vertex_shader=vfile.read(), fragment_shader=ffile.read())
        
    def render(self, delta_time):
        self.background_fbo_b.use()


 
        # --- FADE PASS (A → B) ---
        self.ctx.disable(moderngl.BLEND)
        self.ctx.blend_func = moderngl.ONE, moderngl.ZERO
        self.background_texture_a.use(location=0)
        #self.fade_program['alpha'].value = 0.03
        self.fade_program['decayK'].value = 0.055
        self.quad_fade.render(moderngl.TRIANGLE_STRIP)

        self.ctx.enable(moderngl.BLEND)

        # --- PARTICLES PASS (B üzerinde) ---
        self.ctx.blend_func = moderngl.SRC_ALPHA, moderngl.ONE
        self.particle_system.render()

        # --- SMOKE PASS (B üzerinde) ---
        self.ctx.blend_func = moderngl.ONE, moderngl.ONE_MINUS_SRC_ALPHA
        self.smoke_program['smokeColor'].value = (c / 255 for c in self.smoke_color)
        self.smoke_program['alpha'].value = 0.98
        self.smoke_program['texelSize'].value = (1.0 / self.width, 1.0 / self.height)
        self.quad_smoke.render(moderngl.TRIANGLE_STRIP)


        # --- COMPOSITE TO SCREEN ---  
        self.ctx.screen.use()
        self.ctx.blend_func = moderngl.SRC_ALPHA, moderngl.ONE_MINUS_SRC_ALPHA

        self.background_texture_b.use(location=0)
        self.quad_screen.render(moderngl.TRIANGLE_STRIP)

        # --- Ping-pong swap ---
        self.background_fbo_a, self.background_fbo_b         = self.background_fbo_b, self.background_fbo_a
        self.background_texture_a, self.background_texture_b = self.background_texture_b,     self.background_texture_a
