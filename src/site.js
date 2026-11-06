// Two small enhancements. The page works without this file.

// 1. Highlight the sidebar link for the section currently on screen.
(function () {
    const links = new Map(
        [...document.querySelectorAll(".toc a[href^='#']")].map((a) => [a.getAttribute("href").slice(1), a])
    );
    const sections = [...links.keys()].map((id) => document.getElementById(id)).filter(Boolean);
    if (!("IntersectionObserver" in window) || sections.length === 0) return;

    const visible = new Set();
    const update = () => {
        // The first section (in page order) that is on screen wins.
        const active = sections.find((s) => visible.has(s.id));
        links.forEach((a, id) => a.setAttribute("aria-current", String(active && id === active.id)));
    };
    const observer = new IntersectionObserver((entries) => {
        entries.forEach((e) => (e.isIntersecting ? visible.add(e.target.id) : visible.delete(e.target.id)));
        update();
    }, { rootMargin: "0px 0px -60% 0px" });
    sections.forEach((s) => observer.observe(s));
})();

// 2. Send the contact form in place instead of leaving the page.
(function () {
    const form = document.querySelector("form.contact");
    if (!form || !window.fetch) return;
    const status = form.querySelector(".form-status");
    const button = form.querySelector("button[type=submit]");

    form.addEventListener("submit", async (event) => {
        event.preventDefault();
        button.disabled = true;
        status.textContent = "Sending…";
        try {
            const response = await fetch(form.action.replace("formsubmit.co/", "formsubmit.co/ajax/"), {
                method: "POST",
                headers: { Accept: "application/json" },
                body: new FormData(form),
            });
            if (!response.ok) throw new Error(String(response.status));
            form.reset();
            status.textContent = "Thanks, I’ll be in touch.";
        } catch {
            status.textContent = "That didn’t send. Please try again, or reach me on LinkedIn.";
        } finally {
            button.disabled = false;
        }
    });
})();
