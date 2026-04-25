// Password strength (entropy-bits) — mirrors server logic for consistency.

import { POOLS, AMBIGUOUS } from "./generator.js";

export const LEVELS = Object.freeze({
    1: "weak",
    2: "fair",
    3: "strong",
    4: "excellent",
});

export function alphabetSize(policy) {
    let size = 0;
    for (const [key, chars] of Object.entries(POOLS)) {
        if (!policy[key]) continue;
        size += policy.excludeAmbiguous
            ? [...chars].filter((c) => !AMBIGUOUS.has(c)).length
            : chars.length;
    }
    return size;
}

export function entropyBits(length, size) {
    if (length <= 0 || size <= 0) return 0;
    return length * Math.log2(size);
}

export function classify(bits) {
    if (bits < 40) return 1;
    if (bits < 60) return 2;
    if (bits < 80) return 3;
    return 4;
}

export function evaluate(policy) {
    const size = alphabetSize(policy);
    const bits = entropyBits(policy.length, size);
    const level = classify(bits);
    return { level, label: LEVELS[level], bits, alphabetSize: size };
}
