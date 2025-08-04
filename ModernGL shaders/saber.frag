#version 330

in vec2 uv;
out vec4 fragColor;


uniform float time;
uniform vec3 color1;
uniform vec3 color2;
uniform float leftCutoff;
uniform float rightCutoff;
uniform float speed;
uniform float saber_y;

const int NUM_OVALS = 120;

float draw_oval(vec2 p, vec2 center, vec2 radius) {
    vec2 d = (p - center) / radius;
    float dist = dot(d, d);
    return exp(-dist * 4.0); // İç opak, dış saydam
}


float hash(vec2 p) {
    return fract(sin(dot(p ,vec2(127.1, 311.7))) * 43758.5453123);
}

float noise(vec2 p) {
    vec2 i = floor(p);
    vec2 f = fract(p);
    float a = hash(i);
    float b = hash(i + vec2(1.0, 0.0));
    float c = hash(i + vec2(0.0, 1.0));
    float d = hash(i + vec2(1.0, 1.0));
    vec2 u = f * f * (3.0 - 2.0 * f);
    return mix(a, b, u.x) + (c - a)*u.y*(1.0 - u.x) + (d - b)*u.x*u.y;
}

void main() {
    

    float center_y = saber_y;
    float dist_to_center = abs(uv.y - center_y) * 5;

    float line_intensity = exp(-pow(dist_to_center * 30.0, 0.5)); // Gauss eğrisi

    float n = noise(vec2(uv.x * 10.0, time * speed)) * 0.5 + 0.5;
    float flicker = mix(0.9, 1.1, n);

    float intensity = line_intensity * flicker;

    float glow = exp(-pow(dist_to_center * 10.0, 2.0));

  


    vec3 saber_color;
    if (uv.x < leftCutoff) {
        saber_color = color1;
    } else if (uv.x > rightCutoff) {
        saber_color = color2;
    } else {
        float t = clamp((uv.x - leftCutoff) / (rightCutoff - leftCutoff), 0.0, 1.0);
        saber_color = mix(color1, color2, t);
    }



    vec3 color = saber_color * intensity * 0.5 + saber_color * glow * 0.3;
    float alpha = intensity * 0.5 + glow * 0.2;

    float fog2 = 0.0;
    for (int i = 0; i < NUM_OVALS; ++i) {
        float fi = float(i);
        float offset = fi * 1.01;
        float speed_factor = 0.02 + fract(sin(fi * 78.233) * 43758.5453) * 0.02;
        float y_pos = center_y;
        float size_x = 0.003 + fract(sin(fi * 5.123) * 234.321) * 0.03;
        float size_y = 0.005 + fract(sin(fi * 12.456) * 643.123) * 0.05;

        float x_pos = fract((time * speed_factor + offset)) * 1.2 - 0.1;
        fog2 += draw_oval(uv, vec2(x_pos, y_pos), vec2(size_x, size_y)) * 0.3;
    }

    color += saber_color * fog2 * 0.02; // mavi-beyaz duman
    alpha += fog2 * 0.25;

    fragColor = vec4(color, alpha);
}
