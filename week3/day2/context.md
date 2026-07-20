# Context Document: Book Tracker CLI

Purpose: give an AI assistant everything it needs to build this project correctly on the first pass, without back-and-forth guessing.

## 1. Task Goal

Build a command-line Python tool to track books being read. Practice project for CRUD operations and JSON read/write — no database.

## 2. Environment

- **OS:** Windows
- **Terminal:** Git Bash (MINGW64)
- **Editor:** VS Code
- **Python:** `pythoncore-3.14-64`
- **Run command:** `python booktracker.py` (not `python3`)
- **Git:** installed and configured; part of a single repo (`summerProject`), root folder `ai agent`, structured as `week3/day2/`
- **Docker:** Docker Desktop installed and must be manually opened/running before any `docker` command works. Once the tool works locally, containerize it with a Dockerfile (standard template: `python:3.12-slim` base, `WORKDIR /app`, copy + install requirements, `ENTRYPOINT ["python"]`). Build with `docker build -t image-name .`; run interactively (needed for `input()`) with `docker run -it -e ... image-name booktracker.py`

## 3. Functional Requirements

- Add a book: title, author, pages, genre, status
- Mark a book as finished
- Rate a book 1–5 stars (only allowed once status is `finished`)
- List all books
- Filter books by status
- Search by author

### Nice-to-have (optional, do only if core works)
- Sort by rating
- Export book list to a text file
- Count total pages read across all finished books

## 4. Data Model

Stored in a local `books.json` file.

```json
{
  "title": "Dune",
  "author": "Frank Herbert",
  "pages": 412,
  "genre": "scifi",
  "status": "finished",
  "rating": 5
}
```

| Field    | Type   | Notes                                                     |
|----------|--------|------------------------------------------------------------|
| title    | string | Required                                                    |
| author   | string | Required                                                    |
| pages    | number | Must be numeric                                             |
| genre    | string | Free text (fiction, nonfiction, scifi, biography, etc.)     |
| status   | string | Must be one of: `want to read`, `reading`, `finished`       |
| rating   | number | 1–5, only valid once `finished`; otherwise `null`           |

## 5. Validation Rules

- `pages` must be numeric — reject non-numeric input
- `rating` must be an integer 1–5
- `status` must be exactly one of the three allowed values — no free text, no typos accepted
- `rating` can only be set when `status` is `finished`

## 6. Constraints

- Python standard library only — `json`, optionally `argparse`; otherwise a simple `input()`-driven menu loop
- No external libraries, no database
- Must run with `python booktracker.py`

## 7. Working Style / Delivery Preferences

- Prefer real iteration (rough version → diagnose issues → improve) over a finished answer handed over immediately
- Code should be ready to copy-paste, not fragmented across many partial snippets
- Keep outputs short and non-truncated
- Agree on spec in plain language before writing code (already done — see Day 1 deliverables)
- Documentation of progress is via terminal screenshots, not automated logging

## 8. Out of Scope

- No database (JSON file only)
- No authentication, multi-user support, or networked storage
- No GUI — command-line only
