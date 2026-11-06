# chasestrickler.com

Source for [chasestrickler.com](https://chasestrickler.com): plain HTML, CSS and a little JavaScript,
generated at build time from my public resume.

```
src/index.html.j2   page template (Jinja)
src/style.css       styles
src/site.js         sidebar highlight + in-place contact form (optional; the page works without it)
images/             favicons
build.py            renders the template and the PDF into _site/
```

## Where the content comes from

The resume, the project spotlight and the PDF all come from `resumes/tailored/public.yml` in my
private `strcklr/resumes` repo, built with [resumake](https://github.com/strcklr/resumake). To change
what the site says, edit that file (or `default.yml`, which it extends), not this repo. The page
layout, the about text and the tag colors live here.

The build refuses a resume that contains a location, email or phone, so a private variant can't be
published by mistake.

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
