#version 330 core

layout(location = 0) in vec2 in_uv;         

uniform vec2  notePosition;    // top‐left of note
uniform vec2  noteSize;        // size of note
uniform float glowRadius;      // how far your frag‐shader glows outside
uniform vec2  screenResolution;

out vec2 fragCoord;       

void main() {
    // 1) Expand the quad by glowRadius on all sides
    vec2 expandedPos  = notePosition - vec2(glowRadius);
    vec2 expandedSize = noteSize     + vec2(glowRadius * 2.0);

    // 2) Compute pixel‐space coordinate for this vertex
    vec2 pixel = expandedPos + in_uv * expandedSize;
    fragCoord  = pixel;

    // 3) Transform to NDC
    vec2 ndc = (pixel / screenResolution) * 2.0 - 1.0;
    ndc.y = -ndc.y;  // flip Y for GL

    gl_Position = vec4(ndc, 0.0, 1.0);
}
