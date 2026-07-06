// UI controller. Wires DOM → generator / strength / history.
// CSP-safe: no inline handlers, only delegated listeners from this module.

import { generatePassword, MIN_LENGTH, MAX_LENGTH } from "./generator.js";
import { evaluate, colorForLevel, formatCrackTime } from "./strength.js";
import * as history from "./history.js";

const SELECTORS = {
    length: "#length",
    lengthValue: "#length-value",
    uppercase: "#uppercase",
    lowercase: "#lowercase",
    numbers: "#numbers",
    symbols: "#symbols",
    excludeAmbiguous: "#exclude-ambiguous",
    output: "#password-output",
    strength: "#strength",
    strengthLevel: "#strength-level",
    strengthFill: "#strength-fill",
    strengthCrackTime: "#strength-crack-time",
    entropy: "#strength-entropy",
    generate: "#generate-btn",
    copy: "#copy-btn",
    regenerate: "#regenerate-btn",
    historyList: "#history-list",
    historyClear: "#history-clear",
    toast: "#toast",
};

const $ = (sel) => document.querySelector(sel);

let pulseTimer;

function readPolicy() {
    return {
        length: Number($(SELECTORS.length).value),
        uppercase: $(SELECTORS.uppercase).checked,
        lowercase: $(SELECTORS.lowercase).checked,
        numbers: $(SELECTORS.numbers).checked,
        symbols: $(SELECTORS.symbols).checked,
        excludeAmbiguous: $(SELECTORS.excludeAmbiguous).checked,
    };
}

function renderStrength(policy) {
    const res = evaluate(policy);
    const color = colorForLevel(res.level);
    $(SELECTORS.strength).dataset.level = String(res.level);
    $(SELECTORS.strengthLevel).textContent = res.label;
    $(SELECTORS.strengthLevel).style.color = color;
    $(SELECTORS.entropy).textContent = `${res.bits.toFixed(1)} bits de entropía`;
    $(SELECTORS.strengthFill).style.width = `${Math.min(100, (res.bits / 100) * 100)}%`;
    $(SELECTORS.strengthFill).style.background = color;
    $(SELECTORS.strengthCrackTime).textContent = formatCrackTime(res.bits);
    return res;
}

function pulsePasswordDisplay() {
    const el = $(SELECTORS.output).closest(".password-display");
    if (!el) return;
    el.classList.add("password-display--pulse");
    clearTimeout(pulseTimer);
    pulseTimer = setTimeout(() => el.classList.remove("password-display--pulse"), 320);
}

function showToast(message) {
    const toast = $(SELECTORS.toast);
    toast.textContent = message;
    toast.classList.add("toast--visible");
    setTimeout(() => toast.classList.remove("toast--visible"), 1600);
}

async function doGenerate() {
    const policy = readPolicy();
    let pw;
    try {
        pw = generatePassword(policy);
    } catch (err) {
        showToast(err.message || "no se pudo generar");
        return;
    }
    $(SELECTORS.output).textContent = pw;
    const meta = renderStrength(policy);
    pulsePasswordDisplay();
    try {
        await history.add({
            value: pw,
            strength: meta.label,
            level: meta.level,
            entropyBits: Math.round(meta.bits),
            length: policy.length,
        });
    } catch {
        /* IndexedDB unavailable (private mode etc.) — silent */
    }
    await renderHistory();
}

async function copyCurrent() {
    const pw = $(SELECTORS.output).textContent;
    if (!pw || pw.trim() === "—") return;
    try {
        await navigator.clipboard.writeText(pw);
        showToast("copiado");
    } catch {
        showToast("portapapeles bloqueado");
    }
}

async function renderHistory() {
    const list = $(SELECTORS.historyList);
    if (!list) return;
    let items = [];
    try {
        items = await history.list();
    } catch {
        /* ignore */
    }
    list.innerHTML = "";
    if (!items.length) {
        const empty = document.createElement("li");
        empty.className = "history__empty";
        empty.textContent = "Aún no hay contraseñas generadas en esta sesión.";
        list.appendChild(empty);
        return;
    }
    for (const item of items) {
        const li = document.createElement("li");
        li.className = "history__item";

        const main = document.createElement("span");
        main.className = "history__item-main";

        const dot = document.createElement("span");
        dot.className = "history__dot";
        dot.style.background = colorForLevel(item.level);

        const value = document.createElement("span");
        value.className = "history__value history__value--masked";
        value.textContent = item.value;
        value.title = "pasa el mouse para revelar";

        main.append(dot, value);

        const meta = document.createElement("span");
        meta.className = "history__meta";
        meta.textContent = `${item.entropyBits ?? "—"} bits · ${item.length}ch`;

        const copyBtn = document.createElement("button");
        copyBtn.type = "button";
        copyBtn.className = "btn btn--ghost btn--icon";
        copyBtn.textContent = "📋";
        copyBtn.setAttribute("aria-label", "copiar esta contraseña");
        copyBtn.addEventListener("click", async () => {
            try {
                await navigator.clipboard.writeText(item.value);
                showToast("copiado");
            } catch {
                showToast("portapapeles bloqueado");
            }
        });
        li.append(main, meta, copyBtn);
        list.appendChild(li);
    }
}

function syncLengthLabel() {
    $(SELECTORS.lengthValue).textContent = $(SELECTORS.length).value;
}

function ensureAtLeastOneClass() {
    const keys = ["uppercase", "lowercase", "numbers", "symbols"];
    const anyChecked = keys.some((k) => $(SELECTORS[k]).checked);
    if (!anyChecked) {
        // Re-enable uppercase as fallback.
        $(SELECTORS.uppercase).checked = true;
        showToast("se requiere al menos una opción");
    }
    doGenerate();
}

function init() {
    const length = $(SELECTORS.length);
    length.min = String(MIN_LENGTH);
    length.max = String(MAX_LENGTH);

    syncLengthLabel();

    // Live label + strength preview while dragging, actual regeneration once
    // the drag/keypress settles — regenerating (and writing to history) on
    // every "input" tick would flood the history with in-between lengths.
    length.addEventListener("input", () => {
        syncLengthLabel();
        renderStrength(readPolicy());
    });
    length.addEventListener("change", doGenerate);

    ["uppercase", "lowercase", "numbers", "symbols", "excludeAmbiguous"].forEach(
        (key) => {
            $(SELECTORS[key]).addEventListener("change", ensureAtLeastOneClass);
        }
    );

    $(SELECTORS.generate).addEventListener("click", doGenerate);
    $(SELECTORS.regenerate).addEventListener("click", doGenerate);
    $(SELECTORS.copy).addEventListener("click", copyCurrent);

    const clearBtn = $(SELECTORS.historyClear);
    if (clearBtn) {
        clearBtn.addEventListener("click", async () => {
            await history.clear();
            await renderHistory();
            showToast("historial borrado");
        });
    }

    doGenerate();
}

if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
} else {
    init();
}
