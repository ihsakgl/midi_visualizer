#version 330

in vec2 v_uv;
out vec4 fragColor;
uniform sampler2D text_texture;

void main() {
    fragColor = texture(text_texture, v_uv);
}