# Book Tracker CLI

A simple command-line tool for tracking books you're reading, built in Python with local JSON storage. No database, no external dependencies.

## Features

- Add a book (title, author, pages, genre, status)
- Mark a book as finished
- Rate a finished book 1–5 stars
- List all books
- Filter books by status (`want to read`, `reading`, `finished`)
- Search books by author

## Requirements

- Python 3.12+ (standard library only — no packages to install)
- Docker (optional, for containerized runs)

## Usage

Run locally:
```bash
python booktracker.py
```

Run via Docker:
```bash
docker build -t booktracker .
docker run -it booktracker booktracker.py
```

Follow the on-screen menu to add, list, filter, search, or rate books.

## Data Storage

Books are stored in a local `books.json` file, created automatically on first run. Each book is stored as:

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

- `status` must be one of: `want to read`, `reading`, `finished`
- `rating` is `null` until `status` is `finished`, then must be an integer 1–5

## Validation

- `pages` must be numeric
- `status` must exactly match one of the three allowed values
- `rating` can only be set on books marked `finished`, and must be 1–5

## Project Docs

- `context.md` — environment and background context for AI-assisted development
- `spec.md` — full functional specification and definition of done

## Out of Scope

- No authentication or multi-user support
- No GUI
- No remote/cloud storage

## Status

Practice project — part of a 7-week AI Engineering training course, Week 3 (Writing .md Files for AI).
