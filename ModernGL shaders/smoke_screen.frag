#version 330 core

uniform sampler2D Texture0;
uniform vec3 smokeColor1;
uniform vec3 smokeColor2;
uniform float leftCutoff;
uniform float rightCutoff;

in vec2 uv;
out vec4 fragColor;

void main() {
    vec4 smoke = texture(Texture0, uv);

    float t = clamp(
        (uv.x - leftCutoff) / (rightCutoff - leftCutoff),
        0.0,
        1.0
    );

    vec3 color = mix(smokeColor1, smokeColor2, t);

    fragColor = vec4(color, smoke.a);
}
