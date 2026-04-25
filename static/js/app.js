// UI controller. Wires DOM → generator / strength / history / API.
// CSP-safe: no inline handlers, only delegated listeners from this module.

import { generatePassword, MIN_LENGTH, MAX_LENGTH } from "./generator.js";
import { evaluate } from "./strength.js";
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
    strengthBars: "#strength-bars",
    entropy: "#strength-entropy",
    generate: "#generate-btn",
    copy: "#copy-btn",
    regenerate: "#regenerate-btn",
    useServer: "#use-server",
    historyList: "#history-list",
    historyClear: "#history-clear",
    toast: "#toast",
};

const $ = (sel) => document.querySelector(sel);

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
    const strengthEl = $(SELECTORS.strength);
    strengthEl.dataset.level = String(res.level);
    $(SELECTORS.strengthLevel).textContent = res.label;
    $(SELECTORS.entropy).textContent = `${res.bits.toFixed(1)} bits`;
    const bars = $(SELECTORS.strengthBars).children;
    for (let i = 0; i < bars.length; i++) {
        bars[i].classList.toggle("strength__bar--filled", i < res.level);
    }
}

function showToast(message) {
    const toast = $(SELECTORS.toast);
    toast.textContent = message;
    toast.classList.add("toast--visible");
    setTimeout(() => toast.classList.remove("toast--visible"), 1600);
}

function csrfToken() {
    const match = document.cookie.match(/(?:^|;\s*)csrftoken=([^;]+)/);
    return match ? decodeURIComponent(match[1]) : "";
}

async function generateViaServer(policy) {
    const payload = {
        length: policy.length,
        uppercase: policy.uppercase,
        lowercase: policy.lowercase,
        numbers: policy.numbers,
        symbols: policy.symbols,
        exclude_ambiguous: policy.excludeAmbiguous,
    };
    const res = await fetch("/api/v1/generate", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": csrfToken(),
        },
        body: JSON.stringify(payload),
        credentials: "same-origin",
    });
    if (!res.ok) {
        const err = await res.json().catch(() => ({}));
        throw new Error(err.detail || `API error ${res.status}`);
    }
    return res.json();
}

async function doGenerate() {
    const policy = readPolicy();
    let pw;
    let meta;
    try {
        if ($(SELECTORS.useServer).checked) {
            const resp = await generateViaServer(policy);
            pw = resp.password;
            meta = { level: null, label: resp.strength, bits: resp.entropy_bits };
        } else {
            pw = generatePassword(policy);
            meta = evaluate(policy);
        }
    } catch (err) {
        showToast(err.message || "generation failed");
        return;
    }
    $(SELECTORS.output).textContent = pw;
    renderStrength(policy);
    try {
        await history.add({
            value: pw,
            strength: meta.label,
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
        showToast("copied");
    } catch {
        showToast("clipboard blocked");
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
        empty.textContent = "no entries yet";
        list.appendChild(empty);
        return;
    }
    for (const item of items) {
        const li = document.createElement("li");
        li.className = "history__item";
        const value = document.createElement("span");
        value.className = "history__value history__value--masked";
        value.textContent = item.value;
        value.title = "hover to reveal";
        const meta = document.createElement("span");
        meta.textContent = `${item.length}ch · ${item.strength}`;
        const copyBtn = document.createElement("button");
        copyBtn.type = "button";
        copyBtn.className = "btn btn--ghost btn--icon";
        copyBtn.textContent = "copy";
        copyBtn.setAttribute("aria-label", "copy this password");
        copyBtn.addEventListener("click", async () => {
            try {
                await navigator.clipboard.writeText(item.value);
                showToast("copied");
            } catch {
                showToast("clipboard blocked");
            }
        });
        li.append(value, meta, copyBtn);
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
        showToast("at least one class required");
    }
    renderStrength(readPolicy());
}

function init() {
    const length = $(SELECTORS.length);
    length.min = String(MIN_LENGTH);
    length.max = String(MAX_LENGTH);

    syncLengthLabel();
    renderStrength(readPolicy());

    length.addEventListener("input", () => {
        syncLengthLabel();
        renderStrength(readPolicy());
    });

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
            showToast("history cleared");
        });
    }

    renderHistory();
}

if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
} else {
    init();
}
