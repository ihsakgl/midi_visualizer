#version 330

in vec2 v_texcoord;
in vec2 v_frag_position;

out vec4 fragColor;

uniform sampler2D video_texture;
uniform vec2 frame_pos;
uniform vec2 frame_size;

void main() {
    // Fragment, video alanının dışındaysa çizme
    if (v_frag_position.x < frame_pos.x || v_frag_position.x > frame_pos.x + frame_size.x ||
    v_frag_position.y < frame_pos.y || v_frag_position.y > frame_pos.y + frame_size.y) {
    discard;
    } else {
        fragColor = texture(video_texture, v_texcoord);
    }
 
    
}