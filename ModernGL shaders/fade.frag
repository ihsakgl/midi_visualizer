#version 330 core

uniform sampler2D Texture0;
uniform float decayK;
uniform float time;

in vec2 uv;
out vec4 fragColor;

void main() {
    vec4 color = texture(Texture0, uv);
    color.rgb *= decayK;
    color.a *= decayK;

    if (color.a < 0.03) {
        fragColor = vec4(0.0);
    } else {
        fragColor = color;
    }
}
