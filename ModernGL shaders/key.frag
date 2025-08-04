#version 330

in vec2 uv;


uniform vec3 color1;
uniform vec3 color2;
uniform float leftCutoff;
uniform float rightCutoff;
uniform vec2 u_resolution;
out vec4 fragColor;

void main() {
    


    vec3 color;
    if (uv.x < leftCutoff) {
        color = color1;
    } else if (uv.x > rightCutoff) {
        color = color2;
    } else {
        float t = clamp((uv.x - leftCutoff) / (rightCutoff - leftCutoff), 0.0, 1.0);
        color = mix(color1, color2, t);
    }
    fragColor = vec4(color, 1.0);
}