// Minimal shared JS: theme toggle persistence, confirmations, and light UX helpers.
(function () {
    const saved = localStorage.getItem("theme");
    if (saved) document.documentElement.dataset.theme = saved;

    // Expose a tiny helper for confirmations
    window.lekha = {
        confirm(message) {
            return window.confirm(message || "Are you sure?");
        }
    };
})();
