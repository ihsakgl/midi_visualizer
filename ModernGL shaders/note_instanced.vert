#version 330 core

layout(location = 0) in vec2 in_uv;         // unit quad
layout(location = 1) in vec2 i_pos;         // top-left of note
layout(location = 2) in vec2 i_size;        // note size
layout(location = 3) in vec4 i_color1;      // note color start
layout(location = 4) in vec4 i_color2;      // note color end
layout(location = 5) in float i_seed;
layout(location = 6) in float i_phase;

uniform vec2 u_resolution;
uniform float glowRadius;                   // glow expansion

out vec2 v_uv;         // 0..1 quad coordinate
out vec2 v_fragCoord;  // pixel space
out vec2 v_pos;
out vec2 v_size;
out vec4 v_color1;
out vec4 v_color2;
out float v_seed;
out float v_phase;

void main() {
    // Quad’u glowRadius kadar genişlet
    vec2 expandedPos  = i_pos - vec2(glowRadius);
    vec2 expandedSize = i_size + vec2(glowRadius * 2.0);

    // Pixel-space koordinat
    vec2 pixel = expandedPos + in_uv * expandedSize;
    v_fragCoord = pixel;
    v_uv = in_uv;
    v_pos = i_pos;
    v_size = i_size;
    v_color1 = i_color1;
    v_color2 = i_color2;
    v_seed = i_seed;
    v_phase = i_phase;

    // NDC dönüşümü
    vec2 ndc = (pixel / u_resolution) * 2.0 - 1.0;
    ndc.y = -ndc.y; // OpenGL koordinatlarıyla uyum
    gl_Position = vec4(ndc, 0.0, 1.0);
}
