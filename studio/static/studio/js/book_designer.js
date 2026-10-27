// Shows a preview of the current preset selection. The DOCX itself is
// generated server-side; this is purely a hint to the user.
(function () {
    const select = document.querySelector('select[name="preset"]');
    const hint = document.getElementById("preset-hint");
    if (!select || !hint) return;
    const descriptions = {
        classic_literary: "A5 · literary margins · Noto Serif Bengali 11pt · 1.4 line height",
        modern_minimal: "A5 · even margins · Noto Sans Bengali 10.5pt · no first-line indent",
        academic_textbook: "A4 · generous margins · Noto Serif Bengali 11pt · dense leading",
        clean_office: "A4 · standard margins · Noto Sans Bengali 11pt · 1.15 line height",
    };
    function update() {
        hint.textContent = descriptions[select.value] || "";
    }
    select.addEventListener("change", update);
    update();
})();
