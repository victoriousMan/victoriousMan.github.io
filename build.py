#!/usr/bin/env python3
"""Build static site from YAML, Markdown, and optional BibTeX."""

from __future__ import annotations

import re
from datetime import datetime
from pathlib import Path

import bibtexparser
import markdown
import yaml
from bibtexparser.bparser import BibTexParser
from jinja2 import Environment, FileSystemLoader, select_autoescape

ROOT = Path(__file__).parent
DATA = ROOT / "data"
CONTENT = ROOT / "content"
BIB = ROOT / "bib" / "publications.bib"
TEMPLATE_DIR = ROOT / "templates"
OUTPUT = ROOT / "index.html"

PUB_TYPE_MAP = {
    "article": "journal",
    "inproceedings": "conference",
    "incollection": "book chapter",
    "book": "book",
    "phdthesis": "thesis",
    "mastersthesis": "thesis",
    "misc": "preprint",
    "unpublished": "preprint",
}


def load_yaml(path: Path) -> dict | list:
    if not path.exists():
        return {}
    with path.open(encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def load_bio() -> str:
    bio_path = CONTENT / "bio.md"
    if not bio_path.exists():
        return ""
    text = bio_path.read_text(encoding="utf-8")
    return markdown.markdown(text, extensions=["smarty", "nl2br"])


def parse_authors(author_field: str) -> list[str]:
    if not author_field:
        return []
    authors = []
    for part in re.split(r"\s+and\s+", author_field, flags=re.IGNORECASE):
        part = part.strip()
        if not part:
            continue
        if "," in part:
            last, first = part.split(",", 1)
            authors.append(f"{first.strip()} {last.strip()}")
        else:
            authors.append(part)
    return authors


def bib_entry_to_publication(entry: dict) -> dict:
    entry_type = entry.get("ENTRYTYPE", "misc")
    pub_type = PUB_TYPE_MAP.get(entry_type, entry_type)

    venue = (
        entry.get("booktitle")
        or entry.get("journal")
        or entry.get("publisher")
        or ""
    )
    venue = venue.strip("{}")

    links = {}
    if entry.get("url"):
        links["paper"] = entry["url"]
    if entry.get("eprint"):
        links["arxiv"] = f"https://arxiv.org/abs/{entry['eprint']}"
    if entry.get("code"):
        links["code"] = entry["code"]

    arxiv_match = re.search(r"arxiv[:\s]*([\d.]+)", venue, re.IGNORECASE)
    if arxiv_match:
        pub_type = "preprint"
        if "arxiv" not in links:
            links["arxiv"] = f"https://arxiv.org/abs/{arxiv_match.group(1)}"

    note = entry.get("note", "")
    equal = "*" in note or "equal" in note.lower()

    return {
        "type": pub_type,
        "title": entry.get("title", "").strip("{}"),
        "authors": parse_authors(entry.get("author", "")),
        "venue": venue,
        "year": int(entry.get("year", 0) or 0),
        "location": entry.get("address", "").strip("{}"),
        "note": note.replace("*", "").strip() if note else "",
        "equal_contribution": equal,
        "links": links,
        "selected": entry.get("selected", "true").lower() != "false",
    }


def load_publications_from_bib() -> list[dict]:
    if not BIB.exists():
        return []
    text = BIB.read_text(encoding="utf-8").strip()
    if not text or text.startswith("%") and "@" not in text:
        return []

    parser = BibTexParser()
    parser.ignore_nonstandard_types = False
    library = bibtexparser.loads(text, parser=parser)
    pubs = [bib_entry_to_publication(e) for e in library.entries]
    return sorted(pubs, key=lambda p: (p["year"], p["title"]), reverse=True)


def load_publications() -> list[dict]:
    bib_pubs = load_publications_from_bib()
    if bib_pubs:
        return [p for p in bib_pubs if p.get("selected", True)]

    data = load_yaml(DATA / "publications.yml")
    pubs = data.get("publications", []) if isinstance(data, dict) else []
    return sorted(pubs, key=lambda p: (p.get("year", 0), p.get("title", "")), reverse=True)


def group_publications_by_year(publications: list[dict]) -> list[tuple[int, list[dict]]]:
    years: dict[int, list[dict]] = {}
    for pub in publications:
        year = pub.get("year", 0)
        years.setdefault(year, []).append(pub)
    return sorted(years.items(), key=lambda x: x[0], reverse=True)


def normalize_teaching(entries: list[dict]) -> list[dict]:
    normalized = []
    for entry in entries:
        courses = entry.get("courses")
        if not courses and entry.get("course"):
            courses = [entry["course"]]
        normalized.append({**entry, "courses": courses or []})
    return normalized


def build() -> None:
    profile = load_yaml(DATA / "profile.yml")
    awards_data = load_yaml(DATA / "awards.yml")
    experience_data = load_yaml(DATA / "experience.yml")
    teaching_data = load_yaml(DATA / "teaching.yml")

    awards = awards_data.get("awards", []) if isinstance(awards_data, dict) else []
    experience = (
        experience_data.get("experience", [])
        if isinstance(experience_data, dict)
        else []
    )
    teaching = normalize_teaching(
        teaching_data.get("teaching", []) if isinstance(teaching_data, dict) else []
    )

    publications = load_publications()
    pub_by_year = group_publications_by_year(publications)

    env = Environment(
        loader=FileSystemLoader(TEMPLATE_DIR),
        autoescape=select_autoescape(["html", "xml"]),
    )
    template = env.get_template("index.html")

    html = template.render(
        profile=profile,
        bio_html=load_bio(),
        publications=publications,
        publications_by_year=pub_by_year,
        awards=sorted(awards, key=lambda a: a.get("year", 0), reverse=True),
        experience=experience,
        teaching=teaching,
        current_year=datetime.now().year,
    )

    OUTPUT.write_text(html, encoding="utf-8")
    print(f"Built {OUTPUT}")


if __name__ == "__main__":
    build()
