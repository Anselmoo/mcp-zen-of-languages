/* eslint-disable no-undef -- document$ is provided by mkdocs-material */
document$.subscribe(function () {
    document.documentElement.classList.add("zen-ready");

    // Code hover — event delegation on .md-content (idempotent)
    const content = document.querySelector(".md-content");
    if (content && !content.dataset.zenBound) {
        content.dataset.zenBound = "true";
        content.addEventListener(
            "mouseenter",
            (e) => {
                const code = e.target.closest("pre code");
                if (code) code.parentElement?.classList.add("zen-code-hover");
            },
            true,
        );
        content.addEventListener(
            "mouseleave",
            (e) => {
                const code = e.target.closest("pre code");
                if (code)
                    code.parentElement?.classList.remove("zen-code-hover");
            },
            true,
        );
    }

    // Quote rotation — per navigation
    const quotes = [
        "Make the codebase quieter than you found it.",
        "Small detectors, clear signals, calm systems.",
        "Simplicity is performance for the human brain.",
    ];
    const target = document.querySelector(".md-copyright div");
    if (target) {
        const idx = Math.floor(Date.now() / 1000) % quotes.length;
        target.setAttribute("title", quotes[idx]);
    }
});
