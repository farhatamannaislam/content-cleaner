const tokenEl = document.getElementById("token") as HTMLInputElement;
const inputEl = document.getElementById("input") as HTMLTextAreaElement;
const outputEl = document.getElementById("output") as HTMLTextAreaElement;
const statusEl = document.getElementById("status") as HTMLElement;
const btn = document.getElementById("btn") as HTMLButtonElement;
const clearBtn = document.getElementById("clear") as HTMLButtonElement;
const copyBtn = document.getElementById("copy") as HTMLButtonElement;

function setStatus(message: string, type: "muted" | "ok" | "error" = "muted") {
  statusEl.textContent = message;
  statusEl.className = `status ${type}`;
}

// Remember token in localStorage
try {
  const saved = localStorage.getItem("cc_token");
  if (saved) tokenEl.value = saved;
  tokenEl.addEventListener("input", () =>
    localStorage.setItem("cc_token", tokenEl.value)
  );
} catch {
  // ignore storage errors
}

async function doClean(): Promise<void> {
  const token = tokenEl.value.trim();
  const text = inputEl.value;

  setStatus("", "muted");

  if (!token) {
    setStatus("Bitte Token eingeben.", "error");
    return;
  }
  btn.disabled = true;

  try {
    const resp = await fetch("http://127.0.0.1:8000/clean", {
      method: "POST",
      headers: {
        Authorization: "Bearer " + token,
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ text }),
    });

    const data = (await resp.json()) as { clean?: string; detail?: string };

    if (!resp.ok) {
      setStatus(`${resp.status}: ${data.detail || "Fehler"}`, "error");
      return;
    }

    outputEl.value = data.clean ?? "";
    setStatus("Bereinigung erfolgreich.", "ok");
  } catch (e) {
    const err = e as Error;
    setStatus("Netzwerkfehler: " + err.message, "error");
  } finally {
    btn.disabled = false;
  }
}

// Event listeners
btn.addEventListener("click", doClean);

clearBtn.addEventListener("click", () => {
  inputEl.value = "";
  inputEl.focus();
});

copyBtn.addEventListener("click", async () => {
  try {
    await navigator.clipboard.writeText(outputEl.value || "");
    setStatus("In Zwischenablage kopiert.", "ok");
  } catch {
    setStatus("Kopieren fehlgeschlagen.", "error");
  }
});

// Cmd/Ctrl + Enter to submit
document.addEventListener("keydown", (e: KeyboardEvent) => {
  if ((e.metaKey || e.ctrlKey) && e.key === "Enter") {
    doClean();
  }
});
