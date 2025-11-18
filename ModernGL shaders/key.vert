#version 330

in vec2 in_position;

uniform vec2 u_position;   // key position in pixels
uniform vec2 u_size;       // key size in pixels
uniform vec2 u_resolution; // screen size in pixels   



out vec2 v_uv_local;  // 0..1 within key
out float v_global_x; // 0..1 across screen (or keyboard area)

void main() {
    vec2 pixel = in_position * u_size + u_position;

    // Normalized Device Coordinates
    float x = (pixel.x / u_resolution.x) * 2.0 - 1.0;
    float y = ((u_resolution.y - pixel.y) / u_resolution.y) * 2.0 - 1.0;
    gl_Position = vec4(x, y, 0.0, 1.0);

    v_uv_local = in_position;
    v_global_x = pixel.x / u_resolution.x; // 0..1 across the screen width
}
