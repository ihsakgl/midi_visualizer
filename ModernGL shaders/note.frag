#version 330 core

in vec2 fragCoord;
out vec4 FragColor;

uniform vec2 notePosition;
uniform vec2 noteSize;
uniform vec4 noteColor;
uniform float glowRadius;
uniform float glowStrength;
uniform float blendPower;
uniform float borderRadius;
uniform float time;
uniform float phase;
uniform float noteSeed;

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
    vec2 half = noteSize * 0.5;
    vec2 center = notePosition + half;
    vec2 p = fragCoord - center;

    vec3 finalColor = vec3(0.0);
    float alpha = 0.0;
    float curveIntensity = 0.0;

    // Discard if completely outside bounding box (optimization)
    vec2 totalHalf = half + vec2(glowRadius);
    if (abs(p.x) > totalHalf.x || abs(p.y) > totalHalf.y) {
        discard;
    }

    float dist = roundedBoxSDF(p, half, borderRadius);

    // Draw dynamic curves
    if (dist < 0.0) {
        int maxCurves = 2;
        float lifetime = 4.0;
        float cyclePadding = 2.0; // spawn boşluğu

        for (int i = 0; i < maxCurves; ++i) {
            float id = float(i);
            float seed = hash(vec2(noteSeed, id));
            float delay = hash(vec2(noteSeed, id + 42.0)) * cyclePadding;
            
            float totalTime = time + seed * 100.0;
            float cycleLength = lifetime + cyclePadding;
            float cycleTime = mod(totalTime, cycleLength);

            if (cycleTime < delay || cycleTime > delay + lifetime) {
                continue; // Bu eğri şu an aktif değil
            }

            float localTime = (cycleTime - delay) / lifetime;
            float fade = smoothstep(0.0, 0.2, localTime) * smoothstep(1.0, 0.8, localTime);

            // Kenar belirleme ve A/D noktalarının hafif dışta başlaması
            float edgeOffset = 10.0;
            float edgeType = floor(4.0 * hash(vec2(noteSeed + id, floor(totalTime / cycleLength))));

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

            float curveAlpha = smoothstep(1.5, 0.0, minDist) * fade;
            curveIntensity += curveAlpha;
        }
    }

    // Glow dynamics
    float pulse = sin(time * 3.0 + phase);
    pulse = 0.5 + 0.5 * pulse;
    float dynamicGlowStrength = pulse * glowStrength;

    float glow = 0.0;
    if (dist > 0.0 && dist < glowRadius) {
        float t = dist / glowRadius;
        glow = pow(1.0 - t, blendPower) * dynamicGlowStrength;
    }

    // Color logic
    if (dist > 0.0) {
        finalColor = noteColor.rgb;
        alpha = glow * noteColor.a;
    }

    float whiteEnd = 0.0;
    float blendEnd = -7.0;

    if (dist >= whiteEnd && dist < 0.0) {
        finalColor = vec3(1.0);
    } else if (dist >= blendEnd && dist < whiteEnd) {
        float t = smoothstep(whiteEnd, blendEnd, dist);
        finalColor = mix(vec3(1.0), noteColor.rgb, t);
    } else if (dist < blendEnd) {
        finalColor = noteColor.rgb;
    }

    float shapeAlpha = smoothstep(0.0, -1.0, dist);
    float finalAlpha = shapeAlpha + alpha;

    // Add curves on top (white lines)
    finalColor = mix(finalColor, vec3(1.0), curveIntensity);

    FragColor = vec4(finalColor, finalAlpha);
}
