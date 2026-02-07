#version 330 core

uniform sampler2D Texture0;
uniform float alpha;
uniform vec2 texelSize;
uniform float sigma; 
uniform vec3 smokeColor1;
uniform vec3 smokeColor2;
uniform float leftCutoff;
uniform float rightCutoff;
uniform bool horizontal;  // true = horizontal pass, false = vertical pass

in vec2 uv;
out vec4 fragColor;

// 7-sample 1D Gaussian weights
 //   float k[9] = float[](0.5, 1, 0.5, 1, 6, 1, 0.5, 1, 0.5);


void main() {
    vec4 sum = vec4(0.0);
    float k[7] = float[](0.4,  1.0,  1.5,  6.0,  1.5,  1.0,  0.4);

    for (int i = 0; i < 7; i++) {
        k[i] = k[i] / 23.6;
    }
    const int radius = 3;


    

    // 1D blur along horizontal or vertical
    for (int i = -3; i <= 3; i++) {
        vec2 offset;
        if (horizontal) {
            offset = vec2(float(i) * sigma * texelSize.x, 0.0);
        } else {
            offset = vec2(0.0, float(i) * sigma * texelSize.y);
        }


      
        sum += texture(Texture0, uv + offset) * k[i + radius];
    }

    // Smoke color blending
    vec3 smokeColor;
    if (uv.x < leftCutoff) {
        smokeColor = smokeColor1;
    } else if (uv.x > rightCutoff) {
        smokeColor = smokeColor2;
    } else {
        float t = clamp((uv.x - leftCutoff) / (rightCutoff - leftCutoff), 0.0, 1.0);
        smokeColor = mix(smokeColor1, smokeColor2, t);
    }

    vec4 blurred = sum;
    blurred.rgb = mix(blurred.rgb, smokeColor, 0.5);

    fragColor = vec4(blurred.rgb, blurred.a * alpha);
}
