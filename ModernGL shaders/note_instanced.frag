#version 330 core

in vec2 v_uv;          // 0..1 inside quad
in vec2 v_fragCoord;   // pixel coords
in vec2 v_pos;
in vec2 v_size; 
in vec4 v_color1;      // start color
in vec4 v_color2;      // end color
in float v_seed;
in float v_phase;

uniform vec2 u_resolution;
uniform float leftCutoff;
uniform float rightCutoff;
uniform float borderRadius;
uniform float glowRadius;
uniform float glowStrength;
uniform float blendPower;
uniform float time;


out vec4 FragColor;

float hash(vec2 p) {
    return fract(sin(dot(p ,vec2(127.1,311.7))) * 43758.5453123);
}

vec2 cubicBezier(vec2 A, vec2 B, vec2 C, vec2 D, float t) {
    vec2 AB = mix(A, B, t);
    vec2 BC = mix(B, C, t);
    vec2 CD = mix(C, D, t);
    vec2 ABC = mix(AB, BC, t);
    vec2 BCD = mix(BC, CD, t);
    return mix(ABC, BCD, t);
}

float roundedBoxSDF(vec2 position, vec2 halfSize, float cornerRadius) {
    position = abs(position) - halfSize + cornerRadius;
    return length(max(position, 0.0)) + min(max(position.x, position.y), 0.0) - cornerRadius;
}

void main() {
    // approx half size from v_uv and v_fragCoord
    vec2 half = v_size / 2;

    vec2 center = v_pos + half;
    vec2 p = v_fragCoord - center;

    vec3 finalColor = vec3(0.0);
    float alpha = 0.0;
    float curveIntensity = 0.0;

    // Rounded box SDF
    float dist = roundedBoxSDF(p, half, borderRadius);

    // Draw dynamic curves (simplified: 1 curve per instance for demo)
    if (dist < 0.0) {
        int maxCurves = 2;
        float lifetime = 4.0;
        float cyclePadding = 2.0;

        for (int i = 0; i < maxCurves; ++i) {
            float id = float(i);
            float seed = hash(vec2(v_seed, id));
            float delay = hash(vec2(v_seed, id + 42.0)) * cyclePadding;

            float totalTime = time + seed * 100.0;
            float cycleLength = lifetime + cyclePadding;
            float cycleTime = mod(totalTime, cycleLength);

            if (cycleTime < delay || cycleTime > delay + lifetime) {
                continue;
            }

            float localTime = (cycleTime - delay) / lifetime;
            float fade = smoothstep(0.0, 0.2, localTime) * smoothstep(1.0, 0.8, localTime);

            float edgeOffset = 10.0;
            float edgeType = floor(4.0 * hash(vec2(v_seed + id, floor(totalTime / cycleLength))));

            vec2 A, B, C, D;

            if (edgeType < 1.0) {
                A = vec2(mix(-half.x, half.x, hash(vec2(id, 1.0))), half.y + edgeOffset);
                D = vec2(mix(-half.x, half.x, hash(vec2(id, 2.0))), -half.y);
            } else if (edgeType < 2.0) {
                A = vec2(half.x + edgeOffset, mix(-half.y, half.y, hash(vec2(id, 3.0))));
                D = vec2(-half.x, mix(-half.y, half.y, hash(vec2(id, 4.0))));
            } else if (edgeType < 3.0) {
                A = vec2(mix(-half.x, half.x, hash(vec2(id, 5.0))), -half.y - edgeOffset);
                D = vec2(mix(-half.x, half.x, hash(vec2(id, 6.0))), half.y);
            } else {
                A = vec2(-half.x - edgeOffset, mix(-half.y, half.y, hash(vec2(id, 7.0))));
                D = vec2(half.x, mix(-half.y, half.y, hash(vec2(id, 8.0))));
            }

            B = mix(A, D, 0.33) + vec2(sin(time + id) * 10.0, cos(time + id) * 10.0);
            C = mix(A, D, 0.66) + vec2(cos(time * 0.5 + id) * 10.0, sin(time * 0.5 + id) * 10.0);
            
            float minDist = 1e5;
            for (float t = 0.0; t <= 1.0; t += 0.02) {
                vec2 pt = cubicBezier(A, B, C, D, t);
                float d = length(p - pt);
                minDist = min(minDist, d);
            }
            curveIntensity += smoothstep(1.5, 0.0, minDist) * fade;
        }
    }

    // Glow
    float pulse = 0.5 + 0.5 * sin(time * 3.0 + v_phase);
    float dynamicGlowStrength = pulse * glowStrength;
    
    float glow = 0.0;
    if (dist > 0.0 && dist < glowRadius) {
        float t = dist / glowRadius;
        glow = pow(1.0 - t, blendPower) * dynamicGlowStrength;
    }



    
    
    
    // Color blending
    float gx = v_fragCoord.x / u_resolution.x;
    vec3 noteColor;
    if (gx < leftCutoff) noteColor = v_color1.rgb;
    else if (gx > rightCutoff) noteColor = v_color2.rgb;
    else {
        float t = (gx - leftCutoff) / max(0.0001, rightCutoff - leftCutoff);
        noteColor = mix(v_color1.rgb, v_color2.rgb, clamp(t, 0.0, 1.0));
    }

    //Color logic
    if (dist > 0.0) {
        finalColor = noteColor;
        alpha = glow * 1.0;
    }

    float whiteEnd = 0.0;
    float blendEnd = -7.0;

    if (dist >= whiteEnd && dist < 0.0) {
        finalColor = vec3(1.0);
    } else if (dist >= blendEnd && dist < whiteEnd) {
        float t = smoothstep(whiteEnd, blendEnd, dist);
        finalColor = mix(vec3(1.0), noteColor, t);
    } else if (dist < blendEnd) {
        finalColor = noteColor;
    }



    // Shape alpha
    float shapeAlpha = smoothstep(0.0, -1.0, dist);
    float finalAlpha = shapeAlpha + alpha;

    finalColor = mix(finalColor, vec3(1.0), curveIntensity);

    FragColor = vec4(finalColor, finalAlpha);
    if (FragColor.a <= 0.001) discard;
}
