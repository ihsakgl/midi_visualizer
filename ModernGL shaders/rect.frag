#version 330

uniform vec3 u_color;
out vec4 fragColor;

void main() {
    
    fragColor = vec4(u_color, 1.0);
}