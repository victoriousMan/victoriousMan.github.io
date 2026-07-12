# Personal Website

Academic homepage built from YAML, Markdown, and BibTeX. Styled as a warm, editorial single-page site (distinct from typical colored-tag academic templates).

## Live URL

After deployment, the site will be available at:

- **Primary:** https://victoriousMan.github.io (requires repo named `victoriousMan.github.io` on GitHub account `victoriousMan`)

If you prefer `malghanim07.github.io`, create the repo under the `malghanim07` GitHub account instead and update `data/profile.yml`.

> Note: `malghanim.github.io` / `malghanim07.github.io` are GitHub usernames, not separate custom domains. A true custom domain (e.g. `yourname.com`) needs DNS setup and a `CNAME` file.

## Project structure

```
personal-website/
├── data/           # YAML content (profile, awards, experience, teaching)
├── content/        # Markdown (biography)
├── bib/            # BibTeX source for publications
├── assets/         # profile.jpg
├── files/          # cv.pdf
├── css/            # Stylesheet
├── templates/      # HTML template
├── build.py        # Site generator
└── index.html      # Generated output (commit this OR use GitHub Actions)
```

## Quick start

### 1. Add your files

```bash
cp /path/to/your-photo.jpg assets/profile.jpg
cp /path/to/your-cv.pdf files/cv.pdf
# Paste BibTeX into bib/publications.bib
```

### 2. Edit content

| File | What to edit |
|------|----------------|
| `data/profile.yml` | Name, title, affiliation, email, links |
| `content/bio.md` | Biography (Markdown) |
| `bib/publications.bib` | Publications (BibTeX) |
| `data/awards.yml` | Honors & awards |
| `data/experience.yml` | Work experience |
| `data/teaching.yml` | Teaching roles |

### 3. Build locally

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python build.py
```

Open `index.html` in a browser, or serve locally:

```bash
python -m http.server 8000
# visit http://localhost:8000
```

### 4. Deploy to GitHub Pages

```bash
git init
git add .
git commit -m "Initial personal website"
git remote add origin https://github.com/victoriousMan/victoriousMan.github.io.git
git branch -M main
git push -u origin main
```

Then in the repo: **Settings → Pages → Build and deployment → Source: GitHub Actions**.

The included workflow (`.github/workflows/deploy.yml`) builds and deploys automatically on every push to `main`.

## Publications

Publications are imported from `bib/publications.bib`. They are:

- **Grouped by year** (newest first)
- **Labeled by type** (conference, journal, preprint, etc.) as a subtle left-column prefix — no colored tags

### BibTeX example

```bibtex
@inproceedings{myPaper2025,
  title     = {Paper Title Here},
  author    = {Alghanim, Mansour and Coauthor, Alice},
  booktitle = {International Conference on Example (ICE)},
  year      = {2025},
  address   = {City, Country},
  url       = {https://example.com/paper},
  note      = {Oral}
}
```

Supported entry types map to labels: `inproceedings` → conference, `article` → journal, `misc` → preprint, etc.

Alternatively, edit `data/publications.yml` directly if you prefer not to use BibTeX.

## Adding a new publication

1. Add a BibTeX entry to `bib/publications.bib`
2. Run `python build.py`
3. Commit and push

## Custom domain (optional)

If you own a domain (e.g. `malghanim.com`):

1. Create `CNAME` in the repo root with your domain
2. Configure DNS at your registrar (A/CNAME records per [GitHub docs](https://docs.github.com/en/pages/configuring-a-custom-domain-for-your-github-pages-site))
