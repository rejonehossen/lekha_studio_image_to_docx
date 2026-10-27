// Editor helpers. Currently a plain textarea; toolbar commands operate on
// textarea selections using conservative insert/wrap behavior.
(function () {
    const area = document.querySelector(".editor-area");
    const toolbar = document.querySelector(".editor-toolbar");
    if (!area || !toolbar) return;

    function wrapSelection(prefix, suffix) {
        const start = area.selectionStart;
        const end = area.selectionEnd;
        const before = area.value.slice(0, start);
        const sel = area.value.slice(start, end);
        const after = area.value.slice(end);
        area.value = before + prefix + sel + suffix + after;
        area.selectionStart = start + prefix.length;
        area.selectionEnd = end + prefix.length;
        area.focus();
    }

    toolbar.addEventListener("click", (e) => {
        const cmd = e.target.dataset.cmd;
        if (!cmd) return;
        if (cmd === "bold") wrapSelection("**", "**");
        else if (cmd === "italic") wrapSelection("_", "_");
        else if (cmd === "underline") wrapSelection("<u>", "</u>");
        else if (cmd === "insertUnorderedList") wrapSelection("- ", "");
        else if (cmd === "insertOrderedList") wrapSelection("1. ", "");
    });

    // Autosave: every 20s if content changed. Uses the normal Django POST
    // endpoint (same form) — not a REST API.
    const form = area.closest("form");
    const token = form && form.querySelector('[name="csrfmiddlewaretoken"]');
    let lastSaved = area.value;
    if (form && token) {
        setInterval(() => {
            if (area.value === lastSaved) return;
            const body = new FormData();
            body.append("csrfmiddlewaretoken", token.value);
            body.append("action", "save");
            body.append("text", area.value);
            fetch(form.action || window.location.href, {
                method: "POST",
                body,
                credentials: "same-origin",
            }).then((r) => {
                if (r.ok) lastSaved = area.value;
            }).catch(() => { /* silent; user can still click Save */ });
        }, 20000);
    }
})();
