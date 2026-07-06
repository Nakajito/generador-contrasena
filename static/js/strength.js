// Password strength (entropy-bits) — mirrors server logic for consistency.

import { POOLS, AMBIGUOUS } from "./generator.js";

export const LEVELS = Object.freeze({
    1: "Débil",
    2: "Media",
    3: "Fuerte",
    4: "Muy fuerte",
});

export const LEVEL_COLORS = Object.freeze({
    1: "oklch(0.62 0.19 25)",
    2: "oklch(0.75 0.15 85)",
    3: "oklch(0.6 0.15 150)",
    4: "#5A9BE0",
});

export function colorForLevel(level) {
    return LEVEL_COLORS[level] || LEVEL_COLORS[1];
}

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

const CRACK_TIME_UNITS = [
    [31536000000, "milenios"],
    [31536000, "años"],
    [2592000, "meses"],
    [86400, "días"],
    [3600, "horas"],
    [60, "minutos"],
    [1, "segundos"],
];

// Puerto directo del cálculo del mockup: ataque offline a 1e10 intentos/seg,
// tiempo promedio = mitad del espacio de combinaciones.
export function formatCrackTime(bits) {
    const guessesPerSecond = 1e10;
    const combos = Math.pow(2, bits);
    const seconds = combos / guessesPerSecond / 2;
    if (seconds < 1) return "instantáneo";
    for (const [unitSeconds, name] of CRACK_TIME_UNITS) {
        if (seconds >= unitSeconds) {
            const val = seconds / unitSeconds;
            const rounded =
                val > 1000 ? val.toExponential(1) : Math.round(val).toLocaleString("es");
            return `${rounded} ${name}`;
        }
    }
    return "segundos";
}

export function evaluate(policy) {
    const size = alphabetSize(policy);
    const bits = entropyBits(policy.length, size);
    const level = classify(bits);
    return { level, label: LEVELS[level], bits, alphabetSize: size };
}
