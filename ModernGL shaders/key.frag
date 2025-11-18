#version 330

in vec2 v_uv_local;
in float v_global_x;

out vec4 fragColor;

uniform vec3 color1;
uniform vec3 color2;
uniform float leftCutoff;
uniform float rightCutoff;
uniform float whiteKeyWidth; // relative width of a white key (0..1)
uniform float gap;           // fraction of key width to leave as gap (e.g., 0.02)

void main() {
    float x = v_global_x;  // global coordinate (0..1 across entire keyboard)
    
    // Determine position within a single white key
    float keyPos = v_uv_local.x;

    vec3 color;

    // If we are inside the gap region, make it black
    if (keyPos < gap|| keyPos > (whiteKeyWidth - gap)) {
        color = vec3(0.0, 0.0, 0.0);
    }
    else if (x < leftCutoff) {
        color = color1;
    } else if (x > rightCutoff) {
        color = color2;
    } else {
        float t = clamp((x - leftCutoff) / (rightCutoff - leftCutoff), 0.0, 1.0);
        color = mix(color1, color2, t);
    }

    fragColor = vec4(color, 1.0);
}