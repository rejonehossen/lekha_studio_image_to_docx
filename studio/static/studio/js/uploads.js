// Drag-and-drop helper for the upload zone. Progressive enhancement only —
// the form works with plain file input without this script.
(function () {
    const zone = document.getElementById("upload-zone");
    const input = document.getElementById("upload-input");
    if (!zone || !input) return;

    ["dragenter", "dragover"].forEach((ev) =>
        zone.addEventListener(ev, (e) => {
            e.preventDefault();
            zone.classList.add("dragover");
        })
    );
    ["dragleave", "drop"].forEach((ev) =>
        zone.addEventListener(ev, (e) => {
            e.preventDefault();
            zone.classList.remove("dragover");
        })
    );
    zone.addEventListener("drop", (e) => {
        if (!e.dataTransfer || !e.dataTransfer.files) return;
        input.files = e.dataTransfer.files;
        input.dispatchEvent(new Event("change", { bubbles: true }));
    });
})();
