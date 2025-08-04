#version 330

in vec3 frag_color;
out vec4 out_color;

void main() {
    float dist = length(gl_PointCoord - vec2(0.5));  // Yumuşak kenarlar
    float alpha = smoothstep(0.5, 0.45, dist);  // Alpha değeri

    out_color = vec4(frag_color, alpha);
}
