#version 330 core

uniform sampler2D Texture0;
uniform vec2 texelSize;
uniform float alpha;
uniform vec3 smokeColor;

in vec2 uv;
out vec4 fragColor;

void main() {
    // 3x3 Gaussian kernel
    float k[9] = float[](1, 2, 1, 2, 4, 2, 1, 2, 1);
    //float k[9] = float[](0, 1, 0, 1, 4, 1, 0, 1, 0); 
    //float k[9] = float[](0.5, 1, 0.5, 1, 6, 1, 0.5, 1, 0.5);

    vec2 o[9] = vec2[](
        vec2(-1, -1), vec2(0, -1), vec2(1, -1),
        vec2(-1,  0), vec2(0,  0), vec2(1,  0),
        vec2(-1,  1), vec2(0,  1), vec2(1,  1)
    );

    vec4 sum = vec4(0.0);
    float w = 0.0;

    for (int i = 0; i < 9; i++) {
        vec4 s = texture(Texture0, uv + o[i] * texelSize);
        sum += s * k[i];
        w += k[i];
    }

    vec4 blurred = sum / w;
    blurred.rgb = mix(blurred.rgb, smokeColor, 0.5);

    // Sadece blur (fade ayrı pass'ta)
    fragColor = vec4(blurred.rgb, blurred.a * alpha);
}
