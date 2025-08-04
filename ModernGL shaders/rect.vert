#version 330

in vec2 in_position;

uniform vec2 u_position;
uniform vec2 u_size;
uniform vec2 u_resolution;

out vec2 uv;  // <-- eklendi

void main() {
    // Hesaplanmış ekran pozisyonu
    vec2 pixel = in_position * u_size + u_position;
    float x = (pixel.x / u_resolution.x) * 2.0 - 1.0;
    float y = ((u_resolution.y - pixel.y) / u_resolution.y) * 2.0 - 1.0;
    gl_Position = vec4(x, y, 0.0, 1.0);

    // UV = [0,1] x [0,1] aralığında, in_position zaten 0–1 aralığında
    uv = in_position;
}