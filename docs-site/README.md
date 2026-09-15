# NCPlot website

Source for the NCPlot marketing/documentation site (`docs-site/` in the main
ncplot repository). Plain static HTML/CSS/JS — no build step, no dependencies.

## Structure

```
index.html          Landing page
installing.html      \
quickstart.html         Documentation, mirrors docs/source/*.rst in the
api.html                ncplot package, redesigned
about.html           /
version-history.html   Links to archive/vX.Y.Z/ snapshots - see "Archived
                        versions" below
assets/
  css/style.css      Design system (design tokens, components)
  js/main.js         Nav, copy-to-clipboard, scrollspy, version badge
  img/               Logo (ncplot_wordmark.svg), PML logo, favicon
archive/             Per-release snapshots of just index.html + api.html
                      (nav simplified to a single Version history link) +
                      assets/, written by .github/workflows/docs-archive.yml.
                      Don't hand-edit it.
```

## Previewing locally

```sh
cd docs-site
python3 -m http.server 8000
# then open http://localhost:8000
```

## Deploying to GitHub Pages

Deployment is automated by `.github/workflows/pages.yml` (at the repository
root, not under `docs-site/`), which publishes this directory as-is (no build
step) whenever a push to `master` touches `docs-site/**`.

To turn it on:

1. In the repo's **Settings → Pages**, set **Source** to **GitHub Actions**
   (not "Deploy from a branch").
2. Push to `master` (or run the workflow manually from the **Actions** tab —
   it has `workflow_dispatch` enabled). The site publishes to
   `https://pmlmodelling.github.io/ncplot/`.

If the default branch changes, update the `branches:` list in the workflow
file to match.

The included `.nojekyll` file stops GitHub Pages from running its default
Jekyll processing, which isn't needed here and can interfere with files/paths
starting with an underscore.

## Version badge

Every page shows the latest NCPlot release next to the header logo
(`<span id="ncplot-docs-version" class="brand-version">`). It's entirely
client-side: `assets/js/main.js` fetches `https://pypi.org/pypi/ncplot/json`
on page load and fills in the placeholder `v&hellip;` with the current
version. Don't hardcode a version number here — it needs that literal
placeholder text to find and replace.

## Archived versions

`.github/workflows/docs-archive.yml` runs whenever a GitHub Release is
created. It reads the version from `setup.py` (the source of truth - not the
release's tag name, not PyPI, since PyPI's publish can race this workflow),
and copies only `api.html` and `assets/` into `archive/vX.Y.Z/` — the other
pages (`index.html`, `installing.html`, `quickstart.html`, `about.html`)
aren't meaningfully version-specific, and archiving every page of every
release indefinitely doesn't scale. Within the snapshot, the nav on `api.html`
is simplified down to a single "Version history" link, and any link to one of
the un-archived pages (plus `version-history.html` itself, which isn't
version-specific either) is rewritten to point at the live copy instead of
404ing inside the snapshot. It also freezes the header badge in the snapshot
to a plain "vX.Y.Z (archived)" span - it must never update again, unlike the
live badge. It then updates `archive/versions.json` (newest first) and
rewrites the list between the
`<!-- NCPLOT_VERSION_HISTORY_START -->` / `<!-- NCPLOT_VERSION_HISTORY_END -->`
markers in `version-history.html` to match, linking each version straight
to its archived `api.html`. Finally it commits and pushes that to `master`
and explicitly dispatches `pages.yml` (a `GITHUB_TOKEN` push doesn't trigger
other workflows on its own, so this can't just rely on the normal push
trigger).

Existing snapshots are never touched by a later release - only a brand new
`archive/vX.Y.Z/` directory gets created each time. If that directory already
exists (e.g. the workflow re-ran for some reason), it's left alone rather
than overwritten.

`version-history.html` itself is a normal hand-authored page (same header,
nav, and footer as the rest of the site — keep it in sync with the other
pages if you change shared markup) with one auto-generated block in the
middle. Don't hand-edit between its markers; everything else on the page is
yours to edit like any other.

## Updating content

Page content is authored by hand to match the current ncplot docs
(`docs/source/*.rst` and the package README) — there's no templating engine,
so if the underlying package docs change, update the corresponding `.html`
file(s) directly. Shared header/nav/footer markup is duplicated across pages
(no static-site generator), so a nav or footer change should be applied to
all six `.html` files.
