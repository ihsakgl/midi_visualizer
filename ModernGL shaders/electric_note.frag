#version 330

uniform float iTime;
uniform vec2 iResolution;

out vec4 fragColor;

// Simple hash function for noise
float hash(vec2 p) {
    p = fract(p * vec2(123.34, 456.21));
    p += dot(p, p + 45.32);
    return fract(p.x * p.y);
}

// Smooth 2D noise
float noise(vec2 p) {
    vec2 i = floor(p);
    vec2 f = fract(p);
    float a = hash(i);
    float b = hash(i + vec2(1.0, 0.0));
    float c = hash(i + vec2(0.0, 1.0));
    float d = hash(i + vec2(1.0, 1.0));
    vec2 u = f * f * (3.0 - 2.0 * f);
    return mix(a, b, u.x) + (c - a) * u.y * (1.0 - u.x) + (d - b) * u.x * u.y;
}

void main() {
    vec2 uv = gl_FragCoord.xy / iResolution.xy;
    uv = uv * 2.0 - 1.0;
    uv.x *= iResolution.x / iResolution.y;

    // Energy beam width
    float beamWidth = 0.1;
    float dist = abs(uv.x);

    // Electric noise modulation
    float n = noise(vec2(uv.y * 5.0, iTime * 0.8));
    float electric = smoothstep(beamWidth, beamWidth - 0.02, dist - n * 0.03);

    // Inner glow intensity
    float core = smoothstep(beamWidth - 0.04, 0.0, dist);

    // Combine effects
    vec3 color = vec3(0.0);
    color += vec3(0.0, 0.8, 1.0) * core;          // bright cyan core
    color += vec3(0.0, 0.5, 1.0) * electric;      // moving electric streaks
    color += vec3(0.1, 0.3, 0.8) * (1.0 - dist);  // soft outer glow

    // Vignette fade toward top/bottom
    float fade = smoothstep(0.0, 0.2, uv.y + 1.0) * smoothstep(0.0, 0.2, 1.0 - uv.y);
    color *= fade;

    // Final glow boost
    color = pow(color, vec3(0.8)); // gamma
    fragColor = vec4(color, 1.0);
}
