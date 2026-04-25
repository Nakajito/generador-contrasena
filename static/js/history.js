// IndexedDB-backed history (last N entries). Never leaves the browser.

const DB_NAME = "crypt_type";
const STORE = "history";
const DB_VERSION = 1;
const MAX_ENTRIES = 20;

function open() {
    return new Promise((resolve, reject) => {
        const req = indexedDB.open(DB_NAME, DB_VERSION);
        req.onupgradeneeded = () => {
            const db = req.result;
            if (!db.objectStoreNames.contains(STORE)) {
                const store = db.createObjectStore(STORE, {
                    keyPath: "id",
                    autoIncrement: true,
                });
                store.createIndex("createdAt", "createdAt");
            }
        };
        req.onsuccess = () => resolve(req.result);
        req.onerror = () => reject(req.error);
    });
}

function tx(db, mode) {
    return db.transaction(STORE, mode).objectStore(STORE);
}

export async function add(entry) {
    const db = await open();
    await new Promise((res, rej) => {
        const req = tx(db, "readwrite").add({
            value: entry.value,
            strength: entry.strength,
            length: entry.length,
            createdAt: Date.now(),
        });
        req.onsuccess = () => res();
        req.onerror = () => rej(req.error);
    });
    await trim(db);
    db.close();
}

async function trim(db) {
    const items = await new Promise((res, rej) => {
        const req = tx(db, "readonly").index("createdAt").getAll();
        req.onsuccess = () => res(req.result);
        req.onerror = () => rej(req.error);
    });
    if (items.length <= MAX_ENTRIES) return;
    const victims = items
        .sort((a, b) => a.createdAt - b.createdAt)
        .slice(0, items.length - MAX_ENTRIES);
    await Promise.all(
        victims.map(
            (v) =>
                new Promise((res, rej) => {
                    const req = tx(db, "readwrite").delete(v.id);
                    req.onsuccess = () => res();
                    req.onerror = () => rej(req.error);
                })
        )
    );
}

export async function list() {
    const db = await open();
    const items = await new Promise((res, rej) => {
        const req = tx(db, "readonly").index("createdAt").getAll();
        req.onsuccess = () => res(req.result);
        req.onerror = () => rej(req.error);
    });
    db.close();
    return items.sort((a, b) => b.createdAt - a.createdAt);
}

export async function clear() {
    const db = await open();
    await new Promise((res, rej) => {
        const req = tx(db, "readwrite").clear();
        req.onsuccess = () => res();
        req.onerror = () => rej(req.error);
    });
    db.close();
}
