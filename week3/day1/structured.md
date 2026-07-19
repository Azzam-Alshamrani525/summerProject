# Book Tracker CLI

A simple command-line tool for tracking books you're reading. Practice project for basic CRUD operations and JSON read/write, without a real database.

## Overview

Run the tool and interact with it via prompts (input loop). All data is stored locally in a `books.json` file — no external database needed.

## Features

- Add a book (title, author, pages, genre, status)
- Mark a book as finished
- Rate a book 1–5 stars (only once marked finished)
- List all books
- Filter books by status
- Search by author

### Nice-to-have (not required)
- Sort books by rating
- Export book list to a text file
- Count total pages read across all finished books

## Sample Data

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

## Book Schema

| Field    | Type   | Notes                                                          |
|----------|--------|----------------------------------------------------------------|
| title    | string | Required                                                       |
| author   | string | Required                                                       |
| pages    | number | Required; must be numeric                                      |
| genre    | string | Free text (example: fiction, nonfiction, scifi, biography)     |
| status   | string | Required; must be one of: `want to read`, `reading`, `finished`|
| rating   | number | 1–5, only valid once status is `finished`; otherwise `null`    |


## Validation Rules

- `pages` must be a number
- `rating` must be between 1 and 5
- `status` must be one of the three allowed values — no free text
- `rating` should only be set when `status` is `finished`

## Tech Stack

- **Language:** Python
- **Storage:** Local `books.json` file (no database)
- **Libraries:** Standard library only — `json`, and a simple `input()`-driven menu loop

**Run with:**
```bash
python booktracker.py
```