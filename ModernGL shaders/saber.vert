#version 330



in vec2 in_pos;
out vec2 uv;

uniform float x_left;
uniform float x_right;

void main() {
    uv.x = (in_pos.x - x_left) / (x_right - x_left);
    uv.y = (in_pos.y + 1.0) * 0.5;
 
    gl_Position = vec4(in_pos, 0.0, 1.0);
}
