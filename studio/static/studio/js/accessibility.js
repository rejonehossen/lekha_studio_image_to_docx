// Keyboard focus helpers: highlight focused elements and ensure Escape closes
// open <dialog>s.
(function () {
    document.addEventListener("keydown", (e) => {
        if (e.key !== "Escape") return;
        document.querySelectorAll("dialog[open]").forEach((d) => d.close());
    });
})();
