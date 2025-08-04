import random, math, numpy as np, moderngl
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


    def update(self, delta_time):
        #print(len(self.particles))

        # Update all particles
        for p in self.particles:
            p.update(delta_time)
      

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
    def __init__(self, x, y, vx, vy, radius, hit_particle: bool, note_width, scale_multiplier):
        self.x = x + random.uniform(-note_width / 6, note_width / 6) 
        self.y = y
        
        
        
        self.initial_radius = (radius + random.uniform(-0.2, 0.2) * radius) * scale_multiplier
        self.radius = self.initial_radius
        self.color = (255, 255, 255)
        
  
      
        self.x_speed = (vx + random.uniform(-0.4, 0.4)  * vx) * scale_multiplier 
        self.y_speed = (vy + random.uniform(-0.1, 0) * vy) * scale_multiplier

        if not hit_particle:
            self.x_speed *= random.uniform(-2.0, 2.0)
            self.y_speed *= random.uniform(-2.0, 2.0)

 

        self.is_hit_particle = hit_particle
       
        self.x_acceleration = 50.0 * scale_multiplier 
        if self.x_speed < 0: self.x_acceleration *= -1
     
        self.y_acceleration = 300.0 * scale_multiplier

 

    def update(self, delta_time):
        
        self.radius *= 0.988
  

        if self.is_hit_particle:
            self.x_speed += self.x_acceleration * delta_time
            self.y_speed += self.y_acceleration * delta_time
    

     

        self.y += self.y_speed * delta_time
        self.x += self.x_speed * delta_time
        
  
class Background:
    def __init__(self, ctx, offscreen_fbo, width, height, particle_system, smoke_color1, smoke_color2, left_cutoff, right_cutoff, particle_radius):
        self.ctx = ctx
        self.offscreen_fbo = offscreen_fbo
        self.width = int(width)
        self.height = int(height)
        self.particle_system = particle_system
        self.smoke_color1 = smoke_color1
        self.smoke_color2 = smoke_color2
        self.left_cutoff = left_cutoff
        self.right_cutoff = right_cutoff
        self.particle_radius = particle_radius

        self.background_texture_a = self.ctx.texture((width, height), 4, dtype='f4')
        self.background_texture_b = self.ctx.texture((width, height), 4, dtype='f4')
        self.background_fbo_a = self.ctx.framebuffer(color_attachments=[self.background_texture_a])
        self.background_fbo_b = self.ctx.framebuffer(color_attachments=[self.background_texture_b])
        self.current_texture = self.background_texture_a
        self.current_fbo = self.background_fbo_a

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


 
        # Fade pass (A to B)
        self.ctx.disable(moderngl.BLEND)
        self.ctx.blend_func = moderngl.ONE, moderngl.ZERO
        self.background_texture_a.use(location=0)
        #self.fade_program['alpha'].value = 0.03
        self.fade_program['decayK'].value = 0.055 - (3.0 / self.particle_radius) * 0.02
        self.quad_fade.render(moderngl.TRIANGLE_STRIP)

        self.ctx.enable(moderngl.BLEND)

        # Particle pass (on B)
        self.ctx.blend_func = moderngl.SRC_ALPHA, moderngl.ONE
        self.particle_system.render()

        # Smoke pass (on B)
        self.ctx.blend_func = moderngl.ONE, moderngl.ONE_MINUS_SRC_ALPHA
        self.smoke_program['smokeColor1'].value = (c  for c in self.smoke_color1)
        self.smoke_program['smokeColor2'].value = (c  for c in self.smoke_color2)
        self.smoke_program['leftCutoff'].value = self.left_cutoff
        self.smoke_program['rightCutoff'].value = self.right_cutoff
        self.smoke_program['alpha'].value = 0.98
        self.smoke_program['texelSize'].value = (1.0 / self.width, 1.0 / self.height)
        self.quad_smoke.render(moderngl.TRIANGLE_STRIP)


        # Composite to screen
        self.offscreen_fbo.use()
        self.ctx.blend_func = moderngl.SRC_ALPHA, moderngl.ONE_MINUS_SRC_ALPHA

        self.background_texture_b.use(location=0)
        self.quad_screen.render(moderngl.TRIANGLE_STRIP)

        # Ping pong swap
        self.background_fbo_a, self.background_fbo_b         = self.background_fbo_b, self.background_fbo_a
        self.background_texture_a, self.background_texture_b = self.background_texture_b,     self.background_texture_a
