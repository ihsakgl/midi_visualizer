#version 330

uniform sampler2D screen_texture;
in vec2 uv;
out vec4 fragColor;

void main() {
    fragColor = texture(screen_texture, uv);
}
