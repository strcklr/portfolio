// Small enhancements. The page works without this file.

// Light/dark toggle. The <head> script already applied a saved choice; with no
//    choice saved, the CSS follows the visitor's system setting.
(function () {
    const button = document.querySelector(".theme-toggle");
    if (!button) return;
    const root = document.documentElement;
    const prefersLight = window.matchMedia("(prefers-color-scheme: light)");
    const meta = document.querySelector('meta[name="theme-color"]');
    const current = () => root.getAttribute("data-theme") || (prefersLight.matches ? "light" : "dark");

    const sync = () => {
        const theme = current();
        button.setAttribute("aria-label", theme === "dark" ? "Switch to light mode" : "Switch to dark mode");
        if (meta) meta.setAttribute("content", getComputedStyle(root).getPropertyValue("--bg").trim());
    };
    button.addEventListener("click", () => {
        const next = current() === "dark" ? "light" : "dark";
        root.setAttribute("data-theme", next);
        try { localStorage.setItem("theme", next); } catch (e) { /* private mode: still switches */ }
        sync();
    });
    prefersLight.addEventListener("change", sync);
    sync();
})();

// Highlight the sidebar link for the section currently on screen.
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

// Send the contact form in place instead of leaving the page.
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
            if (window.goatcounter && window.goatcounter.count) {
                window.goatcounter.count({ path: "contact-form-sent", title: "Contact form sent", event: true });
            }
        } catch {
            status.textContent = "That didn’t send. Please try again, or reach me on LinkedIn.";
        } finally {
            button.disabled = false;
        }
    });
})();

// Timeline progress: in each company's role timeline, a dot follows your scroll from the
//    current role down to the oldest one, filling the line behind it and lighting up each
//    role it passes. Skipped entirely for visitors who prefer reduced motion.
(function () {
    if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) return;
    const timelines = [...document.querySelectorAll(".timeline")];
    if (timelines.length === 0) return;
    const ANCHOR = 0.45; // the marker tracks a line 45% of the way down the window
    const DOT = 13;      // a role's dot center, in px below the top of the role

    let queued = false;
    const update = () => {
        queued = false;
        const anchor = window.innerHeight * ANCHOR;
        for (const list of timelines) {
            const top = list.getBoundingClientRect().top;
            const roles = [...list.children];
            const stops = roles.map((r) => r.offsetTop + DOT); // dot centers within the list
            const first = stops[0];
            const last = stops[stops.length - 1];
            const y = Math.min(Math.max(anchor - top, first), last);
            list.style.setProperty("--y", `${y}px`);
            roles.forEach((role, i) => role.classList.toggle("reached", stops[i] <= y + 0.5));
        }
    };
    const schedule = () => {
        if (!queued) { queued = true; requestAnimationFrame(update); }
    };
    timelines.forEach((list) => list.classList.add("tracking"));
    window.addEventListener("scroll", schedule, { passive: true });
    window.addEventListener("resize", schedule);
    update();
})();

// Footer visit count: shown only once the site has had more than 1,000 visits in the past
// year. Uses GoatCounter's public counter, which must be enabled in its site settings
// ("Allow adding visitor counts on your website"); until then nothing is shown.
(function () {
    const footer = document.querySelector(".footer .visits");
    const script = document.querySelector("script[data-goatcounter]");
    if (!footer || !script || !window.fetch) return;
    const THRESHOLD = 1000;
    const base = script.getAttribute("data-goatcounter").replace(/\/count$/, "");

    fetch(`${base}/counter/TOTAL.json?start=year`)
        .then((r) => (r.ok ? r.json() : null))
        .then((data) => {
            // "count" is a formatted string ("1,204" or "1 204"), so keep only the digits.
            const visits = data ? parseInt(String(data.count).replace(/\D/g, ""), 10) : NaN;
            if (!(visits > THRESHOLD)) return;
            footer.textContent = ` · ${visits.toLocaleString("en-US")} visits in the past year`;
            footer.hidden = false;
        })
        .catch(() => { /* counter disabled, blocked or offline: show nothing */ });
})();
