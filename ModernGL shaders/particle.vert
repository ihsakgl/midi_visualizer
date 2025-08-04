#version 330

in vec2 in_position;
in vec3 in_color;
in float in_size;

out vec3 frag_color;

uniform float screen_width;
uniform float screen_height;

void main() {
    // Piksel pozisyonlarını NDC'ye dönüştür
    float x_ndc = (in_position.x / screen_width) * 2.0 - 1.0;
    float y_ndc = 1.0 - (in_position.y / screen_height) * 2.0;

    // NDC pozisyonunu gl_Position’a ata
    gl_Position = vec4(x_ndc, y_ndc, 0.0, 1.0);

    frag_color = in_color;
    gl_PointSize = in_size;
}
