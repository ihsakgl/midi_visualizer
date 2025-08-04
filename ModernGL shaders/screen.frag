#version 330 core

uniform sampler2D Texture0;

in vec2 uv;
out vec4 fragColor;

void main() {
    fragColor = texture(Texture0, uv);
}