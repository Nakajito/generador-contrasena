// Client-side password generator (crypto.getRandomValues).
// Mirrors the server-side policy so local results match server fallback.

export const MIN_LENGTH = 8;
export const MAX_LENGTH = 128;

export const POOLS = Object.freeze({
    uppercase: "ABCDEFGHIJKLMNOPQRSTUVWXYZ",
    lowercase: "abcdefghijklmnopqrstuvwxyz",
    numbers: "0123456789",
    symbols: "!@#$%^&*()-_=+[]{};:,.<>?/~",
});

export const AMBIGUOUS = new Set("Il1O0o`'\"B8S5Z2");

export class PolicyError extends Error {
    constructor(message) {
        super(message);
        this.name = "PolicyError";
    }
}

/**
 * @typedef {Object} Policy
 * @property {number} length
 * @property {boolean} uppercase
 * @property {boolean} lowercase
 * @property {boolean} numbers
 * @property {boolean} symbols
 * @property {boolean} excludeAmbiguous
 */

function getActivePools(policy) {
    const mapping = [
        ["uppercase", POOLS.uppercase],
        ["lowercase", POOLS.lowercase],
        ["numbers", POOLS.numbers],
        ["symbols", POOLS.symbols],
    ];
    let pools = mapping
        .filter(([key]) => policy[key])
        .map(([, chars]) => chars);
    if (policy.excludeAmbiguous) {
        pools = pools.map((p) =>
            [...p].filter((c) => !AMBIGUOUS.has(c)).join("")
        );
        if (pools.some((p) => !p.length)) {
            throw new PolicyError(
                "ambiguous exclusion emptied a required character class"
            );
        }
    }
    return pools;
}

function randInt(maxExclusive) {
    // Unbiased rejection sampling using Uint32.
    if (maxExclusive <= 0) throw new RangeError("maxExclusive must be > 0");
    const limit = Math.floor(0x100000000 / maxExclusive) * maxExclusive;
    const buf = new Uint32Array(1);
    let val;
    do {
        crypto.getRandomValues(buf);
        val = buf[0];
    } while (val >= limit);
    return val % maxExclusive;
}

function choice(str) {
    return str[randInt(str.length)];
}

/**
 * @param {Policy} policy
 * @returns {string}
 */
export function generatePassword(policy) {
    if (!Number.isInteger(policy.length) || policy.length < MIN_LENGTH || policy.length > MAX_LENGTH) {
        throw new PolicyError(
            `length must be an integer in [${MIN_LENGTH}, ${MAX_LENGTH}]`
        );
    }
    if (!(policy.uppercase || policy.lowercase || policy.numbers || policy.symbols)) {
        throw new PolicyError("at least one character class must be enabled");
    }
    const pools = getActivePools(policy);
    const chars = pools.map(choice);
    const combined = pools.join("");
    while (chars.length < policy.length) {
        chars.push(choice(combined));
    }
    // Durstenfeld shuffle with crypto randomness.
    for (let i = chars.length - 1; i > 0; i--) {
        const j = randInt(i + 1);
        [chars[i], chars[j]] = [chars[j], chars[i]];
    }
    return chars.join("");
}
