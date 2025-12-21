#version 330 core

uniform sampler2D Texture0;
uniform vec2 texelSize;
uniform float dt;
uniform float decay;        // e.g. 0.98 per second
uniform float diffusion;    // diffusion strength

in vec2 uv;
out vec4 fragColor;

void main() {
    vec4 center = texture(Texture0, uv);

    // --- 3x3 diffusion kernel ---
    vec4 sum = vec4(0.0);
    float w = 0.0;

    float k[9] = float[](
        0.5, 1.0, 0.5,
        1.0, 6.0, 1.0,
        0.5, 1.0, 0.5
    );

    vec2 o[9] = vec2[](
        vec2(-1,-1), vec2(0,-1), vec2(1,-1),
        vec2(-1, 0), vec2(0, 0), vec2(1, 0),
        vec2(-1, 1), vec2(0, 1), vec2(1, 1)
    );

    for (int i = 0; i < 9; i++) {
        sum += texture(Texture0, uv + o[i] * texelSize) * k[i];
        w += k[i];
    }

    vec4 blur = sum / w;

    // --- Diffusion ---
    float alpha = 1.0 - exp(-diffusion * dt);
    vec4 diffused = center + alpha * (blur - center);

    // --- Exponential decay (frame-rate independent) ---
    float d = exp(-decay * dt);
    diffused *= d;

    fragColor = diffused;
}
