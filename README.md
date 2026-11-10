# chasestrickler.com

Source for [chasestrickler.com](https://chasestrickler.com): plain HTML, CSS and a little JavaScript,
generated at build time from my public resume.

```
src/index.html.j2   page template (Jinja)
src/style.css       styles
src/site.js         theme toggle, sidebar highlight, in-place contact form, timeline progress
                    (all optional; the page works without it)
images/             favicons
build.py            renders the template and the PDF into _site/
```

## Where the content comes from

The resume, the projects list and the PDF all come from `resumes/tailored/public.yml` in my
private `strcklr/resumes` repo, built with [resumake](https://github.com/strcklr/resumake). To change
what the site says, edit that file (or `default.yml`, which it extends), not this repo. The page
layout, the about text, and the tag colors and links (`TAG_COLORS` and `TAG_LINKS` in
`build.py`) live here.

Each project card shows its `status` (`in progress` or `deployed`; `complete` shows nothing, and
without a status a project with no `end` is in progress).

The build refuses a resume that contains a location, email or phone, so a private variant can't be
published by mistake.

## Analytics

A self-hosted [Umami](https://umami.is) instance (cookieless, so no consent banner; Do Not Track is
honoured) counts page views and these events: `resume-pdf` (with `placement`: `sidebar` or
`resume`), `tag` (with the tag's name) and `contact-form-sent`. Only chasestrickler.com is counted,
so local builds aren't. It's shared with the resumake editor (strcklr/resumake#24).

Set in the repo's Actions settings:

| Name | Kind | |
|---|---|---|
| `UMAMI_SRC` | variable | Umami's tracker script, e.g. `https://analytics.chasestrickler.com/script.js` |
| `UMAMI_WEBSITE_ID` | variable | This site's ID in Umami |
| `UMAMI_USERNAME`, `UMAMI_PASSWORD` | secrets | Optional: a view-only Umami user, for the footer count |

Without the two variables the page has no analytics at all. With the login too, the nightly build
asks Umami for the past year's visits and, once there are more than 1,000, writes the count into
the footer (Umami's API needs a login, so it's done at build time rather than in the browser).

GoatCounter counted the site before Umami; its history is in the CSV export from GoatCounter.

## Building locally

```bash
pip install -r requirements.txt
python build.py ../resumes/resumes/tailored/public.yml           # writes _site/
python build.py ../resumes/resumes/tailored/public.yml --no-pdf  # without Pango
python -m http.server -d _site
```

## Deploying

`.github/workflows/static.yml` builds and deploys to GitHub Pages on every push to `main`, nightly,
and on demand. Pull requests build but don't deploy.

It needs one repository secret, `RESUMES_TOKEN`: a fine-grained personal access token with access to
only `strcklr/resumes` and the **Contents: Read-only** permission.
