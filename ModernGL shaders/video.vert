#version 330

in vec2 in_position;
in vec2 in_texcoord;

out vec2 v_texcoord;
out vec2 v_frag_position;

uniform vec2 screen_size;
uniform vec2 position;
uniform vec2 size;

void main() {
    vec2 pixel_pos = position + in_position * size;
    v_frag_position = pixel_pos;

    vec2 ndc_pos = vec2(
        (pixel_pos.x / screen_size.x) * 2.0 - 1.0,
        1.0 - (pixel_pos.y / screen_size.y) * 2.0
    );

    gl_Position = vec4(ndc_pos, 0.0, 1.0);
    v_texcoord = in_texcoord;
}
