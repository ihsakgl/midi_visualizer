#version 330

in vec2 uv;
out vec4 fragColor;

uniform sampler2D screen_texture;
uniform int num_lights;

uniform vec2  u_light_pos[88];
uniform vec3  u_light_col[88];
uniform float u_light_inten[88];
uniform float u_light_rad[88];

void main() {
    // Orijinal sahne pikseli
    vec3 base = texture(screen_texture, uv).rgb;
    vec3 result = base;

    // Her ışık için efekt uygula
    for (int i = 0; i < num_lights; i++) {
        // UV uzayında mesafe
        float dist = distance(uv, u_light_pos[i]);
        // 0..1 arası faktör (1 merkezde, 0 yarıçapta ve dışı)
        float f = clamp(1.0 - dist / u_light_rad[i], 0.0, 1.0);

        // Işığın renk katmanı (isteğe bağlı renk filtresi)
        vec3 lightCol = u_light_col[i];

        // Parlaklık artışı: base pikseli (1 + intensity * f) ile ölçekle
        float boost = u_light_inten[i] * f;
        result += base * boost * lightCol;
    }

    fragColor = vec4(result, 1.0);
}
