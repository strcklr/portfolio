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
without a status a project with no `end` is in progress). A project with one link, `url` (the live
site) or `source` (the code), links the whole card to it; one with both shows a button for each.

The build refuses a resume that contains a location, email or phone, so a private variant can't be
published by mistake.

## Analytics

[GoatCounter](https://chasestrickler.goatcounter.com) (cookieless, so no consent banner) counts page views
and these click events: `resume-pdf-sidebar`, `resume-pdf-resume`, `tag-<tag>` and
`contact-form-sent`. The footer shows the past year's visit count once it passes 1,000; that needs
"Allow adding visitor counts on your website" turned on in GoatCounter's site settings.

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
