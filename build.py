"""Build chasestrickler.com from a resumake YAML file.

    python build.py path/to/public.yml            # writes _site/
    python build.py path/to/public.yml --no-pdf   # skip the PDF (no Pango needed)

The page is plain HTML rendered at build time from src/index.html.j2, so the
resume content is in the HTML itself (readable without JavaScript and by
crawlers). The PDF is rendered from the same file with resumake.
"""

from __future__ import annotations

import argparse
import datetime as dt
import shutil
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape
from resumake.context import build_context, format_date
from resumake.loader import load_resume

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"
STATIC = ["style.css", "site.js"]
PDF_NAME = "Strickler_Chase_Resume_Public.pdf"  # same name as before, so old links keep working

# Dot color for each tech tag. Anything not listed gets a neutral gray.
TAG_COLORS = {
    "Kotlin": "#7F52FF", "Groovy": "#4298B8", "Java": "#F29111", "Python": "#4B8BBE",
    "Ratpack": "#FDC329", "Spring Boot": "#70AC5F", "WebFlux": "#6DB33F", "Terraform": "#8C5AD6",
    "Spinnaker": "#6495ED", "Jenkins": "#D33833", "AWS": "#FF9900", "DynamoDB": "#5A6FE0",
    "CloudFront": "#B07CF7", "DataDog": "#8E5BD8", "SumoLogic": "#1F6FEB", "Go": "#00ADD8",
    "Dart": "#2B8CC4", "Flutter": "#27B0EE", "AOSP": "#34A853", "C": "#1E90FF", "C++": "#6544D2",
    "Docker": "#2496ED", "Svelte": "#FF3E00", "TypeScript": "#3178C6", "Pyodide": "#9C6ADE",
}
DEFAULT_TAG_COLOR = "#8C8C8C"

# Where each tag links: the project's home page. A tag without an entry is shown as plain text.
TAG_LINKS = {
    "Kotlin": "https://kotlinlang.org/",
    "Groovy": "https://groovy-lang.org/",
    "Java": "https://dev.java/",
    "Python": "https://www.python.org/",
    "Go": "https://go.dev/",
    "C": "https://www.open-std.org/jtc1/sc22/wg14/",  # C has no project site; this is its standards committee
    "C++": "https://isocpp.org/",
    "Dart": "https://dart.dev/",
    "Ratpack": "https://ratpack.io/",
    "Spring Boot": "https://spring.io/projects/spring-boot",
    "WebFlux": "https://spring.io/projects/spring-framework",  # part of Spring Framework, no site of its own
    "Flutter": "https://flutter.dev/",
    "AOSP": "https://source.android.com/",
    "AWS": "https://aws.amazon.com/",
    "DynamoDB": "https://aws.amazon.com/dynamodb/",
    "CloudFront": "https://aws.amazon.com/cloudfront/",
    "Terraform": "https://www.terraform.io/",
    "Spinnaker": "https://spinnaker.io/",
    "Jenkins": "https://www.jenkins.io/",
    "Docker": "https://www.docker.com/",
    "DataDog": "https://www.datadoghq.com/",
    "SumoLogic": "https://www.sumologic.com/",
    "Svelte": "https://svelte.dev/",
    "TypeScript": "https://www.typescriptlang.org/",
    "Pyodide": "https://pyodide.org/",
}


def _month(value) -> dt.date:
    """'2024-08' / '2024-08-15' / 2024 -> first of that month."""
    text = str(value)
    year = int(text[:4])
    month = int(text[5:7]) if len(text) >= 7 else 1
    return dt.date(year, month, 1)


def duration(start, end, today: dt.date) -> str:
    """Months between two dates, inclusive of the start month: '2 yr 3 mo', '6 mo'."""
    first = _month(start)
    last = _month(end) if end else dt.date(today.year, today.month, 1)
    months = max((last.year - first.year) * 12 + last.month - first.month, 1)
    years, months = divmod(months, 12)
    parts = ([f"{years} yr"] if years else []) + ([f"{months} mo"] if months else [])
    return " ".join(parts)


def short_title(position: str) -> str:
    """'Staff Software Engineer — Client API' -> 'Staff Software Engineer'."""
    return position.split(" — ")[0].strip()


def team(position: str) -> str:
    """'Staff Software Engineer — Client API' -> 'Client API'."""
    return position.split(" — ")[1].strip() if " — " in position else ""


def tags(keywords) -> list[dict]:
    return [{"label": k, "color": TAG_COLORS.get(k, DEFAULT_TAG_COLOR), "url": TAG_LINKS.get(k)}
            for k in keywords or []]


def companies(work: list[dict], today: dt.date) -> list[dict]:
    """One entry per company, newest role first, with dates and durations."""
    out = []
    for job in work:
        roles = job.get("roles") or [job]  # single-position entries become one role
        role_views = []
        for i, role in enumerate(roles):
            current = "end" not in role
            role_views.append({
                "title": short_title(role["position"]),
                "start": format_date(role["start"]) if role.get("start") else "",
                "end": format_date(role["end"]) if role.get("end") else "Present",
                "current": current,
                "duration": duration(role["start"], role.get("end"), today) if role.get("start") else "",
                "highlights": [" ".join(h.split()) for h in role.get("highlights", [])],
                "tags": tags(role.get("keywords")),
            })
        starts = [r["start"] for r in roles if r.get("start")]
        ends = [r.get("end") for r in roles]
        first = min(starts, key=_month) if starts else None
        last = None if any(e is None for e in ends) else max(ends, key=_month)
        teams = {team(r["position"]) for r in roles} - {""}
        out.append({
            "company": job["company"],
            "url": job.get("url"),
            "meta": " · ".join([*sorted(teams), *([job["location"]] if job.get("location") else [])]),
            "span": f"{str(first)[:4]} – {str(last)[:4] if last else 'now'}" if first else "",
            "duration": duration(first, last, today) if first else "",
            "roles": role_views,
        })
    return out


def skills(items: list[dict]) -> list[dict]:
    """Each skill group as lines of keywords: a flat list is one line, a list of lists one line each.

    The template keeps each keyword from wrapping ("Spring Boot", "C++", "multi-version"), so lines
    only break between keywords.
    """
    out = []
    for s in items:
        keywords = s.get("keywords", [])
        if any(isinstance(k, list) for k in keywords):
            lines = [k if isinstance(k, list) else [k] for k in keywords]
        else:
            lines = [keywords]
        out.append({"name": s["name"], "lines": lines, "note": s.get("note")})
    return out


def view_model(data: dict, today: dt.date) -> dict:
    projects = [{
        "name": p["name"],
        "url": p.get("url"),
        "summary": (p.get("summary") or "").strip(),
        "in_progress": "end" not in p,
        "tags": tags(p.get("keywords")),
    } for p in data.get("projects", [])]
    profiles = {p["network"].lower(): p["url"] for p in data["basics"].get("profiles", [])}
    return {
        "basics": data["basics"],
        "github": profiles.get("github"),
        "linkedin": profiles.get("linkedin"),
        "projects": projects,
        "companies": companies(data.get("work", []), today),
        "skills": skills(data.get("skills", [])),
        "education": data.get("education", []),
        "pdf": PDF_NAME,
        # Official brand marks, used when their SVGs are in images/ (otherwise generic icons).
        "brand_icons": {name: (ROOT / "images" / f"{name}.svg").is_file() for name in ("github", "linkedin")},
        "year": today.year,
    }


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("resume", type=Path, help="resumake YAML to build from (the public variant)")
    parser.add_argument("-o", "--out", type=Path, default=ROOT / "_site")
    parser.add_argument("--no-pdf", action="store_true", help="skip rendering the PDF")
    args = parser.parse_args(argv)

    data = load_resume(args.resume)
    if data["basics"].get("location") or data["basics"].get("email") or data["basics"].get("phone"):
        raise SystemExit(f"{args.resume}: has a location, email or phone; build from the public variant")

    out = args.out
    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True)

    env = Environment(loader=FileSystemLoader(SRC), autoescape=select_autoescape(["html", "j2"]),
                      trim_blocks=True, lstrip_blocks=True)
    html = env.get_template("index.html.j2").render(**view_model(data, dt.date.today()))
    (out / "index.html").write_text(html, encoding="utf-8")
    for name in STATIC:
        shutil.copy2(SRC / name, out / name)
    shutil.copytree(ROOT / "images", out / "images")

    if not args.no_pdf:
        from resumake.renderers import pdf  # needs Pango; imported only when used
        pdf.render(build_context(data), out / PDF_NAME)

    print(f"built {out}")


if __name__ == "__main__":
    main()
